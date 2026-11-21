from __future__ import annotations

import json
from pathlib import Path

from ics_commitment_audit.mcp_server import handle_message


def test_mcp_initialize_and_tools_list() -> None:
    initialized = handle_message(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2025-06-18"},
        }
    )
    assert initialized is not None
    assert initialized["result"]["serverInfo"]["name"] == "ics-commitment-audit"

    listed = handle_message({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    assert listed is not None
    names = {tool["name"] for tool in listed["result"]["tools"]}
    assert {
        "audit_local_document",
        "audit_text",
        "submit_cloud_audit",
        "get_cloud_audit",
    } <= names


def test_mcp_audit_text_tool_returns_structured_report() -> None:
    response = handle_message(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "audit_text",
                "arguments": {
                    "text": "公司承诺到2030年将碳排放减少50%。",
                },
            },
        }
    )
    assert response is not None
    assert response["result"]["isError"] is False
    report = response["result"]["structuredContent"]
    assert report["summary"]["commitment_count"] == 1
    assert report["commitments"][0]["evidence"]["excerpt"]


def test_plugin_manifest_and_mcp_config_are_consistent() -> None:
    plugin = json.loads(Path(".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    mcp = json.loads(Path(".mcp.json").read_text(encoding="utf-8"))

    assert plugin["name"] == "ics-commitment-audit"
    assert plugin["skills"] == "./skills/"
    assert plugin["mcpServers"] == "./.mcp.json"
    assert "ics-commitment-audit" in mcp["mcpServers"]
