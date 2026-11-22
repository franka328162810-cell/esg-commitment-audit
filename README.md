# ESG Commitment Audit

**Find ESG and climate commitments in long reports, trace each one to its source
evidence, and test whether the wording is observable, enforceable, and
revisable.**

[Subscribe — US$29/month](https://icsstudies.gumroad.com/l/esg-commitment-audit)
· [Customer guide](docs/PRODUCT_GUIDE.md)
· [Methodology](docs/METHODOLOGY.md)
· [Limitations](docs/LIMITATIONS.md)

![ESG Commitment Audit cover](assets/esg-commitment-audit-cover.png)

Built for sustainability analysts, boutique ESG consultancies, researchers, and
procurement teams that need a repeatable evidence trail before human review.
The hosted API processes up to 100 documents per month on the Founding Small
Team plan, with a maximum of 100 pages and 50 MB per document.

> This service analyzes written commitment structure. It is not audit assurance,
> legal advice, compliance certification, investment advice, or a finding of
> greenwashing.

## AI Alignment Revisability Audit — development preview

The local package now includes a separate AI-revisability review mode for news
media, advertising, insurance, and industrial-design governance documents. It
checks written authority, revision routes, version history, rollback, affected
party safeguards, monitoring, oversight, and technical-control evidence.

The shared Python distribution is `esg-commitment-audit`. This product's
command is `ai-revisability-audit`.

```powershell
ai-revisability-audit audit examples\revisability_strong_policy.md
ai-revisability-audit compare examples\revisability_policy_v1.md examples\revisability_policy_v2.md
ai-revisability-audit serve
```

Open `http://127.0.0.1:8765/revisability`. This development preview does not
replace the live Recursive Freedom Beta and has not yet been deployed as a
separate paid service. See
[AI Alignment Revisability Audit](docs/AI_ALIGNMENT_REVISABILITY_AUDIT.md) and
[the generated sample report](docs/AI_ALIGNMENT_REVISABILITY_SAMPLE.md) and
[the version-trace sample](docs/AI_ALIGNMENT_REVISABILITY_VERSION_SAMPLE.md).

## Why teams use it

| Review question | What ESG Commitment Audit provides |
|---|---|
| What exactly did the organization promise? | Extracted commitment text and target values |
| Where is the supporting evidence? | Page- or paragraph-level source locations |
| Can progress be measured? | Baseline, target year, scope, method, and reporting checks |
| Who owns delivery? | Named owner, oversight body, and assurance evidence when present |
| Can the commitment be revised? | Review cadence, revision triggers, remedies, and exit terms |
| What is missing? | Explicit missing checks rather than filled-in assumptions |

## Start in three steps

1. **Subscribe** to the Founding Small Team plan on
   [Gumroad](https://icsstudies.gumroad.com/l/esg-commitment-audit).
2. **Activate** the Gumroad license key at the
   [activation page](https://esg-commitment-audit-api.franka328162810.workers.dev/activate).
3. **Run an audit** with the generated API key. The
   [hosted evidence workbench](https://esg-commitment-audit-api.franka328162810.workers.dev/workspace)
   lets you choose a mode and upload a document directly in the browser. The
   [customer guide](docs/PRODUCT_GUIDE.md) also includes ready-to-run `curl`
   commands and troubleshooting steps.

## What is included

- A free local CLI and local web workbench.
- A hosted HTTPS audit API running on Cloudflare.
- Text-layer PDF, DOCX, TXT, and Markdown input.
- Structured JSON reports with commitment-level evidence.
- Recursive Freedom Audit for AI Beta with ten written governance controls.
- A monthly quota of 100 documents on the founding plan.
- A 30-day no-questions-asked full-refund policy on the Gumroad offer.
- Seven-day report retention and tenant-scoped API access.
- A Codex plugin manifest, skill, and local/cloud MCP tools.

## Claims boundary

The audit evaluates written commitment structure. It does not verify emissions
data, decide whether a company is truthful, determine greenwashing, or replace
legal, assurance, or investment due diligence. Missing evidence means the
examined text did not support a check; it does not prove that an underlying
action is absent.

The current rules are strongest for English and Chinese reports. Scanned PDFs
require OCR, which is not included in the current version.

### Recursive Freedom Audit for AI Beta

The same workbench now accepts `X-ESG-Mode: recursive-freedom` and reviews ten
written controls: scope/owner, review cadence, revision process, version
history, advance notice, appeal/human review, refusal/exit, monitoring/audit,
rollback/deprecation, and independent oversight. This Beta analyses AI policy
and governance documents only. It does not assess an individual's personality,
psychology, or rights and must not be used for employment, education, credit,
insurance, immigration, political, or judicial scoring.

The revision-oriented framing is informed by Xue, Z. (2026), *On Recursive
Freedom: A Theory of the Freedom to Revise*, DOI
[10.5281/zenodo.24217876](https://doi.org/10.5281/zenodo.24217876). The
software operationalises only a narrow document-review perspective; the DOI
does not validate the audit results.

The dedicated product page is:

```text
https://esg-commitment-audit-api.franka328162810.workers.dev/recursive-freedom
```

Public sample report:

```text
https://esg-commitment-audit-api.franka328162810.workers.dev/recursive-freedom/sample
```

See [Recursive Freedom Audit for AI](docs/RECURSIVE_FREEDOM_AUDIT.md) for the
product scope, v0.2 benchmark result, interpretation rules, and development
boundary.

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

- Founding plan: https://icsstudies.gumroad.com/l/esg-commitment-audit
- API-key activation: https://esg-commitment-audit-api.franka328162810.workers.dev/activate
- Evidence workbench: https://esg-commitment-audit-api.franka328162810.workers.dev/workspace
- Recursive Freedom Audit for AI: https://esg-commitment-audit-api.franka328162810.workers.dev/recursive-freedom
- Recursive Freedom public sample: https://esg-commitment-audit-api.franka328162810.workers.dev/recursive-freedom/sample
- Public landing page: https://esg-commitment-audit-api.franka328162810.workers.dev/
- Health check: https://esg-commitment-audit-api.franka328162810.workers.dev/v1/health
- Privacy draft: https://esg-commitment-audit-api.franka328162810.workers.dev/privacy
- Terms draft: https://esg-commitment-audit-api.franka328162810.workers.dev/terms

The hosted API and Gumroad founding offer are live. Stripe checkout code is
deployed but is not the current production checkout route. A verified and
unused Gumroad license key can be exchanged once at `/activate` for a
founding-team organization and API key. Gumroad membership status is rechecked
every 15 minutes. The legal pages state the service boundary but have not
received professional legal review.

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
esg-commitment-audit audit examples\strong_commitment.txt
esg-commitment-audit audit examples\strong_commitment.txt --format html --output audit-output\strong.html
esg-commitment-audit serve
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
GET    /activate
POST   /v1/billing/gumroad/redeem
POST   /v1/billing/checkout
POST   /v1/billing/stripe-webhook
POST   /v1/billing/webhook
```

Raw uploads are deleted after success or final failure. Reports expire after
seven days, job metadata after 180 days, and an R2 lifecycle rule deletes any
remaining `orgs/` objects after 30 days.

The founding plan permits one organization, one shared API key, 100 audited
documents per month, and at most 100 pages and 50 MB per document. The Gumroad
listing is capped at 20 active founding supporters. Scanned PDFs without a text
layer are rejected because OCR is not included.

`POST /v1/audits` accepts `X-ESG-Mode: commitment` for ESG/climate reports or
`X-ESG-Mode: recursive-freedom` for Recursive Freedom Audit for AI. Both modes use the same
monthly allowance and the same page and file-size limits.

An owner-only Gumroad test purchase passed on 2026-11-22 without a charge. Its
license authenticated, activated a `founding-team` organization, and produced a
100-document quota. The test organization is recorded with `active` Gumroad
billing status.

Deployment, backup, monitoring, cost, and recovery notes are in
[`docs/COMMERCIAL_DEPLOYMENT.md`](docs/COMMERCIAL_DEPLOYMENT.md).

### Local commercial server

Create an organization and a one-time API key:

```powershell
$env:ESG_SERVICE_DATA_DIR = "C:\ics-service-data"
$env:ESG_BILLING_WEBHOOK_SECRET = "replace-with-a-long-random-secret"

esg-commitment-audit-admin create-org --name "Example Corp" --plan starter
esg-commitment-audit-admin issue-key --organization-id org_... --name production
esg-commitment-audit-workbench serve-commercial --host 127.0.0.1 --port 8766
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
`ESG_REPORT_RETENTION_DAYS`.

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
skills/esg-commitment-audit/SKILL.md
plugin/.codex-plugin/plugin.json
plugin/.mcp.json
plugin/server.mjs
.agents/plugins/marketplace.json
```

Install the hosted plugin from the repository marketplace:

```powershell
codex plugin marketplace add franka328162810-cell/esg-commitment-audit --ref main
codex plugin add esg-commitment-audit@ics-tec
```

Configure `ESG_AUDIT_API_KEY` before using hosted tools. The marketplace bundle
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
python -m esg_commitment_audit audit examples\vague_statement.txt
```

## License

Code and rules are licensed under Apache License 2.0. Future formalizations under
`formalizations/` are intended to be licensed separately under CC BY-SA 4.0; no
formal proof is included in v0.3.1.

Copyright 2026 Xue Zhi Xin (ICS-TEC).
