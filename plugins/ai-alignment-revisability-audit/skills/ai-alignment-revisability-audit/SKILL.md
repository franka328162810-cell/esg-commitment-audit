---
name: ai-alignment-revisability-audit
description: Review AI policies, constitutions, model cards, and governance evidence for revision authority, rollback, oversight, and affected-party safeguards.
---

# AI Alignment Revisability Audit

Use this plugin to review whether written AI governance supplies traceable
authority, revision routes, version history, rollback controls, monitoring,
oversight, and affected-party safeguards. It does not test model behaviour,
prove alignment, certify safety, determine legal compliance, or assess a
person's psychology or rights.

## Account and permission checks

The plugin is free. Hosted reviews use the ICS API and require a matching API
key in `ICS_AUDIT_API_KEY` (`ESG_AUDIT_API_KEY` is accepted for compatibility).

1. Call `get_account` before the first upload.
2. Continue only when `compatible` is `true` and
   `allowed_audit_modes` contains `ai-revisability`; evidence-pack review also
   requires `evidence-pack`.
3. If no key is configured and the user asks how to buy or activate, call
   `get_purchase_options` to return the current price, checkout, activation,
   refund and policy links.
4. If the key is missing, belongs to the ESG product, or the subscription is
   inactive, do not upload. Direct the user to the AI activation page:
   https://esg-commitment-audit-api.franka328162810.workers.dev/ai-revisability-audit/activate
5. A paid key is obtained after subscribing at
   https://icsstudies.gumroad.com/l/ai-alignment-revisability-audit and
   activating the Gumroad license key.

Upload only after the user explicitly asks for a hosted review. State the exact
file that will be uploaded and that raw uploads are deleted after success or
final failure while reports expire after seven days.

## Review a policy or governance document

- Use `audit_document` for PDF, DOCX, TXT, or Markdown.
- Use `audit_text` for pasted text.
- Choose the closest profile: `general`, `news_media`, `advertising`,
  `insurance`, or `industrial_design`.
- Use `get_cloud_audit` to poll the job and set `include_report` to `true` once
  the status is `completed`.
- Use `delete_cloud_audit` only when the user explicitly requests deletion.

Lead with the material revision, rollback, oversight, and affected-party gaps.
Preserve source evidence and distinguish `absent`, `asserted`, `documented`,
and `contradicted`. Do not award operational or independent evidence without
the corresponding artifacts and human confirmation.

## Review an evidence pack

Use `audit_evidence_pack` for a sealed ZIP containing one manifest and its
supporting artifacts. The compressed limit is 100 MB and the service rejects
more than 200 MB of uncompressed content.

Report:

1. artifact inventory and hash status;
2. proposed E2/E3/E4 grade changes;
3. remaining artifact gaps;
4. warnings and the required human confirmation.

A matching SHA-256 value proves byte consistency, not that an event occurred,
that an issuer had authority, or that an independent review was adequate.

## Error recovery

- `401`: ask the user to issue a valid key at the AI activation page.
- `403`: explain that the key is inactive or belongs to the ESG product; do
  not retry with the same key.
- `413`: document exceeds 50 MB or the ZIP exceeds 100 MB compressed or 200 MB
  uncompressed.
- `415`: unsupported file or scanned PDF without a text layer.
- `429`: monthly allowance exhausted.
- `503` or a network timeout during upload: the job may already exist. Do not
  repeat the upload automatically; call `get_account` and inspect the job
  status before asking the user whether to retry.

## Offline fallback

When the open-source Python package is installed:

```text
ai-revisability-audit audit <file> --profile general --format json
ai-revisability-audit compare <previous-file> <current-file> --profile general
ai-revisability-audit evidence-pack <manifest-or-zip> --format json
```
