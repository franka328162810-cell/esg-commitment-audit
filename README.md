# ICS Commitment Audit Workbench

**Evidence-first ESG / climate commitment structure auditor — v0.2.0**

This project extracts written commitments and tests whether their structure is
observable, enforceable, and revisable under the ICS CRV framework. It does not
decide whether a company is truthful, greenwashing, compliant, assured, or
performing well.

Version 0.2.0 includes:

- a free local CLI and local web workbench;
- tenant-isolated commercial API foundations;
- API-key authentication, monthly document quotas, persistent audit jobs, and
  tenant-scoped report retrieval;
- a provider-neutral billing webhook for subscription activation/update/cancel;
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

The repository root is also a Codex plugin:

```text
.codex-plugin/plugin.json
.mcp.json
skills/ics-commitment-audit/SKILL.md
```

After installing this Python package, enable the repository as a local plugin or
publish it through a Codex plugin marketplace. The MCP server provides:

- `audit_local_document`
- `audit_text`
- `submit_cloud_audit`
- `get_cloud_audit`

Local audit is the default. Hosted tools require both `ICS_AUDIT_API_URL` and
`ICS_AUDIT_API_KEY`; cloud submission is approval-gated in `.mcp.json`.

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
