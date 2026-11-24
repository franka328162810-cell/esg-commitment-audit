# Cross-client distribution

Version: `0.6.2`

Public description: **ICS Audit Tools for MCP-compatible AI agents**

## Architecture

```text
ICS hosted API
  ├─ local stdio MCP core
  │   ├─ Codex AI plugin
  │   ├─ Codex ESG plugin
  │   ├─ Claude Code adapters
  │   ├─ Hermes template
  │   ├─ WorkBuddy template
  │   └─ generic MCP template
  └─ remote Streamable HTTP MCP
      ├─ /mcp/ai
      └─ /mcp/esg
```

The product names remain host-neutral:

- `AI Alignment Revisability Audit`
- `ESG Commitment Audit`

The technical package identifiers remain stable:

- `ai-alignment-revisability-audit`
- `esg-commitment-audit`

## Support matrix

| Client | Transport | Status |
|---|---|---|
| Codex CLI/desktop | stdio | Supported and tested |
| Claude Code | stdio | Supported and tested |
| Codex CLI | Streamable HTTP | Configuration accepted; direct protocol tested |
| Claude Code | Streamable HTTP | Not verified because the local Claude account is not logged in |
| Generic MCP client | Streamable HTTP | Direct JSON-RPC initialize, tools/list and production tool calls tested |
| Generic MCP client | stdio | Protocol-compatible; client-specific test required |
| Hermes | stdio or HTTP | Template only; not yet verified |
| WorkBuddy | stdio or HTTP | Template only; not yet verified |

Only clients marked supported may appear in external compatibility claims.

## Claude Code

From the repository root:

```powershell
$env:ICS_AUDIT_API_KEY = "<matching API key>"
claude --mcp-config adapters/claude-code/.mcp.json --strict-mcp-config
```

Remote HTTP configuration:

```powershell
$env:ICS_AUDIT_API_KEY = "<matching API key>"
claude --mcp-config adapters/claude-code/remote-mcp.json --strict-mcp-config
```

Direct CLI registration:

```powershell
claude mcp add --transport http ics-esg-remote `
  https://esg-commitment-audit-mcp.franka328162810.workers.dev/mcp/esg `
  --header "Authorization: Bearer $env:ICS_AUDIT_API_KEY"

claude mcp add --transport http ics-ai-remote `
  https://esg-commitment-audit-mcp.franka328162810.workers.dev/mcp/ai `
  --header "Authorization: Bearer $env:ICS_AUDIT_API_KEY"
```

Use `claude mcp list` and `claude mcp get <name>` to inspect registration and
health.

## Remote MCP limits

Streamable HTTP sends document bytes inside base64 JSON. To stay below the
Cloudflare request-body ceiling:

- policy documents: 50 MB decoded;
- evidence-pack ZIPs: 70 MB decoded;
- local stdio MCP retains the full 100 MB ZIP limit.

Larger evidence packs must use the local stdio adapter or the REST upload
endpoint. The client-visible limits must not be described as identical.

## Hermes and WorkBuddy

Templates:

```text
adapters/hermes/mcp.json
adapters/workbuddy/mcp.json
```

The template keys and transport names must be checked against the installed
client version. A syntactically plausible JSON file is not evidence of support.
The client must complete:

1. initialize;
2. tools/list;
3. `get_purchase_options`;
4. `get_account`;
5. one document review;
6. one evidence-pack review for AI;
7. report retrieval;
8. deletion;
9. wrong-product key rejection;
10. upgrade and uninstall.

Only then may its row be changed to Supported.

## Authentication

- All remote MCP calls require `Authorization: Bearer <ICS API key>`.
- The remote gateway does not store the key.
- Each remote endpoint exposes one product only.
- Account preflight runs before uploads.
- Wrong-product or inactive keys stop before document transfer.
- Secrets must be supplied by environment variable or client secret storage.

## Remote MCP testing

Initialize:

```powershell
$body = @{
  jsonrpc = "2.0"
  id = 1
  method = "initialize"
  params = @{
    protocolVersion = "2025-06-18"
    clientInfo = @{ name = "manual-test"; version = "1.0.0" }
  }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod `
  -Method Post `
  -Uri "https://esg-commitment-audit-mcp.franka328162810.workers.dev/mcp/ai" `
  -Headers @{ Authorization = "Bearer $env:ICS_AUDIT_API_KEY" } `
  -ContentType "application/json" `
  -Body $body
```

The same test must be repeated with `tools/list`, `get_purchase_options`,
`get_account`, `audit_text`, status retrieval and deletion.

The production endpoint was additionally checked with
`Accept: application/json, text/event-stream` and returned a valid
`event: message` SSE frame.

## Release rule

A client-specific adapter is not a release blocker for the two verified clients
when its absence is explicit. It becomes a release blocker when the public
support matrix claims that client.

The stable public wording is:

> ICS Audit Tools for MCP-compatible AI agents. Verified with Codex and Claude
> Code through local MCP. The remote Streamable HTTP service is protocol-tested;
> Hermes and WorkBuddy adapters remain unverified templates until
> client-specific lifecycle testing is completed.
