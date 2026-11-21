param(
  [Parameter(Mandatory = $true)]
  [string] $OciArchive,

  [Parameter(Mandatory = $true)]
  [string] $Repository,

  [Parameter(Mandatory = $true)]
  [string] $Tag,

  [string] $Registry = "registry.cloudflare.com",
  [string] $CredentialServer = "registry.cloudflare.com",
  [string] $CredentialHelper = "G:\Docker\DockerDesktop\resources\bin\docker-credential-desktop.exe",
  [int] $ChunkSize = 1048576,
  [int] $MaxRetries = 12
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

if (-not (Test-Path -LiteralPath $OciArchive)) {
  throw "OCI archive not found: $OciArchive"
}
if ($env:ICS_REGISTRY_CREDENTIALS) {
  $credential = $env:ICS_REGISTRY_CREDENTIALS | ConvertFrom-Json
  $registryUsername = [string] $credential.username
  $registryPassword = [string] $credential.password
}
else {
  if (-not (Test-Path -LiteralPath $CredentialHelper)) {
    throw "Docker credential helper not found: $CredentialHelper"
  }
  $credentialJson = $CredentialServer | & $CredentialHelper get
  if ($LASTEXITCODE -ne 0) {
    throw "Docker credential helper could not return registry credentials."
  }
  $credential = $credentialJson | ConvertFrom-Json
  $registryUsername = [string] $credential.Username
  $registryPassword = [string] $credential.Secret
}

$basicToken = [Convert]::ToBase64String(
  [Text.Encoding]::UTF8.GetBytes("${registryUsername}:${registryPassword}")
)
Write-Verbose (
  "Registry user '$registryUsername', password length " +
  "$($registryPassword.Length), token length $($basicToken.Length)."
)
$registryBase = [Uri] "https://$Registry"
$registryRoot = $registryBase.AbsoluteUri.TrimEnd("/")
$repositoryRoot = "$registryRoot/v2/$Repository"

$extractRoot = Join-Path $PWD ".wrangler\oci-image-$Tag"
if (Test-Path -LiteralPath $extractRoot) {
  Remove-Item -LiteralPath $extractRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $extractRoot -Force | Out-Null
& tar.exe -xf $OciArchive -C $extractRoot
if ($LASTEXITCODE -ne 0) {
  throw "Could not extract the OCI archive."
}

$indexPath = Join-Path $extractRoot "index.json"
$index = Get-Content -LiteralPath $indexPath -Raw | ConvertFrom-Json
if (-not $index.manifests -or $index.manifests.Count -eq 0) {
  throw "The OCI index does not contain an image manifest."
}
$manifestDescriptor = $index.manifests[0]
$manifestDigest = [string] $manifestDescriptor.digest
$manifestPath = Join-Path $extractRoot (
  "blobs\sha256\" + $manifestDigest.Substring("sha256:".Length)
)
$manifestBytes = [IO.File]::ReadAllBytes($manifestPath)
$manifest = [Text.Encoding]::UTF8.GetString($manifestBytes) | ConvertFrom-Json

function Resolve-RegistryUri([Uri] $Location) {
  if ($Location.IsAbsoluteUri) {
    return $Location
  }
  return [Uri]::new($registryBase, $Location.ToString())
}

function Invoke-RegistryRequest(
  [string] $Method,
  [Uri] $Uri,
  [byte[]] $Body = $null,
  [string] $ContentType = "application/octet-stream",
  [hashtable] $ExtraHeaders = @{},
  [switch] $NoRetry
) {
  $headers = @{
    Authorization = "Basic $basicToken"
  }
  foreach ($key in $ExtraHeaders.Keys) {
    $headers[$key] = $ExtraHeaders[$key]
  }
  $parameters = @{
    Uri = $Uri
    Method = $Method
    Headers = $headers
    SkipHttpErrorCheck = $true
    SkipHeaderValidation = $true
    MaximumRedirection = 0
    TimeoutSec = 180
  }
  if ($null -ne $Body) {
    $parameters.Body = $Body
    $parameters.ContentType = $ContentType
  }
  $lastError = $null
  $attempts = if ($NoRetry) { 1 } else { $MaxRetries }
  for ($attempt = 1; $attempt -le $attempts; $attempt++) {
    try {
      return Invoke-WebRequest @parameters
    }
    catch {
      $lastError = $_
      if ($attempt -ge $attempts) {
        break
      }
      Write-Host "Registry request retry $attempt/$attempts."
      Start-Sleep -Seconds ([Math]::Min(10, $attempt))
    }
  }
  throw $lastError
}

function Test-Blob([string] $Digest) {
  $uri = [Uri] "$repositoryRoot/blobs/$Digest"
  $response = Invoke-RegistryRequest "HEAD" $uri
  if ([int] $response.StatusCode -eq 200) {
    return $true
  }
  if ([int] $response.StatusCode -eq 404) {
    return $false
  }
  throw "Blob check failed ($([int] $response.StatusCode)): $($response.Content)"
}

function Start-BlobUpload {
  $response = Invoke-RegistryRequest "POST" ([Uri] "$repositoryRoot/blobs/uploads/")
  if ([int] $response.StatusCode -ne 202) {
    throw (
      "Blob upload could not start ($([int] $response.StatusCode)): " +
      $response.Content
    )
  }
  $location = $response.Headers.Location | Select-Object -First 1
  return Resolve-RegistryUri ([Uri] $location)
}

function Get-UploadOffset([Uri] $UploadUri) {
  $response = Invoke-RegistryRequest "GET" $UploadUri
  $range = $response.Headers.Range | Select-Object -First 1
  if (-not $range) {
    return $null
  }
  $last = [int64] (($range -split "-")[-1])
  return $last + 1
}

function Push-Blob([string] $Digest, [string] $BlobPath) {
  if (Test-Blob $Digest) {
    Write-Host "Blob $($Digest.Substring(7, 12)) already exists."
    return
  }

  $bytes = [IO.File]::ReadAllBytes($BlobPath)
  $uploadUri = Start-BlobUpload
  $offset = [int64] 0
  $failures = 0
  $nextChunkSize = [int64] $ChunkSize

  while ($offset -lt $bytes.LongLength) {
    $end = [Math]::Min($offset + $nextChunkSize, $bytes.LongLength) - 1
    $chunkLength = [int] ($end - $offset + 1)
    $chunk = [byte[]]::new($chunkLength)
    [Array]::Copy($bytes, $offset, $chunk, 0, $chunkLength)

    try {
      $response = Invoke-RegistryRequest `
        "PATCH" `
        $uploadUri `
        $chunk `
        "application/octet-stream" `
        @{ "Content-Range" = "$offset-$end" } `
        -NoRetry
      $status = [int] $response.StatusCode
      $nextLocation = $response.Headers.Location | Select-Object -First 1
      if ($status -notin @(202, 204)) {
        throw "Chunk upload failed with HTTP $status`: $($response.Content)"
      }
      if ($nextLocation) {
        $uploadUri = Resolve-RegistryUri ([Uri] $nextLocation)
      }
      $offset = $end + 1
      $nextChunkSize = [Math]::Min($nextChunkSize * 2, 16MB)
      $failures = 0
      Write-Progress -Activity "Uploading $Digest" -PercentComplete (
        (100 * $offset) / $bytes.LongLength
      )
    }
    catch {
      $failures++
      Write-Host "Chunk attempt $failures at byte $offset failed: $($_.Exception.Message)"
      if ($failures -gt $MaxRetries) {
        throw "Blob upload exceeded $MaxRetries retries at byte $offset."
      }
      Start-Sleep -Seconds ([Math]::Min(10, $failures))
      try {
        $knownOffset = Get-UploadOffset $uploadUri
      }
      catch {
        $knownOffset = $null
      }
      if ($null -ne $knownOffset) {
        $offset = [int64] $knownOffset
      }
      else {
        $uploadUri = Start-BlobUpload
        $offset = 0
        $nextChunkSize = [int64] $ChunkSize
      }
    }
  }

  Write-Progress -Activity "Uploading $Digest" -Completed
  $separator = if ($uploadUri.Query) { "&" } else { "?" }
  $finishUri = [Uri] (
    "$uploadUri$separator" + "digest=" + [Uri]::EscapeDataString($Digest)
  )
  $response = Invoke-RegistryRequest "PUT" $finishUri ([byte[]] @())
  $status = [int] $response.StatusCode
  if ($status -notin @(201, 204)) {
    throw "Blob finalization failed ($status): $($response.Content)"
  }
  if (-not (Test-Blob $Digest)) {
    throw "Registry did not retain finalized blob $Digest."
  }
  Write-Host "Blob $($Digest.Substring(7, 12)) uploaded."
}

$blobRoot = Join-Path $extractRoot "blobs\sha256"
$descriptors = @($manifest.config) + @($manifest.layers)
foreach ($descriptor in $descriptors) {
  $digest = [string] $descriptor.digest
  $blobPath = Join-Path $blobRoot ($digest.Substring("sha256:".Length))
  Push-Blob $digest $blobPath
}

$manifestUri = [Uri] "$repositoryRoot/manifests/$Tag"
$contentType = [string] $manifestDescriptor.mediaType
if (-not $contentType) {
  $contentType = "application/vnd.oci.image.manifest.v1+json"
}
$response = Invoke-RegistryRequest "PUT" $manifestUri $manifestBytes $contentType
$status = [int] $response.StatusCode
if ($status -notin @(201, 202, 204)) {
  throw "Manifest upload failed ($status): $($response.Content)"
}

$verify = Invoke-RegistryRequest "HEAD" $manifestUri
if ([int] $verify.StatusCode -ne 200) {
  throw "Manifest verification failed ($([int] $verify.StatusCode))."
}

Write-Host "Published: $Registry/$Repository`:$Tag"
