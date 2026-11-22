from __future__ import annotations

import json
from pathlib import Path

import pytest

from ics_commitment_audit import mcp_server
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
    marketplace = json.loads(
        Path(".agents/plugins/marketplace.json").read_text(encoding="utf-8")
    )
    bundle = json.loads(
        Path("plugin/.codex-plugin/plugin.json").read_text(encoding="utf-8")
    )
    bundle_mcp = json.loads(Path("plugin/.mcp.json").read_text(encoding="utf-8"))

    assert plugin["name"] == "ics-commitment-audit"
    assert plugin["skills"] == "./skills/"
    assert plugin["mcpServers"] == "./.mcp.json"
    assert "ics-commitment-audit" in mcp["mcpServers"]
    assert marketplace["name"] == "ics-tec"
    assert marketplace["plugins"][0]["source"]["path"] == "./plugin"
    assert bundle["version"] == plugin["version"]
    assert bundle_mcp["mcpServers"]["ics-commitment-audit"]["command"] == "node"
    assert Path("plugin/server.mjs").is_file()


def test_mcp_cloud_submission_uses_streamable_worker_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report = tmp_path / "report.txt"
    report.write_text("We commit to net zero by 2040.", encoding="utf-8")
    monkeypatch.setenv("ICS_AUDIT_API_URL", "https://audit.example.com")
    monkeypatch.setenv("ICS_AUDIT_API_KEY", "ics_live_test")
    captured: dict[str, object] = {}

    def fake_request(method: str, path: str, **kwargs):
        captured.update({"method": method, "path": path, **kwargs})
        return {"id": "job_1", "status": "queued"}

    monkeypatch.setattr(mcp_server, "_cloud_request", fake_request)
    result = mcp_server._submit_cloud(report, "default")

    assert result["id"] == "job_1"
    assert captured["method"] == "POST"
    assert captured["path"] == "/v1/audits"
    assert captured["body"] == report.read_bytes()
    assert captured["content_type"] == "text/plain; charset=utf-8"
    assert captured["extra_headers"]["X-ICS-Filename"] == "report.txt"


def test_mcp_cloud_request_sets_product_user_agent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ICS_AUDIT_API_URL", "https://audit.example.com")
    monkeypatch.setenv("ICS_AUDIT_API_KEY", "ics_live_test")
    captured: dict[str, object] = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self) -> bytes:
            return b'{"status":"ok"}'

    def fake_urlopen(request, timeout: int):
        captured["request"] = request
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(mcp_server.urllib.request, "urlopen", fake_urlopen)
    result = mcp_server._cloud_request("GET", "/v1/account")

    request = captured["request"]
    assert result == {"status": "ok"}
    assert isinstance(request, mcp_server.urllib.request.Request)
    assert request.get_header("User-agent") == "ics-commitment-audit-mcp/0.3.1"
