# ESG Commitment Audit

**Find ESG and climate commitments in long reports, trace each one to its source
evidence, and test whether the wording is observable, enforceable, and
revisable.**

[Subscribe — US$29/month](https://icsstudies.gumroad.com/l/esg-commitment-audit)
· [Customer guide](docs/PRODUCT_GUIDE.md)
· [Methodology](docs/METHODOLOGY.md)
· [Limitations](docs/LIMITATIONS.md)

![ESG Commitment Audit cover](assets/esg-commitment-audit-cover.png)

Current release: [`v0.6.1`](docs/RELEASE_CHECK_V061.md) —
[release notes](docs/PLUGIN_RELEASE_NOTES_V061.md).

Built for sustainability analysts, boutique ESG consultancies, researchers, and
procurement teams that need a repeatable evidence trail before human review.
The hosted API processes up to 100 documents per month on the Founding Small
Team plan, with a maximum of 100 pages and 50 MB per document.

> This service analyzes written commitment structure. It is not audit assurance,
> legal advice, compliance certification, investment advice, or a finding of
> greenwashing.

## AI Alignment Revisability Audit — founding release

The local package includes a separate AI-revisability review mode for news
media, advertising, insurance, and industrial-design governance documents. It
checks written authority, revision routes, version history, rollback, affected
party safeguards, monitoring, oversight, and technical-control evidence.

The shared Python distribution is `esg-commitment-audit`. This product's
command is `ai-revisability-audit`.

```powershell
ai-revisability-audit audit examples\revisability_strong_policy.md
ai-revisability-audit compare examples\revisability_policy_v1.md examples\revisability_policy_v2.md
ai-revisability-audit evidence-pack-seal examples\evidence-pack\manifest.yaml --output examples\evidence-pack\manifest.sealed.yaml
ai-revisability-audit evidence-pack examples\evidence-pack\manifest.sealed.yaml --format html --output audit-output\evidence-pack.html
ai-revisability-audit benchmark benchmarks\ai_revisability_2026_11_23\dataset.yaml --sources C:\path\to\frozen-sources --strict
ai-revisability-audit serve
```

Open `http://127.0.0.1:8765/revisability` or
`http://127.0.0.1:8765/revisability/evidence`. The hosted product is
available at:

```text
https://esg-commitment-audit-api.franka328162810.workers.dev/ai-revisability-audit
https://esg-commitment-audit-api.franka328162810.workers.dev/workspace
```

It is sold separately at **US$99/month** to the first 20 customer
organizations, with 100 policy or evidence-pack jobs per month, one shared API
key, and a 30-day no-questions-asked full refund:

```text
https://icsstudies.gumroad.com/l/ai-alignment-revisability-audit
https://esg-commitment-audit-api.franka328162810.workers.dev/ai-revisability-audit/activate
```

See
[AI Alignment Revisability Audit](docs/AI_ALIGNMENT_REVISABILITY_AUDIT.md) and
[the generated sample report](docs/AI_ALIGNMENT_REVISABILITY_SAMPLE.md) and
[the version-trace sample](docs/AI_ALIGNMENT_REVISABILITY_VERSION_SAMPLE.md).
The local and hosted `0.6.x` line includes a 588-decision real-policy
benchmark, sealed evidence-pack intake, an independent `ai-founding-team` plan,
a server-enforced 20-customer organization cap, and `ai_live_` API keys.
Version `0.6.1` corrects the Gumroad marketing assets, repairs the CI test
path, and aligns the Python, Codex plugin and Worker release metadata.

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
- AI Alignment Revisability Audit with 28 core checks and five profiles.
- A 21-document, 588-decision benchmark spanning the EU AI Act, current UK
  regulation, US federal actions, and enacted US state AI laws.
- A local evidence-pack workflow for SHA-256 sealing, E2/E3/E4 proposals,
  ZIP validation, Markdown/JSON/HTML reports, and MCP access.
- Separate ESG and AI founding plans, each with a monthly quota of 100 jobs.
- A 30-day no-questions-asked full-refund policy on the Gumroad offer.
- Seven-day report retention and tenant-scoped API access.
- Two independent free Codex plugin entries sharing one local/cloud MCP core.

## Claims boundary

The audit evaluates written commitment structure. It does not verify emissions
data, decide whether a company is truthful, determine greenwashing, or replace
legal, assurance, or investment due diligence. Missing evidence means the
examined text did not support a check; it does not prove that an underlying
action is absent.

The current rules are strongest for English and Chinese reports. Scanned PDFs
require OCR, which is not included in the current version.

### AI Alignment Revisability Audit

The same workbench now accepts `X-ESG-Mode: ai-revisability` and
`X-ESG-Profile: general|news_media|advertising|insurance|industrial_design`.
General mode reviews 28 written controls; industry profiles add two specific
checks. It does not assess an individual's personality, psychology, or rights
and must not be used for employment, education, credit, insurance,
immigration, political, or judicial scoring.

The revision-oriented framing is informed by Xue, Z. (2026), *On Recursive
Freedom: A Theory of the Freedom to Revise*, DOI
[10.5281/zenodo.24217876](https://doi.org/10.5281/zenodo.24217876). The
software operationalises only a narrow document-review perspective; the DOI
does not validate the audit results.

The dedicated product page is:

```text
https://esg-commitment-audit-api.franka328162810.workers.dev/ai-revisability-audit
```

Public sample report:

```text
https://esg-commitment-audit-api.franka328162810.workers.dev/ai-revisability-audit/sample
```

See [AI Alignment Revisability Audit](docs/AI_ALIGNMENT_REVISABILITY_AUDIT.md)
for the product scope, profiles, evidence grades, and development boundary.
See [Evidence-pack workflow](docs/EVIDENCE_PACK_WORKFLOW.md) and the
[evidence-pack sample](docs/AI_REVISABILITY_EVIDENCE_PACK_SAMPLE.md) and
[policy benchmark](benchmarks/ai_revisability_2026_11_23/README.md) for commands,
security controls, source provenance, and validation gates.

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
- AI founding plan: https://icsstudies.gumroad.com/l/ai-alignment-revisability-audit
- AI API-key activation: https://esg-commitment-audit-api.franka328162810.workers.dev/ai-revisability-audit/activate
- Evidence workbench: https://esg-commitment-audit-api.franka328162810.workers.dev/workspace
- AI Alignment Revisability Audit: https://esg-commitment-audit-api.franka328162810.workers.dev/ai-revisability-audit
- AI Revisability public sample: https://esg-commitment-audit-api.franka328162810.workers.dev/ai-revisability-audit/sample
- Public landing page: https://esg-commitment-audit-api.franka328162810.workers.dev/
- Health check: https://esg-commitment-audit-api.franka328162810.workers.dev/v1/health
- Privacy draft: https://esg-commitment-audit-api.franka328162810.workers.dev/privacy
- Terms draft: https://esg-commitment-audit-api.franka328162810.workers.dev/terms

The hosted API and both Gumroad founding offers are live. Stripe checkout code is
deployed but is not the current production checkout route. A verified and
unused Gumroad license key can be exchanged once at `/activate` for a
`founding-team` organization and `esg_live_` API key. The AI product uses
`/ai-revisability-audit/activate`, creates an `ai-founding-team` organization,
and issues an `ai_live_` key. A background scheduler runs every 15 minutes and
rotates through at least the 20 oldest-checked Gumroad memberships. The legal
pages state the service boundary but have not received professional legal
review.

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

Each founding plan permits one organization and one shared API key. The ESG
plan costs US$29/month for 100 audited documents. The AI plan costs US$99/month
for 100 policy or evidence-pack jobs. Policy documents may contain at most 100
pages and 50 MB. The AI evidence-pack intake accepts a 100 MB ZIP containing at
most 200 MB of uncompressed content. Each public offer is limited to 20 customer
organizations. Scanned PDFs without a text layer are rejected because OCR is
not included.

`POST /v1/audits` accepts `X-ESG-Mode: commitment`,
`recursive-freedom`, `ai-revisability`, or `evidence-pack`. ESG plans can use
the ESG modes. AI plans can use `ai-revisability` and `evidence-pack`. The AI
document mode also accepts `X-ESG-Profile`, stored with the job so later reviews
remain reproducible.

Owner-only Gumroad test purchases passed without a charge on 2026-11-22 for ESG
and 2026-11-24 for AI. The AI test verified the complete path from a generated
Gumroad license to an `ai-founding-team` organization, an `ai_live_` API key,
and a completed 28-check production audit. Temporary test organizations, keys,
reports and reserved seats were then removed.

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

The repository publishes two independent, free Codex plugin entries that share
one dependency-free MCP core:

```text
.agents/plugins/marketplace.json
plugins/core/server.mjs
plugins/esg-commitment-audit/
plugins/ai-alignment-revisability-audit/
```

Install either or both plugins from the repository marketplace:

```powershell
codex plugin marketplace add franka328162810-cell/esg-commitment-audit --ref main
codex plugin add esg-commitment-audit@ics-tec
codex plugin add ai-alignment-revisability-audit@ics-tec
```

The plugin packages are free. Hosted reviews require a matching ICS API key.
Set `ICS_AUDIT_API_KEY` after activating a Gumroad license:

- ESG activation: `/activate`
- AI activation: `/ai-revisability-audit/activate`

The ESG plugin checks that the account can use `commitment`; the AI plugin
checks for `ai-revisability` and, for evidence packs, `evidence-pack`. A key
from the wrong product is rejected before the document is uploaded.

Shared tools:

- `get_purchase_options`
- `audit_document`
- `audit_text`
- `get_cloud_audit`
- `get_account`
- `delete_cloud_audit`

The AI plugin additionally provides `audit_evidence_pack`. Uploads and deletion
are approval-gated in each `.mcp.json`; read-only account and status checks are
not. Both packages contain byte-identical copies of the canonical
`plugins/core/server.mjs`, checked by an automated hash test.

Claude Code, Hermes, WorkBuddy, generic MCP templates and remote Streamable HTTP
endpoints are documented in
[Cross-client distribution](docs/CROSS_CLIENT_DISTRIBUTION.md). Codex and Claude
Code stdio adapters are verified; Hermes and WorkBuddy remain explicitly
unverified templates. Remote MCP endpoints are:

```text
https://esg-commitment-audit-mcp.franka328162810.workers.dev/mcp/esg
https://esg-commitment-audit-mcp.franka328162810.workers.dev/mcp/ai
```

The root development plugin remains available for local Python audit tools.
Local audit is free and on-device when the Python package is installed.

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
python -m ruff check src tests validation scripts
python -m esg_commitment_audit audit examples\vague_statement.txt
```

## License

Code and rules are licensed under Apache License 2.0. Future formalizations under
`formalizations/` are intended to be licensed separately under CC BY-SA 4.0; no
formal proof is included in v0.6.1.

Copyright 2026 Xue Zhi Xin (ICS-TEC).
