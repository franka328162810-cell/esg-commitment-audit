# Changelog

## 0.5.0.dev1 — hosted founding release

Late-2026 commercial release for AI Alignment Revisability Audit.

- Added a 21-document, 588-decision benchmark for the 28 core written controls.
- Added the EU Artificial Intelligence Act, UK Data (Use and Access) Act 2025,
  UK AI and automated decision-making code regulation 2026, current US federal
  actions, and enacted US state AI laws.
- Added source SHA-256 verification, calibration/evaluation splits, exact-grade
  accuracy, positive precision/recall, confusion counts, false-positive and
  false-negative reporting, and evidence-span coverage gates.
- Added `ai-revisability-audit benchmark`.
- Added the sealed evidence-pack workflow with SHA-256 pinning, artifact-type
  compatibility mapping, E2/E3/E4 promotion proposals and mandatory human
  confirmation.
- Added safe ZIP intake with per-file, total-size, entry-count, path-traversal,
  symbolic-link, encryption and compression-ratio checks.
- Added `ai-revisability-audit evidence-pack-seal`.
- Added the local `/revisability/evidence` workbench and the MCP
  `audit_evidence_pack` tool.
- Retained official enactment summaries as summaries rather than presenting
  them as full statutory text.
- Added hosted `evidence-pack` intake with a 100 MB compressed request limit and
  a 200 MB uncompressed artifact limit.
- Added the separate US$99/month `ai-founding-team` plan, `ai_live_` API keys,
  mode isolation, and a D1-enforced 20-customer founding-seat cap.
- Added the Gumroad AI product ID and dedicated activation route.
- Added production tests covering Gumroad license generation, activation,
  `ai_live_` access, a completed 28-check audit, evidence-pack processing, and
  ESG-to-AI mode denial.

## 0.4.0.dev2 — development

AI Alignment Revisability Audit development milestone.

- Added a new document-review engine with 28 core checks across alignment
  targets, authority, revision, version history, rollback, affected-party
  safeguards, monitoring, oversight, and written technical controls.
- Added four first-cohort profiles: news media, advertising, insurance, and
  industrial design.
- Added E0-E4-compatible evidence grades while limiting automatic document-only
  results to absent, asserted, documented, and contradicted.
- Added evidence requests, risk warnings, priority recommendations, and a
  strict non-certification claim boundary.
- Added `esg-commitment-audit revisability`.
- Added the product-specific `ai-revisability-audit` command with `audit`, `compare`,
  and `serve` subcommands; the combined `esg-commitment-audit` commands remain compatible.
- Added a local workbench at `/revisability`.
- Added JSON, Markdown, and standalone HTML reports.
- Added the hosted `ai-revisability` mode, industry-profile selection, dedicated
  product and sample pages, and hosted workbench report rendering.
- Added persistent `audit_profile` storage through D1 migration `0004`.
- Added `esg-commitment-audit revisability-version` and `/revisability/versions` for
  previous/current document comparison.
- Added check-grade movement, high-materiality regression, warning movement, and
  statement addition/removal/modification reporting.
- Added an English strong sample policy and initial automated tests.
- Engineering-design review remains deferred.
- Hosted AI-revisability jobs, persistent source monitoring, evidence-pack
  intake, and the cross-organisation evidence graph are not yet part of this
  milestone.

## 0.3.1 — 2026-11-22

Recursive Freedom Audit rule-quality release.

- Added a dedicated public product page at `/recursive-freedom`.
- Added a public source-based sample report at `/recursive-freedom/sample`.
- Tightened scope/owner checks so a generic policy reference is not treated as
  a complete scope, owner, and effective-date statement.
- Removed false-positive matches for generic consent, general legal oversight,
  user access suspension, and unrelated human-review language.
- Distinguished advance notice from a public updates page.
- Distinguished audit logs from general monitoring.
- Added external-review evidence as independent oversight.
- Tested the v0.2 AI-policy rule set against five public AI policies or
  governance documents.
- Recorded 50/50 exact status matches in the internal written adjudication,
  with 19 expected positive checks, zero recorded false positives, and zero
  recorded false negatives.
- Added a public validation record that explicitly states this is not an
  independent external validation.
- Expanded automated tests to 74.

## 0.3.0 — 2026-11-22

Hosted evidence-workbench and AI-policy Beta release.

- Added a browser workbench at `/workspace` for API-key connection, account
  quota display, drag-and-drop upload, asynchronous status polling, evidence
  review, JSON/CSV download, and report deletion.
- Added the AI Policy Revision Audit Beta with ten written governance checks:
  scope/owner, review cadence, revision process, version history, notice,
  appeal/human review, refusal/exit, monitoring/audit, rollback/deprecation,
  and independent oversight.
