# ESG Commitment Audit

## Customer guide for the Founding Small Team plan

ESG Commitment Audit is a hosted, evidence-first workbench for reviewing the
structure of written ESG and climate commitments. It helps analysts locate what
an organization has promised, identify the evidence attached to each finding,
and see where measurement, accountability, or revision terms are missing.

The product reviews written commitment structure. It does not determine whether
a company is truthful, compliant, assured, or engaged in greenwashing.

## Who it is for

- Sustainability and ESG analysts reviewing corporate reports.
- Boutique consultancies that need a repeatable evidence workflow.
- Researchers comparing target wording, baselines, scopes, and review terms.
- Procurement or due-diligence teams preparing questions for a human review.

The current production rules are strongest for English and Chinese reports.

## Founding Small Team plan

| Item | Included |
|---|---|
| Price | US$29 per month |
| Monthly quota | Up to 100 audited documents |
| Document size | Up to 100 pages and 50 MB |
| Access model | One organization and one shared API key |
| Processing | Standard asynchronous queue |
| Report retention | Seven days |
| Support | Email support; no custom SLA |
| Public founding capacity | 20 customer organizations |

The subscription renews monthly through Gumroad. Cancellation and billing are
managed in Gumroad. Gumroad also displays the applicable taxes at checkout.
The public offer includes a 30-day no-questions-asked full refund.

## Supported files

- PDF with a selectable text layer
- DOCX
- TXT
- Markdown

Scanned PDFs without a text layer are not supported because OCR is not included
in the current version. If the service reports `No text layer was found in the PDF`, run OCR
or use the original text-based source before retrying.

## Purchase and activation

1. Open the
   [Gumroad product page](https://icsstudies.gumroad.com/l/esg-commitment-audit)
   and subscribe to the `Founding Small Team` tier.
2. Open the purchase receipt or Gumroad content page and copy the license key.
3. Go to the
   [activation page](https://esg-commitment-audit-api.franka328162810.workers.dev/activate).
4. Enter the Gumroad license key and your organization name.
5. Copy the generated `esg_live_...` API key immediately. It is displayed once.
6. Store both credentials privately. Never put the API key in a public GitHub
   repository, client-side JavaScript, screenshots, or support posts.
7. Open the
   [evidence workbench](https://esg-commitment-audit-api.franka328162810.workers.dev/workspace),
   paste the API key into the current browser tab, choose a mode, and upload the
   document. The key is kept in that tab's `sessionStorage` and is removed when
   the tab closes.

The server verifies the Gumroad purchase before issuing access. A license can be
activated once. Gumroad membership status is rechecked every 15 minutes, and
access is deactivated when the paid membership ends or the sale is refunded,
disputed, charged back, cancelled, or fails to renew.

## Confirm the account

```bash
curl \
  -H "Authorization: Bearer YOUR_ESG_API_KEY" \
  https://esg-commitment-audit-api.franka328162810.workers.dev/v1/account
```

The response includes the plan, active state, monthly limit, documents used,
remaining quota, and Gumroad billing status. It never returns the original
Gumroad license key.

## Run an audit

Use the hosted browser workbench for the normal workflow. It supports
drag-and-drop input, progress polling, page/paragraph evidence review, JSON and
CSV downloads, and report deletion.

For scripted clients, replace the file name and path with your own document:

```bash
curl \
  -X POST \
  -H "Authorization: Bearer YOUR_ESG_API_KEY" \
  -H "Content-Type: application/pdf" \
  -H "X-ESG-Filename: sustainability-report.pdf" \
  -H "X-ESG-Mode: commitment" \
  --data-binary @sustainability-report.pdf \
  https://esg-commitment-audit-api.franka328162810.workers.dev/v1/audits
```

The API returns HTTP `202` and a job identifier. Poll the job until its status is
`completed` or `failed`:

```bash
curl \
  -H "Authorization: Bearer YOUR_ESG_API_KEY" \
  https://esg-commitment-audit-api.franka328162810.workers.dev/v1/audits/JOB_ID
```

Retrieve the completed JSON report:

```bash
curl \
  -H "Authorization: Bearer YOUR_ESG_API_KEY" \
  https://esg-commitment-audit-api.franka328162810.workers.dev/v1/audits/JOB_ID/report
```

## What the report contains

- Extracted commitment text and target values.
- Baseline year, target year, scope, owner, reporting, assurance, remedy, and
  revision evidence when present in the source.
- `V_obs`, `V_enf`, and `V_rev` scores and the combined CRV structure score.
- Page- or paragraph-level source evidence for supported findings.
- Explicitly missing checks. A missing check means the examined text did not
  provide supporting evidence; it does not prove that an underlying action is
  absent.

See [Methodology](METHODOLOGY.md) for weights and interpretation bands.

## AI Alignment Revisability Audit Beta

Change `X-ESG-Mode` to `ai-revisability`, choose `X-ESG-Profile` as `general`,
`news_media`, `advertising`, `insurance`, or `industrial_design`, and submit an
AI policy, constitution, model card, or governance framework. General mode
covers 28 written controls:

- alignment targets and normative hierarchy;
- revision authority and stakeholder participation;
- review cadence, change triggers, and gradual deployment;
- version identifiers, change logs, and prior-version access;
- rollback conditions, authority, exercises, and protected clauses;
- notice, explanation, appeal, refusal, and exit;
- monitoring metrics, audit logs, and retention;
- independent oversight, anti-abuse controls, and uncertainty;
- capability-gate and interruption evidence.

Industry profiles add two safeguards and therefore return 30 checks. The Beta
reviews written evidence only. It does not test an individual's personality,
psychology, political views, employability, creditworthiness, insurability,
educational eligibility, immigration status, or legal culpability. Each hosted
job consumes one unit from the same monthly quota.

The dedicated product page is:

```text
https://esg-commitment-audit-api.franka328162810.workers.dev/ai-revisability-audit
```

## Data handling

- The vendor receives only documents explicitly submitted to the hosted API.
- Source uploads are deleted after success or final failure.
- Customer reports remain available for seven days.
- Report objects are tenant-scoped and require the customer's API key.
- Gumroad license keys are encrypted before storage and are not returned by an
  API endpoint.
- Terminal job metadata is retained for up to 180 days.

Read the public [privacy page](https://esg-commitment-audit-api.franka328162810.workers.dev/privacy)
and [terms](https://esg-commitment-audit-api.franka328162810.workers.dev/terms).

## Refunds and cancellation

The product displays a 30-day no-questions-asked full refund. Contact
**franka328162810@gmail.com** or use Gumroad support within 30 days of purchase
to request the refund.

Cancel future renewals from the Gumroad purchase or library page. Ending a
membership removes hosted API access after the Gumroad status check.

## Troubleshooting

| Response | Meaning | Action |
|---|---|---|
| `401` | Missing, invalid, or revoked API key | Recheck the bearer token |
| `403` | Gumroad license is inactive | Check the Gumroad purchase status |
| `409` | Report is not ready | Poll the job again |
| `413` | File exceeds 50 MB or 100 pages | Reduce the document or split it |
| `415` | Unsupported file type | Use PDF, DOCX, TXT, or Markdown |
| `429` | Monthly quota exhausted | Wait for the next usage period or upgrade |

For support, email **franka328162810@gmail.com**. Describe the job ID and HTTP
status, but never send an API key or sensitive source document.

## Limits of use

The service provides structured document analysis and research support. It is
not audit assurance, legal advice, compliance certification, investment advice,
or a finding that an organization is or is not greenwashing.
