---
name: esg-commitment-audit
description: Audit ESG commitments or AI alignment/governance documents for source-linked structural evidence; use for sustainability reports, AI policies, constitutions, model cards, and revision/rollback reviews.
---

# ESG Commitment Audit

Use this skill to inspect written ESG or climate commitments. The output is a
structure and evidence audit, not a compliance finding, assurance opinion,
greenwashing determination, or measure of actual environmental performance.

## Run the audit

- For a local PDF, DOCX, TXT, or Markdown file, call
  `audit_local_document` from the `esg-commitment-audit` MCP server.
- For pasted text, call `audit_text`.
- Use `default` weights unless the user explicitly requests another preset.
- If the MCP tool is unavailable, run:
  `esg-commitment-audit audit <file> --format json`.

Do not infer commitments or scores without tool output. Preserve the returned
page, paragraph, excerpt, and fact provenance.

## Interpret results

Lead with:

1. the number and categories of extracted commitments;
2. the strongest structure gaps across the document;
3. up to five high-value findings with page-level evidence;
4. document warnings that require human confirmation.

Distinguish these states explicitly:

- no supporting text found;
- partial evidence;
- evidence present outside the primary commitment paragraph;
- extraction uncertainty or parser warning.

Never describe a low CRV score as proof of greenwashing or poor performance.
Never convert a high score into an assurance conclusion.

For methodology, weights, and limitations, read
[the method](../../docs/METHODOLOGY.md) and
[limits](../../docs/LIMITATIONS.md) when the user asks how scoring works, requests
a defensible interpretation, or challenges a result.

## Hosted audit

Use `submit_cloud_audit` or `get_cloud_audit` only when the user explicitly asks
for the hosted service and `ESG_AUDIT_API_URL` plus `ESG_AUDIT_API_KEY` are
configured. Before submission, tell the user that the selected document will be
uploaded to that URL and retained according to the service policy.

Local audit remains the default. Do not upload a document merely because a cloud
key is configured.

## AI Alignment Revisability Audit

For an AI policy, constitution, model card, system card, or governance policy,
use `audit_revisability_document`; for pasted text, use
`audit_revisability_text`.

When the user supplies a previous and current version, use
`audit_revisability_version` to identify evidence-grade movement, high
materiality regressions, new warnings, and clause additions, removals, or
modifications.

Choose the closest review profile:

- `general`;
- `news_media`;
- `advertising`;
- `insurance`;
- `industrial_design`.

The report grades written evidence as `absent`, `asserted`, `documented`, or
`contradicted`. Do not upgrade a claim to operationally evidenced or
independently verified without separate records and human review.

Lead with the material gaps and the affected revision or rollback route. Never
describe the result as a safety certification, legal-compliance finding, proof
of alignment, or assessment of a person's psychology or rights.

If MCP tools are unavailable, the product-specific local commands are:

```text
ai-revisability-audit audit <file> --profile general --format json
ai-revisability-audit compare <previous-file> <current-file> --profile general
ai-revisability-audit serve
```
