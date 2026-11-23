# Codex plugin GA trials

Date: 2026-11-24

Plugin version: `0.5.0`

## Test basis

The trials used the two installed plugin packages from an isolated `CODEX_HOME`
and called the production Cloudflare API through each package's MCP server.
Temporary API keys were created through the administrative endpoint and deleted
after the trials. Every generated job was deleted through the plugin before the
temporary organizations were removed.

These are five scripted user-role trials with real production requests. They are
not independent external human customers.

## Results

| User role | Workflow | Observed result | Status |
|---|---|---|---|
| ESG sustainability analyst | Account preflight and hosted commitment review | `founding-team`; one commitment extracted; report completed | Passed |
| AI policy lead | General AI policy review | 28 controls across the standard dimensions | Passed |
| Insurance governance reviewer | `insurance` industry profile | 30 controls, including the two profile safeguards | Passed |
| AI evidence manager | Sealed evidence-pack ZIP | Four artifacts, eight promotion proposals, report completed | Passed |
| Misconfigured ESG key user | AI plugin with an ESG key | Rejected before upload with plan, allowed-mode, and activation guidance | Passed |

## Lifecycle checks

| Check | Result |
|---|---|
| Marketplace lists two independent `0.5.0` plugins | Passed |
| Install ESG and AI plugins separately | Passed |
| Both installed packages remain enabled simultaneously | Passed |
| Bundled `server.mjs` files share one SHA-256 hash | Passed |
| Upload and deletion approval rules present | Passed |
| Missing API key returns activation guidance | Passed |
| Uninstall each plugin | Passed |
| Reinstall each plugin | Passed |
| Upgrade from the public `0.4.0-dev.2` ESG package | Passed; installed entry refreshed to `0.5.0` |
| Install AI entry from Git-backed Marketplace | Passed |

## Required final gate

Technical release gate:

1. Push the two-plugin Marketplace definition to GitHub: passed.
2. Upgrade the isolated old installation with
   `codex plugin marketplace upgrade`: passed.
3. Verify the old ESG entry becomes `0.5.0` and the AI entry becomes
   available: passed.
4. Install and use the AI entry from the Git-backed Marketplace: passed.
5. Publish the `v0.5.0` plugin release: performed after this record.
6. Obtain three to five external human pilot accounts before claiming
   market-validated GA: still required.

The internal role trials establish technical readiness. They do not substitute
for independent customer feedback. The release can be published as a technical
GA candidate, but market validation should not be claimed until external pilot
accounts are completed.
