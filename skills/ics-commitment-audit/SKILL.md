---
name: ics-commitment-audit
description: Audit ESG and climate commitments for structural completeness, evidence traceability, and CRV gaps; use for corporate sustainability reports, pledge inventories, and commitment wording reviews.
---

# ICS Commitment Audit

Use this skill to inspect written ESG or climate commitments. The output is a
structure and evidence audit, not a compliance finding, assurance opinion,
greenwashing determination, or measure of actual environmental performance.

## Run the audit

- For a local PDF, DOCX, TXT, or Markdown file, call
  `audit_local_document` from the `ics-commitment-audit` MCP server.
- For pasted text, call `audit_text`.
- Use `default` weights unless the user explicitly requests another preset.
- If the MCP tool is unavailable, run:
  `ics-crv audit <file> --format json`.

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
for the hosted service and `ICS_AUDIT_API_URL` plus `ICS_AUDIT_API_KEY` are
configured. Before submission, tell the user that the selected document will be
uploaded to that URL and retained according to the service policy.

Local audit remains the default. Do not upload a document merely because a cloud
key is configured.
