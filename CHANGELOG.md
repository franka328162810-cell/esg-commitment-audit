# Changelog

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
- Added `ics-crv-admin`, `ics-crv-mcp`, and `ics-crv serve-commercial`.
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
