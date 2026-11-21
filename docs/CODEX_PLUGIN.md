# Codex plugin

## Included structure

```text
.codex-plugin/plugin.json
.mcp.json
assets/icon.svg
skills/ics-commitment-audit/SKILL.md
skills/ics-commitment-audit/agents/openai.yaml
```

The plugin combines a Codex skill with a local MCP server implemented by
`ics_commitment_audit.mcp_server`.

## Prerequisites

Install the Python package and its dependencies:

```powershell
python -m pip install -e .
```

Verify the MCP entry point:

```powershell
ics-crv-mcp
```

The command waits for newline-delimited MCP JSON-RPC messages on standard input.

## Local tools

- `audit_local_document`: audit a local PDF, DOCX, TXT, or Markdown file without
  uploading it.
- `audit_text`: audit pasted commitment text.

## Hosted tools

Set:

```powershell
$env:ICS_AUDIT_API_URL = "https://audit.example.com"
$env:ICS_AUDIT_API_KEY = "ics_live_..."
```

Then these tools become usable:

- `submit_cloud_audit`
- `get_cloud_audit`

Cloud submission is set to `approval_mode: prompt` in `.mcp.json`. The skill also
requires the user to explicitly request hosted processing before uploading.

## Validation

```powershell
python 'C:\Users\Administrator\.codex\skills\.system\skill-creator\scripts\quick_validate.py' skills\ics-commitment-audit
python -m pytest tests\test_mcp.py
```

## Marketplace publication

Before submitting the repository to a Codex marketplace:

1. add the final GitHub repository URL and support/privacy/terms URLs to
   `.codex-plugin/plugin.json`;
2. verify install from a clean machine using the documented Python prerequisite;
3. confirm that the plugin icon and description render correctly;
4. publish a tagged release;
5. keep local-only mode functional without any paid API key.

The plugin does not embed a bypassable entitlement check. Paid quota enforcement
belongs to the hosted service.
