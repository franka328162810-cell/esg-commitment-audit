# v0.6.0 release check

Date: 2026-11-24 (Asia/Shanghai)

Status: release candidate; final tag/publication and external human pilots
remain open.

## Versions and artifacts

| Item | Verified value |
|---|---|
| Python package | `0.6.0` |
| Codex plugins | `0.6.0` |
| Worker health version | `0.6.0` |
| Main Worker version | `4884313f-0cbb-4ef1-8aff-220b5387dcf9` |
| Remote MCP Worker version | `f88339b0-bf08-45ce-bd19-4539b4adddc1` |
| Container image | `0.6.0-r2` |
| Container digest | `sha256:9d78173f8bf0caa53ce9d3151f7ca2beac24e864f35e1ebc2fe5860ed87dd9f4` |
| Wheel SHA-256 | `4732acc7a74102d2468ff9c8b0049ec99166e3c3d19cf6a982343b8861bffd32` |

## Automated checks

| Check | Result |
|---|---|
| Python tests | 126 passed |
| Plugin and bundle tests | 13 passed |
| Codex skills | both valid |
| Ruff lint and format | passed |
| TypeScript and Wrangler checks | passed |
| Main Worker dry run | passed |
| Remote MCP Worker dry run | passed |

## Commercial flow

- `/v1/offers` returned both products with current prices and plans.
- ESG activation page identified US$29/month, 100 jobs and 20 organizations.
- AI activation page identified US$99/month, 100 jobs and 20 organizations.
- Neither page contained cross-product pricing.
- Gumroad remains licensed and public for both products.
- Contract tests reject wrong-product API keys before upload.

## Production and cross-client trials

- Five scripted production roles passed.
- ESG review extracted one commitment.
- General AI review returned 28 controls.
- Insurance review returned 30 controls.
- Evidence-pack review returned four artifacts and eight proposals.
- Wrong-product key rejection passed.
- Claude Code registered both local stdio servers and reported `Connected`.
- Claude Code was also checked from a fresh clone of the public GitHub
  repository; both product entries reported `Connected`.
- Remote MCP `/mcp/esg` and `/mcp/ai` passed initialize and tools/list.
- Remote MCP passed account, purchase options, audit, status, report, evidence
  pack, deletion and plan-isolation tests.
- Claude Code remote HTTP health was not verified because the local Claude
  account is not logged in; it is not claimed as supported.
- Hermes and WorkBuddy are templates only and are not claimed as supported.

## Temporary data cleanup

- All temporary organizations, API keys, jobs and founding seats were deleted.
- The AI founding-seat table returned to zero occupied test seats.
- Test API-key files were removed from the private local directory.

## Remaining release gates

- Push and test the Git-backed Codex marketplace upgrade: passed.
- Register and test Claude Code stdio from the published repository revision:
  passed.
- Publish the GitHub `v0.6.0` tag and release.
- Recruit three to five external human pilot users before claiming
  market-validated GA.
- Independently review privacy, terms and refund language.
