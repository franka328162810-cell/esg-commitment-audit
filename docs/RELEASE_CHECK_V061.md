# v0.6.1 release check

Date: 2026-11-24 (Asia/Shanghai)

Status: production deployed and validated. This patch corrects release
engineering and marketing assets. External human pilots and independent legal
review remain open gates for market-validated GA.

## Versions and artifacts

| Item | Verified value |
|---|---|
| Python package | `0.6.1` |
| Codex plugins | `0.6.1` |
| Worker health version | `0.6.1` |
| Main Worker version | `66eedfe6-3bd3-4291-9a74-6fc8b0ef3f5a` |
| Remote MCP Worker version | `5470db1a-baad-4fd8-bc90-3fb37118dc55` |
| Container image | `0.6.0-r2` unchanged |
| Container digest | `sha256:9d78173f8bf0caa53ce9d3151f7ca2beac24e864f35e1ebc2fe5860ed87dd9f4` |
| Wheel SHA-256 | `00638418d00c1b174609f55eaed0c8f6238e217318f3d8aacbfdec82892e226c` |
| Shared MCP core SHA-256 | `d93683a0c3790416c6bf45571dbd762e79ae300ab18f9075882ecfdcfc9ab934` |

## Automated checks

| Check | Result |
|---|---|
| Python tests | 129 passed |
| Plugin and bundle tests | 13 passed |
| Codex skills | both valid |
| Ruff lint and format | passed across `src`, `tests`, `validation`, `scripts` |
| TypeScript and Wrangler types | passed |
| Main Worker dry run | passed |
| Remote MCP Worker dry run | passed |
| Frozen ESG quality gate | all gate fields passed |

The frozen ESG quality gate retained 98.63% candidate precision, 93.75%
unique-commitment recall, 100% top-level category accuracy and 100% page
citation coverage.

## Production checks

- `/v1/health` returned HTTP `200` with version `0.6.1`.
- Remote MCP root returned version `0.6.1`.
- Remote MCP `initialize` returned protocol `2025-06-18` and server version
  `0.6.1`.
- Remote MCP `tools/list` returned the AI product tools, including
  `audit_evidence_pack`.
- `/v1/offers` retained ESG at US$29/month and AI at US$99/month, each with
  100 monthly jobs and a 20-organization founding cap.
- No database migration or audit-rule change was introduced.

## ESG Gumroad assets

The public ESG product now uses the corrected assets:

| Asset | Public file |
|---|---|
| Cover | `https://public-files.gumroad.com/8h6kbx6xx764ubmi0wra3t8y9f1t` |
| Thumbnail | `https://public-files.gumroad.com/hqdpieua1nz3ikw09zhrmc6z53mp` |

Both downloaded public images were visually checked. They show
`ESG · HOSTED API` and contain no `ICS` product label.

The public Gumroad payload retained:

- `is_licensed: true`;
- monthly price `2900` US cents;
- 20 remaining founding seats.

## CI repair

- The workflow now runs the existing
  `plugins/core/server.test.mjs` and `plugins/core/bundles.test.mjs`.
- The previous nonexistent `plugin/server.test.mjs` path is gone.
- CI now checks `scripts/` with Ruff.
- Production health now rejects a Worker that does not report `0.6.1`.

## Remaining release gates

- Recruit three to five external human pilot users before claiming
  market-validated GA.
- Independently review privacy, terms and refund language.
- Claude Code remote HTTP health remains unverified.
- Hermes and WorkBuddy remain templates and are not claimed as supported.