- Added `X-ESG-Mode: commitment|recursive-freedom` and persisted the selected
  mode on each audit job through D1 migration `0003_audit_mode.sql`.
- Kept both modes under the same document quota, page limit, file-size limit,
  privacy boundary, and tenant-isolation controls.
- Added per-document risk-language safeguards so a protective notice clause
  cannot hide a separate “without notice” clause.
- Replaced the public Chinese-only launch page with an English product page
  linking Gumroad, activation, and the workbench.
- Added the DOI-backed intellectual provenance for the revision-oriented Beta
  framing without treating the publication as independent software validation.
- Added a locked container-dependency manifest and reproducible v0.3.0 wheel
  build.
- Passed 65 automated Python tests and Ruff/TypeScript/Wrangler checks.
- Passed production tests for both modes, invalid keys, cross-tenant isolation,
  one-document quota accounting, 101-page rejection, quota refund, and report
  deletion.

## Cloud pilot extension — 2026-11-21

- Deployed the hosted Worker, D1, R2, Queue, Durable Object, and container
  runtime on Cloudflare.
- Added Stripe Checkout Session creation while keeping live payment disabled
  until merchant credentials and Price IDs exist.
- Added public landing, privacy draft, and terms draft pages.
- Added 7-day report retention, 180-day metadata cleanup, and a 30-day R2
  lifecycle backstop.
- Fixed malformed PDF/DOCX handling so parsing failures return `400` and refund
  quota immediately without three pointless retries.
- Fixed container capacity and idle lifecycle behavior; 3/3 concurrent TXT,
  DOCX, and PDF audits now pass after the capacity correction.
- Added a dependency-free Node MCP marketplace bundle and a repository
  marketplace manifest, validated by an isolated Codex plugin installation.
- Added cloud smoke, load, MCP, D1 backup, and recovery-drill procedures.

## 0.2.0 — 2026-11-21

Commercial-gate and Codex plugin release.

- Added stable candidate keys derived from document hash, page, and normalized
  commitment text.
- Reconstructed multi-column PDF text without cross-page stitching of table
  content.
- Added target/progress table-role handling, PDF number repair, bilingual
  percent parsing, recurring-obligation extraction, and stricter progress /
  citation / third-party filtering.
- Improved duplicate consolidation and compound-target evidence retention.
- Passed the frozen 80-commitment gate: 98.63% candidate precision, 93.75%
  unique-commitment recall, 100% E/S/G top-level accuracy, and 100% page coverage.
- Added organization tenants, hashed API keys, monthly quotas, persistent audit
  jobs, report retention/deletion, and provider-neutral signed billing webhooks.
- Added `esg-commitment-audit-admin`, `esg-commitment-audit-mcp`, and `esg-commitment-audit serve-commercial`.
- Added a formal Codex plugin manifest, skill, UI metadata, icon, and local/cloud
  MCP tools.
- Added commercial deployment and plugin publication guides.

## 0.1.1 — 2026-11-21

Extraction and evidence-aggregation stabilization candidate. This version is
not commercially released because the real-report gate is not met.

- Split PDF headings, bullet groups, table rows, and page-spanning fragments
  into distinct evidence units.
- Added PDF table extraction as a best-effort source of row-level evidence.
- Added statement classification for commitments, historical results,
  methodologies, governance descriptions, and duplicate restatements.
- Added cross-evidence inheritance for owners, standards, assurance, reporting,
  remedies, and review mechanisms.
- Added duplicate consolidation across repeated report sections.
- Added follow-up validation against Apple and Luxshare reports.

Validation result: candidate precision 83.9%, unique-commitment recall 72.1%,
top-level category accuracy 88.5%. The commercial gate remains closed.

## 0.1.0 — 2026-11-21

Initial local-first reference implementation.

- Added bilingual ESG commitment detection and ESG category classification.
- Added deterministic structural checks for observability, enforceability, and
  reversibility using the public ICS CRV weights.
- Added source evidence for every scoring check that receives points.
- Added same-year conflicting-target warnings.
- Added TXT, Markdown, DOCX, and text-layer PDF ingestion.
- Added CLI, local FastAPI interface, Markdown/JSON/standalone HTML reports, and
  five weight presets.
- Added a 30-case internal detection benchmark and automated tests.
- Added Apache 2.0 licensing, trademark notice, and a separate CC BY-SA 4.0 path
  for future formalizations.

Known exclusions:

- no OCR;
- no LLM extraction;
- no external data verification;
- no online account, payment, or cloud deployment;
- no formal Codex plugin package;
- no claim of external calibration or regulatory certification.
