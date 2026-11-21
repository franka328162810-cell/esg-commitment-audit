# v0.3.0 release check

Date: 2026-11-22 (Asia/Shanghai)

## Release decision

The hosted evidence workbench and AI Policy Revision Audit Beta passed local,
integration, container, production, and responsive-layout checks. Production
was deployed with the immutable image tag `0.3.0-r1`.

This is a controlled commercial pilot. It is not an independent assurance
product or a legal/compliance certification.

## Automated verification

| Check | Result |
|---|---|
| Python test suite | 65 passed |
| Ruff check | Passed with Windows mount `EXE002` ignored |
| Ruff format | 33 files already formatted |
| Python compile | Passed |
| TypeScript | Passed |
| Wrangler deploy dry run | Passed |
| Inline browser scripts | Both parsed successfully |
| Container health | Passed |
| Container AI-policy smoke | Ten checks returned |
| Container ESG smoke | One commitment returned |

The only test warning is a FastAPI/Starlette deprecation notice from the test
stack.

## Browser verification

| View | Result |
|---|---|
| Desktop landing page | Gumroad, activation, workbench, and Beta visible |
| Desktop workbench | Controls, modes, quota, upload, and CSP present |
| 390 px mobile viewport | Inner width 390; HTML/body scroll width 390 |
| Mobile AI-policy report | Checks, evidence, risk language, and recommendations readable |
| JSON/CSV controls | Present after completed report |
| Delete controls | Present; quota warning shown before deletion |

## Production acceptance

The production script created two temporary trial organizations and removed
both after the test.

| Check | Result |
|---|---|
| Invalid API key | HTTP 401 |
| Fresh trial quota | 0 used |
| AI policy mode | Completed with 10 checks |
| ESG commitment mode | Completed with one commitment |
| Cross-tenant job access | HTTP 404 |
| Quota accounting | One unit per successful mode |
| 101-page PDF | HTTP 413-equivalent failure |
| Rejected-file quota | Refunded |
| Report deletion | 204 |
| Delete preserves used quota | Passed |
| Temporary test records | 0 organizations, 0 keys, 0 jobs left |

## Data migration

- Pre-migration D1 export: 16,370 bytes.
- SHA-256:
  `F4D27B085D4A6F9D89A095C055A9479EBEA91D37A13C6E0EEF7042F7E3F37D4B`.
- Migration `0003_audit_mode.sql` applied successfully.
- Existing jobs: 16, all backfilled to `commitment`.

## Remaining risks

- The AI policy checklist has not received independent validation.
- Privacy, terms, refund, tax, and data-processing language still need
  professional review for the seller's jurisdiction and target markets.
- External alert routing and a full production restore simulation should be
  completed before paid volume grows.
- Representative Chinese and English PDFs near the 100-page limit should be
  load-tested at expected concurrency.
