# AI Alignment Revisability Audit Beta

Version: `v0.4.0.dev2`

This is a document-review Beta, not a safety certification.

## Included

- Hosted `ai-revisability` audit mode.
- 28 core written controls.
- Five profiles: general AI governance, news media, advertising, insurance,
  and industrial design.
- Two additional profile-specific checks for each industry profile.
- Evidence grades, risk warnings, recommendations, required-evidence lists, and
  source-level citations.
- Hosted product page and synthetic public sample.
- Hosted workbench rendering and CSV export for the new report type.
- Local version-to-version comparison through `ai-revisability-audit compare`.
- Codex MCP local tools for single-document and version comparison reviews.
- Hosted plugin bridge support for `mode` and `profile`.
- D1 migration `0004_audit_profile.sql`.

## Product links

- Product:
  https://esg-commitment-audit-api.franka328162810.workers.dev/ai-revisability-audit
- Sample:
  https://esg-commitment-audit-api.franka328162810.workers.dev/ai-revisability-audit/sample
- Workbench:
  https://esg-commitment-audit-api.franka328162810.workers.dev/workspace

## Validation completed

- Full Python test suite passed.
- Ruff check and format checks passed.
- TypeScript and Wrangler checks passed.
- Node plugin tests passed.
- Hosted general profile returned 28 checks.
- Hosted insurance profile returned 30 checks.
- GitHub CI and Production Health checks passed.

## Claim boundary

The text engine can establish source-linked written claims and documented
controls. It cannot prove actual AI behaviour, hidden intent, operational
effectiveness, legal compliance, safety, or independent verification.

This release has not completed a held-out AI-policy benchmark or external
methodological review. A separate paid subscription and formal Codex
marketplace package remain deferred.
