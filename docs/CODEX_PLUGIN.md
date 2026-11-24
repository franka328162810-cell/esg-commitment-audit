# Codex plugin GA

Plugin release: `0.6.2`

## Product entries

The ICS marketplace publishes two independent plugin entries:

| Plugin | Hosted plan | Monthly limit |
|---|---|---:|
| `ai-alignment-revisability-audit` | US$99 AI plan | 100 jobs |
| `esg-commitment-audit` | US$29 ESG plan | 100 jobs |

Both plugin packages are free. Only the hosted service requires a paid or
administrative API key.

## Shared core

The canonical MCP implementation is:

```text
plugins/core/server.mjs
```

`scripts/sync_plugin_core.mjs` copies that file into both self-contained plugin
packages. This keeps marketplace installation independent while preventing the
two products from drifting into separate implementations. An automated test
confirms that both bundled copies have the same SHA-256 hash as the canonical
file.

Product-specific behavior is selected by `ICS_PRODUCT=esg` or
`ICS_PRODUCT=ai` in each `.mcp.json`.

## Installation

```powershell
codex plugin marketplace add franka328162810-cell/esg-commitment-audit --ref main
codex plugin add ai-alignment-revisability-audit@ics-tec
codex plugin add esg-commitment-audit@ics-tec
```

Other lifecycle commands:

```powershell
codex plugin marketplace upgrade ics-tec
codex plugin list --available --json
codex plugin remove esg-commitment-audit@ics-tec
codex plugin remove ai-alignment-revisability-audit@ics-tec
codex plugin marketplace remove ics-tec
```

## API-key setup

The canonical environment variable is:

```powershell
$env:ICS_AUDIT_API_KEY = "<matching API key>"
```

`ESG_AUDIT_API_KEY` remains accepted for existing installations. Optional
overrides:

```powershell
$env:ICS_AUDIT_API_URL = "https://esg-commitment-audit-api.franka328162810.workers.dev"
```

Obtain a key through the matching activation page:

- ESG: `/activate`
- AI: `/ai-revisability-audit/activate`

The plugin calls `get_account` before an uploaded review. If the account does
not expose the required mode, the plugin returns the current plan, allowed
modes, and the correct activation page without uploading the file.

## Tools

Shared:

- `get_purchase_options`
- `audit_document`
- `audit_text`
- `get_cloud_audit`
- `get_account`
- `delete_cloud_audit`

AI-only:

- `audit_evidence_pack`

The AI policy tool accepts the `general`, `news_media`, `advertising`,
`insurance`, and `industrial_design` profiles. Evidence-pack review accepts a
ZIP up to 100 MB compressed; the service enforces the 200 MB uncompressed limit.

## Permissions and approvals

Both plugin manifests declare `Read` and `Write` capabilities.

The following MCP tools use `approval_mode: prompt`:

- document or text upload;
- evidence-pack upload;
- cloud job deletion.

Read-only status and account calls do not require an extra MCP approval. The
skill must still state the exact file, destination, source deletion and report
retention before the first hosted upload. No plugin-level entitlement bypass
exists; quota and plan enforcement remain server-side.

## Error recovery

The shared core maps the hosted API statuses to actionable guidance:

| Status | Recovery |
|---|---|
| `401` | Issue a valid key at the matching activation page |
| `403` | Correct product, inactive subscription, cancellation or refund |
| `409` | Query current account or job state before retrying |
| `413` | Reduce document, page count or ZIP size |
| `415` | Use a supported text-layer document |
| `429` | Wait for the next monthly period or upgrade |
| `503` | Check recent jobs before retrying |

GET requests use bounded retries. Uploads are never retried automatically
because the first request may already have created a billable job. A failed
upload response explicitly tells the user that the outcome is uncertain.

## Validation

```powershell
node --test plugins\core\server.test.mjs plugins\core\bundles.test.mjs
.\.venv\Scripts\python.exe "C:\Users\Administrator\.codex\skills\.system\skill-creator\scripts\quick_validate.py" plugins\ai-alignment-revisability-audit\skills\ai-alignment-revisability-audit
.\.venv\Scripts\python.exe "C:\Users\Administrator\.codex\skills\.system\skill-creator\scripts\quick_validate.py" plugins\esg-commitment-audit\skills\esg-commitment-audit
```

GA lifecycle verification must cover:

1. fresh marketplace add;
2. fresh install of both plugins;
3. upgrade from the previous plugin version;
4. uninstall and reinstall;
5. missing, wrong-product and valid API keys;
6. AI general and insurance-profile review;
7. AI evidence-pack review;
8. ESG document review;
9. upload and deletion approval policy;
10. three to five scripted user-role trials.

## Claims boundary

The plugins are clients for document and evidence review. They do not certify
AI safety, legal compliance, assurance, model alignment, or the truthfulness of
an organization's ESG claims.
