# ESG Commitment Audit plugin

This marketplace bundle contains a dependency-free Node MCP client for the ICS
hosted audit API.

Requirements:

- a trial or paid `ESG_AUDIT_API_KEY`;
- network access to the hosted HTTPS API.

Set `ESG_AUDIT_API_KEY` in the Codex environment before enabling the plugin.
The key is read at runtime and is not stored in this bundle.

The hosted API deletes source uploads after success or final failure. Reports
expire after seven days. Do not upload documents you are not authorized to
process.
