# AI Revisability Evidence-Pack Workflow

The evidence pack connects a written AI-governance document to dated operating
records. It is a verification and escalation workflow, not a safety
certification.

## What it establishes

| Grade | Minimum interpretation |
|---|---|
| `absent` | The examined policy text did not support the control |
| `asserted` | The policy makes a general claim or aspiration |
| `documented` | The policy states a specific written control |
| `operationally_evidenced` | A compatible, dated, issuer-identified, hash-matched artifact supports operation |
| `independently_verified` | A hash-matched independent review with an independent issuer supports the control |

An evidence pack can propose E2, E3, or E4. It cannot approve E3 or E4
automatically. Every promotion carries `requires_human_confirmation: true`.

A matching file hash proves only that the file did not change after sealing. It
does not prove that the event occurred, that the signer had authority, or that
the review was adequate.

## 1. Prepare the manifest

Create a directory with the base policy and evidence files:

```text
evidence/
  manifest.yaml
  policy.md
  approval-record.txt
  rollback-drill.txt
  monitoring-snapshot.json
  independent-review.txt
```

Example:

```yaml
manifest_version: "1.0"
organization: Example AI Company
reviewed_at: 2026-11-23
profile: general
base_document: policy.md

artifacts:
  - path: approval-record.txt
    artifact_type: approval_record
    issued_at: 2026-11-20
    issuer: AI Governance Board
    supports:
      - revision_authority

  - path: rollback-drill.txt
    artifact_type: rollback_drill
    issued_at: 2026-11-18
    issuer: Incident Response Team
    supports:
      - rollback_evidence

  - path: independent-review.txt
    artifact_type: independent_review
    issued_at: 2026-11-21
    issuer: Independent AI Review Panel
    independent: true
    supports:
      - independent_oversight
```

## 2. Seal SHA-256 hashes

```powershell
ai-revisability-audit evidence-pack-seal evidence\manifest.yaml `
  --output evidence\manifest.sealed.yaml
```

Sealing writes a new manifest and refuses to overwrite the editable source.
Do not edit evidence files after sealing; generate a new sealed manifest
instead.

## 3. Validate a manifest or ZIP

Manifest directory:

```powershell
ai-revisability-audit evidence-pack evidence\manifest.sealed.yaml `
  --format html --output evidence\report.html
```

ZIP:

```powershell
ai-revisability-audit evidence-pack evidence-pack.zip `
  --format json --output evidence\report.json
```

The ZIP must contain exactly one `manifest.yaml`, `manifest.yml`, or
`manifest.json`.

## 4. Local web workflow

```powershell
ai-revisability-audit serve
```

Open `http://127.0.0.1:8765/revisability/evidence` and upload a ZIP. The local
service removes the temporary upload after processing.

## Security controls

- Maximum 50 MB per file.
- Maximum 200 MB total uncompressed content.
- Maximum 1,000 ZIP entries.
- SHA-256 pinning for every artifact.
- Path traversal and absolute paths rejected.
- Symbolic links and encrypted ZIP entries rejected.
- Unusually high ZIP compression ratios rejected.
- Artifact type must be compatible with the control it supports.
- A missing date, issuer, hash, or compatible type prevents E3 eligibility.

## Codex and MCP

The local MCP server exposes `audit_evidence_pack` and accepts an absolute path
to a sealed manifest or ZIP. The tool returns the same JSON structure as the
CLI.

## Claim boundary

Do not describe an evidence-pack proposal as an audit opinion, legal conclusion,
model-alignment proof, or certification. A reviewer must inspect the underlying
artifact, the issuer's authority, the sampling method, and unresolved counterevidence.
