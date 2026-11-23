from __future__ import annotations

import json
from pathlib import Path

import pytest

from esg_commitment_audit import __version__, mcp_server
from esg_commitment_audit.mcp_server import handle_message


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
    assert initialized["result"]["serverInfo"]["name"] == "esg-commitment-audit"

    listed = handle_message({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    assert listed is not None
    names = {tool["name"] for tool in listed["result"]["tools"]}
    assert {
        "audit_local_document",
        "audit_text",
        "audit_revisability_document",
        "audit_revisability_text",
        "audit_revisability_version",
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


def test_mcp_revisability_text_tool_returns_evidence_grades() -> None:
    response = handle_message(
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "audit_revisability_text",
                "arguments": {
                    "text": (
                        "The policy is reviewed annually. Users may appeal and "
                        "exit the service."
                    ),
                    "profile": "general",
                },
            },
        }
    )
    assert response is not None
    assert response["result"]["isError"] is False
    report = response["result"]["structuredContent"]
    assert report["report_type"] == "ai-alignment-revisability"
    assert report["summary"]["check_count"] == 28
    assert report["summary"]["documented_count"] >= 3


def test_mcp_revisability_version_tool_returns_check_movement() -> None:
    response = handle_message(
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "audit_revisability_version",
                "arguments": {
                    "previous_path": "examples/revisability_policy_v1.md",
                    "current_path": "examples/revisability_policy_v2.md",
                    "profile": "general",
                },
            },
        }
    )
    assert response is not None
    assert response["result"]["isError"] is False
    report = response["result"]["structuredContent"]
    assert report["report_type"] == "ai-revisability-version-trace"
    assert report["summary"]["regressed_count"] >= 4


def test_plugin_manifest_and_mcp_config_are_consistent() -> None:
    development_plugin = json.loads(
        Path(".codex-plugin/plugin.json").read_text(encoding="utf-8")
    )
    development_mcp = json.loads(Path(".mcp.json").read_text(encoding="utf-8"))
    marketplace = json.loads(
        Path(".agents/plugins/marketplace.json").read_text(encoding="utf-8")
    )

    assert development_plugin["name"] == "esg-commitment-audit"
    assert development_plugin["skills"] == "./skills/"
    assert development_plugin["mcpServers"] == "./.mcp.json"
    assert "esg-commitment-audit" in development_mcp["mcpServers"]
    assert marketplace["name"] == "ics-tec"
    assert [plugin["name"] for plugin in marketplace["plugins"]] == [
        "esg-commitment-audit",
        "ai-alignment-revisability-audit",
    ]

    for entry in marketplace["plugins"]:
        plugin_root = Path(entry["source"]["path"])
        manifest = json.loads(
            (plugin_root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        mcp = json.loads((plugin_root / ".mcp.json").read_text(encoding="utf-8"))
        assert manifest["name"] == entry["name"]
        assert manifest["version"] == "0.5.0"
        assert mcp["mcpServers"][entry["name"]]["command"] == "node"
        assert (plugin_root / "server.mjs").is_file()


def test_mcp_cloud_submission_uses_streamable_worker_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report = tmp_path / "report.txt"
    report.write_text("We commit to net zero by 2040.", encoding="utf-8")
    monkeypatch.setenv("ESG_AUDIT_API_URL", "https://audit.example.com")
    monkeypatch.setenv("ESG_AUDIT_API_KEY", "esg_live_test")
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
    assert captured["extra_headers"]["X-ESG-Filename"] == "report.txt"


def test_mcp_cloud_request_sets_product_user_agent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ESG_AUDIT_API_URL", "https://audit.example.com")
    monkeypatch.setenv("ESG_AUDIT_API_KEY", "esg_live_test")
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
    assert request.get_header("User-agent") == f"esg-commitment-audit-mcp/{__version__}"
