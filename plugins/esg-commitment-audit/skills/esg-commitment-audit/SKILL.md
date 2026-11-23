---
name: esg-commitment-audit
description: Audit ESG and climate commitments for source-linked evidence and CRV structure gaps; use for sustainability reports, pledge inventories, and commitment wording reviews.
---

# ESG Commitment Audit

Use this plugin to find written ESG or climate commitments and test whether the
text supplies observable measures, enforcement routes, owners, remedies, and
revision terms. The result is a document-structure review, not assurance,
legal advice, compliance certification, or proof of environmental performance.

## Account and permission checks

The plugin is free. Hosted uploads use the ICS API and require a matching API
key in `ICS_AUDIT_API_KEY` (`ESG_AUDIT_API_KEY` is accepted for compatibility).

1. Call `get_account` before the first upload.
2. Continue only when `compatible` is `true` and
   `allowed_audit_modes` contains `commitment`.
3. If the key is missing, belongs to the AI product, or the subscription is
   inactive, do not upload. Direct the user to the ESG activation page:
   https://esg-commitment-audit-api.franka328162810.workers.dev/activate
4. A paid key is obtained after subscribing at
   https://icsstudies.gumroad.com/l/esg-commitment-audit and activating the
   Gumroad license key.

Upload only after the user explicitly asks for a hosted audit. State the exact
file that will be uploaded and that raw uploads are deleted after success or
final failure while reports expire after seven days.

## Run the review

- Use `audit_document` for a PDF, DOCX, TXT, or Markdown file.
- Use `audit_text` for pasted text.
- Use `default` weights unless the user explicitly requests another preset.
- Use `get_cloud_audit` to poll a queued job. Set `include_report` to `true`
  after the status is `completed`.
- Use `delete_cloud_audit` only when the user explicitly requests deletion.

Treat `audit_document` and `audit_text` as external uploads. The bundled MCP
configuration requires approval before either tool runs.

## Interpret the report

Lead with:

1. the number and E/S/G categories of extracted commitments;
2. the strongest observability, enforceability, and revisability gaps;
3. up to five high-value findings with page or paragraph evidence;
4. parser warnings or extraction uncertainty that require human inspection.

Never describe a low CRV score as greenwashing, poor environmental performance,
or a compliance failure. Never treat a high score as assurance.

## Error recovery

- `401`: ask the user to issue a valid key at the ESG activation page.
- `403`: explain that the key is inactive or belongs to another ICS product;
  do not retry with the same key.
- `413`: document is over 50 MB or 100 pages.
- `415`: unsupported file or scanned PDF without a text layer.
- `429`: monthly allowance exhausted.
- `503` or a network timeout during upload: the job may already exist. Do not
  repeat the upload automatically; call `get_account` and inspect the job
  status before asking the user whether to retry.

## Offline fallback

When the user requests an offline review and the open-source Python package is
installed:

```text
esg-commitment-audit audit <file> --format json
```
