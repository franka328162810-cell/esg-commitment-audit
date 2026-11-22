# v0.2.0 release check

Date: 2026-11-21 (Asia/Shanghai)

## Release decision

The v0.2.0 extraction gate passed. The local product, authenticated commercial
API foundation, and Codex plugin package are structurally complete.

This is a controlled-pilot release. A public paid launch still requires a
payment merchant account, processor adapter, HTTPS deployment, legal/privacy
review, monitoring, backups, and capacity testing.

## Environment

- Windows
- Python 3.13.14 for the verification run
- Ruff
- Pytest
- FastAPI/Starlette TestClient

## Functional verification

| Check | Result |
|---|---|
| Automated tests | **52 passed** |
| Static analysis | Ruff check passed |
| Format check | Ruff format passed |
| Commercial gate check | Passed |
| Local CLI | `esg-commitment-audit 0.2.0` |
| Commercial admin CLI | organization/key/plan commands present |
| MCP server | initialize and 4 tools verified |
| Skill validation | `Skill is valid!` |
| Plugin manifest | JSON parsed; skill/MCP references resolved |
| Wheel build | succeeded |
| Wheel size | 68,553 bytes |
| Wheel SHA-256 | `5c8466f831748c3cc4a03df22aa0619d4b0be5cbabf2720fd84f013e56aee687` |
| Isolated wheel install | succeeded |
| Installed CLI smoke | report version 0.2.0 |
| Commercial API smoke | HTTP 202, completed job, one extracted commitment |

Two test warnings are deprecation notices from the installed
FastAPI/Starlette/httpx test stack. They are not application failures.

## Real-report gate

| Metric | Result | Gate | Status |
|---|---:|---:|---|
| Candidate precision | 98.63% | ≥80% | Pass |
| Unique commitment recall | 93.75% | ≥85% | Pass |
| E/S/G top-level accuracy | 100% | ≥90% | Pass |
| Subcategory accuracy | 97.22% | informational | — |
| Page citation coverage | 100% | 100% | Pass |
| Manual unique commitments | 80 | 80–100 | Pass |
| Duplicate candidates | 0 | 0 | Pass |

The review is a Codex adjudication under the written rules. The author waived
an independent second human reviewer; this is not independent validation.

See `docs/REAL_REPORT_VALIDATION_V020_2026-11-21.md`.

## Commercial API checks

| Check | Result |
|---|---|
| Missing API key rejected | Pass |
| Invalid/revoked key rejected | Pass |
| Tenant isolation | Pass |
| Monthly quota enforcement | Pass |
| Failed job quota refund | Covered by state logic and tests |
| Input deletion after processing | Pass |
| Report retention/deletion paths | Implemented |
| Billing HMAC and timestamp validation | Pass |
| Plan activation webhook | Pass |

## Codex plugin checks

| Check | Result |
|---|---|
| `.codex-plugin/plugin.json` | Present |
| `.mcp.json` | Present |
| `skills/esg-commitment-audit/SKILL.md` | Present |
| `agents/openai.yaml` | Present |
| Local audit tools | Present |
| Cloud job tools | Present |
| Cloud submission approval gate | Present |

## Known limitations

- Scanned PDFs still require OCR, which is not included.
- Complex merged-cell tables may still need manual review.
- Chinese and English rules are stronger than other languages.
- A 50–150 page PDF may take minutes and should run asynchronously.
- The built-in commercial queue is single-node SQLite plus an in-process worker.
- The provider-neutral billing webhook needs a processor-specific adapter.
- No external assurance, legal opinion, or environmental-performance validation
  is produced.

## External launch prerequisites

1. Git author name/email, GitHub repository URL, and public metadata.
2. HTTPS deployment and encrypted storage.
3. Payment merchant account, price IDs, tax/refund policy, and processor adapter.
4. Privacy policy, terms, DPA, and jurisdiction-specific legal review.
5. Database/report backup and restore drill.
6. Load test and service-level objectives for the selected plan.
7. Incident response and API-key rotation procedure.
