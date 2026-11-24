# v0.6.2 release check

Date: 2026-11-24 (Asia/Shanghai)

Status: production deployed and validated. This release changes product
presentation and catalog order only. External human pilots and independent
legal review remain open gates for market-validated GA.

## Versions and artifacts

| Item | Verified value |
|---|---|
| Python package | `0.6.2` |
| Codex plugins | `0.6.2` |
| Worker health version | `0.6.2` |
| Main Worker version | `d801e10f-9af3-4b6e-9379-8346640feeb7` |
| Remote MCP Worker version | `545796de-b41f-4e11-b78e-211ea80f3d4f` |
| Container image | `0.6.0-r2` unchanged |
| Wheel SHA-256 | `489f3724f9813ee2986e990730a41cc6e7cbeebadba58fbd66e666fe85020198` |

## Product presentation

- AI Alignment Revisability Audit is first in the Codex marketplace, public
  landing page, offers API, workbench and repository README.
- ESG Commitment Audit remains a separate plugin and product section.
- Each plugin ships a distinct cover and thumbnail.
- Each plugin has its own homepage, product description and README.
- The offers API returns `ai` before `esg`.
- The workbench presents AI policy review, AI evidence-pack review and ESG
  review in that order, with AI policy review selected by default.

## Plugin asset verification

| Product | Cover | Thumbnail |
|---|---|---|
| AI Alignment Revisability Audit | `plugins/ai-alignment-revisability-audit/assets/cover.png` | `plugins/ai-alignment-revisability-audit/assets/thumbnail.png` |
| ESG Commitment Audit | `plugins/esg-commitment-audit/assets/cover.png` | `plugins/esg-commitment-audit/assets/thumbnail.png` |

The AI and ESG cover hashes differ. The same is true for their thumbnails. Both
plugin manifests declare both files under `interface.screenshots`.

## Automated checks

| Check | Result |
|---|---|
| Python tests | 130 passed |
| Plugin and bundle tests | 14 passed |
| Codex skills | both valid |
| Ruff lint and format | passed |
| TypeScript and Wrangler types | passed |
| Main Worker dry run | passed |
| Remote MCP Worker dry run | passed |

The plugin tests verify:

- exact marketplace order: AI first, ESG second;
- two independent plugin entries;
- product-specific homepage and screenshots;
- separate cover and thumbnail hashes;
- byte-identical shared MCP core;
- product-specific upload and evidence-pack permissions.

## Production checks

- `/v1/health` returned version `0.6.2`.
- The public root title is `ICS Audit Tools | AI and ESG Evidence Workbench`.
- The landing page places AI before ESG.
- `/v1/offers` returned products in `ai,esg` order.
- `/workspace` places AI policy, AI evidence-pack and ESG modes in that order.
- `/workspace` selects AI policy review by default.
- Remote MCP root returned `/mcp/ai` before `/mcp/esg`.
- Remote MCP `initialize` on `/mcp/ai` returned version `0.6.2`.

## Compatibility

- Audit rules are unchanged.
- JSON report schema remains `0.6.0`.
- The container runtime remains `0.6.0-r2`.
- Existing ESG and AI plans, prices, quotas and API-key prefixes are unchanged.

## Remaining release gates

- Recruit three to five external human pilot users before claiming
  market-validated GA.
- Independently review privacy, terms and refund language.
- Claude Code remote HTTP health remains unverified.
- Hermes and WorkBuddy remain templates and are not claimed as supported.
