# ICS Audit Tools v0.6.2 — independent product presentation

This release changes how the two audit products are presented. It does not
change the audit rules or report formats.

## AI Alignment Revisability Audit — first

The AI product is now first in the Codex marketplace, public landing page,
offers API and repository README.

Its dedicated listing explains:

- 28 written AI-governance controls;
- five industry profiles;
- sealed evidence-pack review;
- the 588-decision multi-jurisdiction benchmark;
- the US$99/month founding plan and matching `ai_live_` activation path.

The plugin package now includes its own cover and thumbnail and a standalone
product README.

## ESG Commitment Audit — separate

The ESG product remains a separate plugin with its own:

- cover and thumbnail;
- product README;
- US$29/month founding plan;
- `esg_live_` activation path;
- ESG commitment extraction and CRV methodology.

The repository introduction no longer leads with ESG or presents the AI product
as a subordinate mode.

## Shared infrastructure

The two products still share:

- one byte-identical MCP core;
- the hosted account, quota and tenant controls;
- Codex and Claude Code stdio adapters;
- remote Streamable HTTP transport.

Sharing infrastructure does not merge the products. Plans, API keys, scopes,
activation pages and product language remain isolated.

## Install

AI first:

```powershell
codex plugin marketplace add franka328162810-cell/esg-commitment-audit --ref main
codex plugin add ai-alignment-revisability-audit@ics-tec
```

ESG separately:

```powershell
codex plugin add esg-commitment-audit@ics-tec
```

## Claims boundary

These tools review written governance and commitment structure plus submitted
evidence. They do not certify AI safety, legal compliance, assurance, model
alignment, environmental performance or the truth of an organization's claims.
