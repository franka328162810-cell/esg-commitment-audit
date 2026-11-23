# Codex plugins v0.5.0

This release publishes two independent ICS Codex plugins that share one MCP/API
core.

## Install

```powershell
codex plugin marketplace add franka328162810-cell/esg-commitment-audit --ref main
codex plugin add esg-commitment-audit@ics-tec
codex plugin add ai-alignment-revisability-audit@ics-tec
```

The plugins are free. Set `ICS_AUDIT_API_KEY` to a matching key obtained through
the activated Gumroad subscription.

## ESG Commitment Audit

- Reviews PDF, DOCX, TXT, and Markdown reports.
- Extracts written ESG and climate commitments with source evidence.
- Tests observability, enforceability, and revisability.
- Hosted plan: US$29/month for 100 jobs, limited to 20 customer organizations.

Activation:
https://esg-commitment-audit-api.franka328162810.workers.dev/activate

## AI Alignment Revisability Audit

- Reviews policies, constitutions, model cards, and governance frameworks.
- Returns 28 core controls; industry profiles return 30.
- Supports general, news-media, advertising, insurance, and industrial-design
  configurations.
- Reviews sealed evidence-pack ZIPs and proposes human-confirmed E2/E3/E4
  upgrades.
- Hosted plan: US$99/month for 100 policy or evidence-pack jobs, limited to 20
  customer organizations.

Activation:
https://esg-commitment-audit-api.franka328162810.workers.dev/ai-revisability-audit/activate

## Safety and permissions

- Both plugins declare `Read` and `Write` capabilities.
- Uploads and deletion require approval for each action.
- The core checks account plan and allowed modes before uploading.
- Wrong-product keys stop before document transfer.
- GET requests use bounded retries; uploads are never retried automatically.
- Missing keys and API failures return concrete activation or recovery steps.

## Validation

- 126 Python tests passed.
- 11 plugin core and bundle tests passed.
- Both Codex skills passed validation.
- Five scripted production role trials passed against the live API.
- Fresh install, simultaneous installation, uninstall, reinstall, and upgrade
  from `0.4.0-dev.2` passed in isolated Codex homes.

External human pilots are still required before claiming market-validated GA.

## Claims boundary

These products review written governance structure and submitted evidence. They
do not certify AI safety, legal compliance, assurance, model alignment,
environmental performance, or the truth of an ESG commitment.
