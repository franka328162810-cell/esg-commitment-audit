---
name: esg-commitment-audit
description: Audit ESG and climate commitments for structural completeness, evidence traceability, and CRV gaps; use for corporate sustainability reports, pledge inventories, and commitment wording reviews.
---

# ESG Commitment Audit

Use this skill to inspect written ESG or climate commitments. The result is a
structure and evidence audit, not a compliance finding, assurance opinion,
greenwashing determination, or measure of actual environmental performance.

## Before uploading

The marketplace plugin uses the ICS hosted API. Upload only after the user
explicitly asks for a hosted audit. Tell the user which local file will be
uploaded, confirm that `ESG_AUDIT_API_KEY` is configured, and state that the
source is deleted after success or final failure and the report expires after
seven days.

Never upload a file merely because the plugin is installed.

## Run a hosted audit

- For a local PDF, DOCX, TXT, or Markdown file, call `audit_document`.
- For pasted text, call `audit_text`.
- Set `mode` to `ai-revisability` for an AI policy, constitution, model card,
  or governance framework. Choose `profile` as `general`, `news_media`,
  `advertising`, `insurance`, or `industrial_design`.
- Call `get_cloud_audit` after the task is queued. Set `include_report` to true
  once the status is `completed`.
- Call `get_account` when the user asks about plan or remaining quota.
- Call `delete_cloud_audit` only when the user explicitly requests deletion.

Use `default` weights unless the user explicitly requests another preset.

If the user requests an offline audit and `esg-commitment-audit` is installed locally, use
the open-source CLI instead:

```text
esg-commitment-audit audit <file> --format json
```

## Interpret results

Lead with:

1. the number and categories of extracted commitments;
2. the strongest structure gaps across the document;
3. up to five high-value findings with page or paragraph evidence;
4. parser warnings that require human confirmation.

Distinguish:

- no supporting text found;
- partial evidence;
- evidence found outside the primary commitment paragraph;
- extraction uncertainty.

Never describe a low CRV score as proof of greenwashing or poor performance.
Never convert a high score into an assurance conclusion.
