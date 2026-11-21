# ICS Commitment Audit Workbench

**Evidence-first ESG / climate commitment structure auditor — v0.2.0**

This project extracts written commitments and tests whether their structure is
observable, enforceable, and revisable under the ICS CRV framework. It does not
decide whether a company is truthful, greenwashing, compliant, assured, or
performing well.

Version 0.2.0 includes:

- a free local CLI and local web workbench;
- a deployed HTTPS pilot API on Cloudflare Workers, D1, R2, Queues, and
  Containers;
- API-key authentication, monthly document quotas, persistent audit jobs, and
  tenant-scoped report retrieval;
- provider-neutral billing webhooks and a Stripe Checkout Session endpoint;
- a Codex plugin manifest, skill, and local/cloud MCP tools.

## What the audit does

- Reads text-layer PDF, DOCX, TXT, and Markdown files.
- Reconstructs multi-column PDF pages and target/progress table roles.
- Detects Chinese and English ESG or climate commitment statements.
- Extracts target values, baseline years, target years, scopes, owners,
  assurance, reporting, remedies, review mechanisms, and evidence spans.
- Scores `V_obs`, `V_enf`, and `V_rev`, using default weights:

```text
V_obs 0.35 + V_enf 0.35 + V_rev 0.30
```

- Produces Markdown, JSON, and standalone HTML reports with page/paragraph
  evidence.

## Validation status

The commercial gate passed on the frozen 2026-11-21 review:

| Metric | Result | Gate |
|---|---:|---:|
| Candidate precision | 98.63% | ≥80% |
| Unique commitment recall | 93.75% | ≥85% |
| E/S/G top-level accuracy | 100% | ≥90% |
| Page citation coverage | 100% | 100% |
| Manual unique commitments | 80 | 80–100 |
| Duplicate candidates | 0 | 0 |

The review covers Microsoft, Apple, CATL, and Luxshare official public reports.
It is a single-reviewer Codex adjudication under written rules; the author
waived an independent second human reviewer. The waiver does not convert the
review into independent validation.

## Live pilot

- Public landing page: https://ics-commitment-audit-api.franka328162810.workers.dev/
- Health check: https://ics-commitment-audit-api.franka328162810.workers.dev/v1/health
- Privacy draft: https://ics-commitment-audit-api.franka328162810.workers.dev/privacy
- Terms draft: https://ics-commitment-audit-api.franka328162810.workers.dev/terms

The hosted API is operational for controlled pilots. Stripe checkout code is
deployed but returns `503` until a Stripe merchant account, secret key, webhook
secret, and Starter/Pro Price IDs are configured. The legal pages remain drafts
and require review before charging customers.

Reproduce the calculation:

```powershell
python validation\check_gate.py
```

Review data:

- `docs/REAL_REPORT_VALIDATION_V020_2026-11-21.md`
- `validation/real_report_review_v011_gate_2026-11-21.json`
- `validation/check_gate.py`

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

## Free local use

```powershell
ics-crv audit examples\strong_commitment.txt
ics-crv audit examples\strong_commitment.txt --format html --output audit-output\strong.html
ics-crv serve
```

The local server binds to `127.0.0.1` by default and does not upload documents.

## Commercial API

### Hosted Cloudflare pilot

The hosted control plane uses D1 for organizations and jobs, R2 for private
uploads/reports, Queues for asynchronous work, and one Durable Object container
per audit. All customer records are tenant-scoped.

```text
POST   /v1/audits
GET    /v1/audits/{job_id}
GET    /v1/audits/{job_id}/report
DELETE /v1/audits/{job_id}
GET    /v1/account
POST   /v1/billing/checkout
POST   /v1/billing/stripe-webhook
POST   /v1/billing/webhook
```

Raw uploads are deleted after success or final failure. Reports expire after
seven days, job metadata after 180 days, and an R2 lifecycle rule deletes any
remaining `orgs/` objects after 30 days.

Deployment, backup, monitoring, cost, and recovery notes are in
[`docs/COMMERCIAL_DEPLOYMENT.md`](docs/COMMERCIAL_DEPLOYMENT.md).

### Local commercial server

Create an organization and a one-time API key:

```powershell
$env:ICS_SERVICE_DATA_DIR = "C:\ics-service-data"
$env:ICS_BILLING_WEBHOOK_SECRET = "replace-with-a-long-random-secret"

ics-crv-admin create-org --name "Example Corp" --plan starter
ics-crv-admin issue-key --organization-id org_... --name production
ics-crv serve-commercial --host 127.0.0.1 --port 8766
```

Then use:

```text
POST   /v1/audits
GET    /v1/audits/{job_id}
GET    /v1/audits/{job_id}/report
DELETE /v1/audits/{job_id}
GET    /v1/account
POST   /v1/billing/webhook
```

Authentication uses `Authorization: Bearer <API key>`. Only a SHA-256 hash of
each key is stored. Uploads and reports are isolated by organization, input
files are deleted after processing, and completed reports expire according to
`ICS_REPORT_RETENTION_DAYS`.

The API accepts signed subscription events through a provider-neutral webhook
and provides native Stripe signature verification. Actual charging still
requires a merchant account, price configuration, HTTPS deployment, and
tax/refund policy. See
[`docs/COMMERCIAL_DEPLOYMENT.md`](docs/COMMERCIAL_DEPLOYMENT.md).

## Codex plugin

The repository includes both a development plugin at the root and a
dependency-free marketplace bundle in `plugin/`.

```text
.codex-plugin/plugin.json
.mcp.json
skills/ics-commitment-audit/SKILL.md
plugin/.codex-plugin/plugin.json
plugin/.mcp.json
plugin/server.mjs
.agents/plugins/marketplace.json
```

Install the hosted plugin from the repository marketplace:

```powershell
codex plugin marketplace add franka328162810-cell/ics-commitment-audit --ref main
codex plugin add ics-commitment-audit@ics-tec
```

Configure `ICS_AUDIT_API_KEY` before using hosted tools. The marketplace bundle
uses a dependency-free Node MCP client and requires network access to the ICS
HTTPS API. It provides:

- `audit_document`
- `audit_text`
- `get_cloud_audit`
- `get_account`
- `delete_cloud_audit`

The root development plugin additionally exposes local Python audit tools. Local
audit remains free and on-device when the Python package is installed. Hosted
uploads and deletion are approval-gated in `.mcp.json`.

## Report interpretation

The score measures commitment structure completeness, not environmental
performance or the truth of the undertaking. Every automated finding must carry
source evidence. A missing check means no supporting text was found in the
examined scope, not that the underlying action is absent.

See:

- `docs/METHODOLOGY.md`
- `docs/LIMITATIONS.md`
- `docs/RULE_PROVENANCE.md`
- `docs/BUSINESS_MODELS.md`

## Development

```powershell
python -m pytest
python -m ruff check src tests validation
python -m ics_commitment_audit audit examples\vague_statement.txt
```

## License

Code and rules are licensed under Apache License 2.0. Future formalizations under
`formalizations/` are intended to be licensed separately under CC BY-SA 4.0; no
formal proof is included in v0.2.0.

Copyright 2026 Xue Zhi Xin (ICS-TEC).
