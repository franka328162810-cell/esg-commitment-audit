# ESG and AI audit tools v0.6.1

Historical record. Superseded by `docs/PLUGIN_RELEASE_NOTES_V062.md`.

This patch corrects the public ESG image assets and repairs the release
engineering checks. The audit rules and report formats are unchanged.

## Changes

- The ESG Gumroad cover and thumbnail now use `ESG` rather than an `ICS`
  product label.
- GitHub CI now runs the shared plugin core and bundle tests from their actual
  path under `plugins/core/`.
- Ruff lint and format checks now include `scripts/`.
- The Python package, both Codex plugins, hosted API and remote MCP Worker
  report version `0.6.1`.
- The production health workflow rejects a deployment that does not report
  version `0.6.1`.

## Compatibility

- Historical JSON report schema versions remain `0.6.0`.
- The container runtime remains `0.6.0-r2` because no hosted audit logic
  changed in this patch.
- The existing ESG and AI purchase, activation and API-key flows are unchanged.
- The two Codex plugin entries continue to share one byte-identical MCP core.

## Install

```powershell
codex plugin marketplace add franka328162810-cell/esg-commitment-audit --ref main
codex plugin add esg-commitment-audit@ics-tec
codex plugin add ai-alignment-revisability-audit@ics-tec
```

The plugins are free. Hosted audits require the matching activated API key.

## Claims boundary

These products review written commitments, policies and submitted evidence.
They do not certify ESG performance, AI safety, legal compliance, assurance or
the truth of an organization's claims.
