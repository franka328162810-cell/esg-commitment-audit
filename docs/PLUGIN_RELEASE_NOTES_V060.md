# Codex plugins and audit service v0.6.0

This release completes the commercial onboarding layer for the two independent
ICS Codex plugins.

## Commercial onboarding

- New public `/v1/offers` contract returns current pricing, plans, quotas,
  checkout pages, activation pages, privacy and terms links.
- Both plugins expose read-only `get_purchase_options`, which works without an
  API key.
- ESG and AI activation pages now identify the product, price, monthly limit,
  organization cap, checkout link, product scope and 30-day refund policy.
- API keys remain product-specific: `esg_live_` and `ai_live_`.
- Account preflight still blocks a wrong-product key before any upload.
- Added Claude Code stdio adapters and verified both product entries as
  connected.
- Added Hermes, WorkBuddy and generic MCP templates, explicitly marked
  unverified until their client lifecycle tests pass.
- Added a separate Cloudflare remote MCP Worker with `/mcp/esg` and `/mcp/ai`
  Streamable HTTP endpoints backed by a private service binding.

## Codex plugins

- `esg-commitment-audit` version `0.6.0`.
- `ai-alignment-revisability-audit` version `0.6.0`.
- Both bundle the same SHA-256-identical MCP core.
- AI policy, five industry profiles and sealed evidence-pack review are
  available.
- Uploads and deletion require approval. Account, status and purchase-option
  reads do not require an upload approval.

Install:

```powershell
codex plugin marketplace add franka328162810-cell/esg-commitment-audit --ref main
codex plugin add esg-commitment-audit@ics-tec
codex plugin add ai-alignment-revisability-audit@ics-tec
```

Set `ICS_AUDIT_API_KEY` after purchasing and activating the matching plan.

## Verification

- 126 Python tests passed.
- 12 plugin core and bundle tests passed.
- Both Codex skills passed validation.
- Cloudflare TypeScript and deployment dry-run passed.
- Five production role trials passed: ESG analysis, general AI governance,
  insurance profile, evidence-pack review and wrong-product key rejection.
- Public offer and product-specific activation page checks passed.
- Remote MCP initialize, tools/list, account, policy review, evidence-pack
  review, report retrieval, deletion and plan isolation passed direct protocol
  tests.

External human pilots remain required before claiming market-validated GA.
Claude Code remote HTTP health remains unverified because the local Claude
account is not logged in; only its stdio adapter is currently claimed as
supported.

## Boundaries

The plugins are not safety certifications, legal-compliance findings, assurance
opinions, or proof that an ESG claim or AI control operates in practice.
