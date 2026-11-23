# AI Alignment Revisability Audit release check

Date: 2026-11-24 (Asia/Shanghai)

Release: `v0.5.0.dev1`

## Commercial offer

| Item | Verified value |
|---|---|
| Product | AI Alignment Revisability Audit — Founding Team |
| Price | US$99 per month |
| Billing | Monthly only |
| Public capacity | First 20 customer organizations |
| Monthly jobs | 100 policy or evidence-pack jobs per organization |
| Policy document | 100 pages and 50 MB |
| Evidence pack | 100 MB compressed and 200 MB uncompressed |
| Report retention | Seven days |
| API keys | `ai_live_` prefix |
| Refund | 30-day no-questions-asked full refund |
| Gumroad | https://icsstudies.gumroad.com/l/ai-alignment-revisability-audit |

The Gumroad public payload reports `is_licensed: true`, a monthly price of
9,900 US cents, and 20 remaining public slots. A Gumroad License key block is
present on the product content page. Multi-seat licensing is disabled.

## Cloudflare deployment

| Item | Verified value |
|---|---|
| Account ID | `aa7d0faa102dcea2d358907bbf96b7ec` |
| Account domain | `ics-studies.org` active |
| Worker version | `ecd2196a-779f-4617-a6e0-947a6d3c0561` |
| Health version | `0.5.0.dev1` |
| Container tag | `0.5.0.dev1-r1` |
| Container digest | `sha256:553db58e8736388fc26e3425003ccfd976b1932b121e5d1d1ac10532efb2d363` |
| D1 migration | `0005_founding_seats.sql` applied |

## Automated checks

| Check | Result |
|---|---|
| Python tests | 126 passed |
| Ruff lint | passed |
| Ruff format | 55 files formatted |
| Cloudflare TypeScript | passed |
| Wrangler deployment dry run | passed |

## Production checks

- `/v1/health`, product page, AI activation page, workbench, privacy and terms
  returned HTTP `200`.
- The landing page no longer states that the AI product is included in the
  ESG US$29 plan.
- An AI plan account returned only `ai-revisability` and `evidence-pack`.
- An ESG plan account returned only `commitment` and `recursive-freedom`;
  requests for either AI mode returned HTTP `403`.
- A public AI policy completed with 28 checks across nine dimensions.
- A public evidence-pack ZIP completed with four artifacts, eight promotion
  proposals and 13 unresolved controls.
- A Gumroad owner-only test purchase completed without a charge, generated a
  real license key, activated seat 1 of 20, issued an `ai_live_` key, and
  completed a 28-check production audit.
- Temporary test organizations, API keys, jobs, R2 reports and the reserved D1
  seat were deleted after validation.

## Remaining operational notes

- The canceled owner test membership may continue to occupy one Gumroad active
  supporter slot until its scheduled membership end. The Gumroad maximum is
  therefore temporarily set to 21 so the public page exposes 20 real slots.
  The D1 guard remains authoritative at 20 real AI organizations.
- Reduce the Gumroad maximum from 21 to 20 after the canceled test membership
  no longer occupies a slot.
- The legal pages have not received independent counsel review.
- This release is a document and evidence audit, not an AI safety certificate,
  legal compliance finding, or assurance opinion.
