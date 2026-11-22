from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from . import __version__
from .api import (
    audit_bytes,
    audit_revisability_bytes,
    audit_revisability_text,
    audit_revisability_version_bytes,
    audit_text,
)
from .ingest import SUPPORTED_EXTENSIONS
from .report import report_to_dict
from .revisability_report import revisability_report_to_dict
from .revisability_version_report import version_trace_report_to_dict

SERVER_NAME = "esg-commitment-audit"
PROTOCOL_VERSION = "2025-06-18"

TOOLS = [
    {
        "name": "audit_local_document",
        "description": (
            "Audit a local PDF, DOCX, TXT, or Markdown ESG/climate report. "
            "Runs entirely on this machine and returns structured CRV evidence."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute local file path"},
                "weights": {
                    "type": "string",
                    "enum": [
                        "default",
                        "obs-priority",
                        "enf-priority",
                        "rev-priority",
                        "esg-balanced",
                    ],
                    "default": "default",
                },
            },
            "required": ["path"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True},
    },
    {
        "name": "audit_text",
        "description": (
            "Audit pasted commitment text locally and return CRV dimensions, "
            "page/paragraph evidence, warnings, and recommendations."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "filename": {"type": "string", "default": "pasted-text.txt"},
                "weights": {"type": "string", "default": "default"},
            },
            "required": ["text"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True},
    },
    {
        "name": "audit_revisability_document",
        "description": (
            "Audit a local AI policy, constitution, model card, or governance "
            "document for written revisability evidence."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute local file path"},
                "profile": {
                    "type": "string",
                    "enum": [
                        "general",
                        "news_media",
                        "advertising",
                        "insurance",
                        "industrial_design",
                    ],
                    "default": "general",
                },
            },
            "required": ["path"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True},
    },
    {
        "name": "audit_revisability_text",
        "description": (
            "Audit pasted AI governance text for alignment-target authority, "
            "revision, version, rollback, oversight, and affected-party evidence."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "filename": {"type": "string", "default": "ai-policy.txt"},
                "profile": {
                    "type": "string",
                    "enum": [
                        "general",
                        "news_media",
                        "advertising",
                        "insurance",
                        "industrial_design",
                    ],
                    "default": "general",
                },
            },
            "required": ["text"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True},
    },
    {
        "name": "audit_revisability_version",
        "description": (
            "Compare two local versions of an AI policy or constitution and "
            "identify evidence-grade movement, new warnings, and clause changes."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "previous_path": {"type": "string"},
                "current_path": {"type": "string"},
                "profile": {
                    "type": "string",
                    "enum": [
                        "general",
                        "news_media",
                        "advertising",
                        "insurance",
                        "industrial_design",
                    ],
                    "default": "general",
                },
            },
            "required": ["previous_path", "current_path"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True},
    },
    {
        "name": "submit_cloud_audit",
        "description": (
            "Upload a local report to an authorized ICS commercial API. "
            "Requires ESG_AUDIT_API_URL and ESG_AUDIT_API_KEY."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "weights": {"type": "string", "default": "default"},
            },
            "required": ["path"],
            "additionalProperties": False,
        },
        "annotations": {"destructiveHint": False},
    },
    {
        "name": "get_cloud_audit",
        "description": (
            "Get the status of an authorized cloud audit job and optionally "
            "fetch its completed JSON report."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "job_id": {"type": "string"},
                "include_report": {"type": "boolean", "default": False},
            },
            "required": ["job_id"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True},
    },
]


def _tool_result(value: Any) -> dict[str, Any]:
    rendered = json.dumps(value, ensure_ascii=False)
    return {
        "content": [{"type": "text", "text": rendered}],
        "structuredContent": value,
        "isError": False,
    }


def _tool_error(message: str) -> dict[str, Any]:
    return {
        "content": [{"type": "text", "text": message}],
        "isError": True,
    }


def _cloud_config() -> tuple[str, str]:
    base_url = os.environ.get("ESG_AUDIT_API_URL", "").rstrip("/")
    api_key = os.environ.get("ESG_AUDIT_API_KEY", "")
    if not base_url or not api_key:
        raise ValueError("ESG_AUDIT_API_URL and ESG_AUDIT_API_KEY are required")
    if not base_url.startswith("https://") and not base_url.startswith(
        "http://127.0.0.1"
    ):
        raise ValueError("Cloud audit URL must use HTTPS or loopback HTTP")
    return base_url, api_key


def _cloud_request(
    method: str,
    path: str,
    *,
    body: bytes | None = None,
    content_type: str | None = None,
    extra_headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    base_url, api_key = _cloud_config()
    request = urllib.request.Request(
        f"{base_url}{path}",
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "User-Agent": f"esg-commitment-audit-mcp/{__version__}",
            **({"Content-Type": content_type} if content_type else {}),
            **(extra_headers or {}),
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ValueError(f"Cloud API returned HTTP {exc.code}: {detail}") from exc


def _submit_cloud(path: Path, weights: str) -> dict[str, Any]:
    base_url, _ = _cloud_config()
    if not path.is_file():
        raise ValueError(f"File not found: {path}")
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {path.suffix}")
    content_types = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".txt": "text/plain; charset=utf-8",
        ".md": "text/markdown; charset=utf-8",
        ".markdown": "text/markdown; charset=utf-8",
    }
    result = _cloud_request(
        "POST",
        "/v1/audits",
        body=path.read_bytes(),
        content_type=content_types[path.suffix.lower()],
        extra_headers={
            "X-ESG-Filename": urllib.parse.quote(path.name),
            "X-ESG-Weights": weights,
        },
    )
    result["api_url"] = base_url
    return result


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "audit_local_document":
        path = Path(arguments["path"])
        if not path.is_file():
            return _tool_error(f"File not found: {path}")
        report = audit_bytes(
            path.read_bytes(),
            path.name,
            weight_preset=str(arguments.get("weights", "default")),
        )
        return _tool_result(report_to_dict(report))
    if name == "audit_text":
        text = str(arguments["text"])
        if not text or len(text) > 2_000_000:
            return _tool_error("Text must contain between 1 and 2,000,000 characters")
        report = audit_text(
            text,
            filename=str(arguments.get("filename", "pasted-text.txt")),
            weight_preset=str(arguments.get("weights", "default")),
        )
        return _tool_result(report_to_dict(report))
    if name == "audit_revisability_document":
        path = Path(arguments["path"])
        if not path.is_file():
            return _tool_error(f"File not found: {path}")
        report = audit_revisability_bytes(
            path.read_bytes(),
            path.name,
            profile=str(arguments.get("profile", "general")),
        )
        return _tool_result(revisability_report_to_dict(report))
    if name == "audit_revisability_text":
        text = str(arguments["text"])
        if not text or len(text) > 2_000_000:
            return _tool_error("Text must contain between 1 and 2,000,000 characters")
        report = audit_revisability_text(
            text,
            filename=str(arguments.get("filename", "ai-policy.txt")),
            profile=str(arguments.get("profile", "general")),
        )
        return _tool_result(revisability_report_to_dict(report))
    if name == "audit_revisability_version":
        previous_path = Path(arguments["previous_path"])
        current_path = Path(arguments["current_path"])
        for path in (previous_path, current_path):
            if not path.is_file():
                return _tool_error(f"File not found: {path}")
        report = audit_revisability_version_bytes(
            previous_path.read_bytes(),
            previous_path.name,
            current_path.read_bytes(),
            current_path.name,
            profile=str(arguments.get("profile", "general")),
        )
        return _tool_result(version_trace_report_to_dict(report))
    if name == "submit_cloud_audit":
        return _tool_result(
            _submit_cloud(
                Path(arguments["path"]),
                str(arguments.get("weights", "default")),
            )
        )
    if name == "get_cloud_audit":
        job_id = str(arguments["job_id"])
        status = _cloud_request("GET", f"/v1/audits/{job_id}")
        if arguments.get("include_report") and status.get("status") == "completed":
            status["report"] = _cloud_request("GET", f"/v1/audits/{job_id}/report")
        return _tool_result(status)
    raise ValueError(f"Unknown tool: {name}")


def _response(request_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }


def handle_message(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    request_id = message.get("id")
    if method == "initialize":
        return _response(
            request_id,
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": SERVER_NAME,
                    "version": __version__,
                },
            },
        )
    if method in {"notifications/initialized", "notifications/cancelled"}:
        return None
    if method == "ping":
        return _response(request_id, {})
    if method == "tools/list":
        return _response(request_id, {"tools": TOOLS})
    if method == "tools/call":
        params = message.get("params") or {}
        name = str(params.get("name", ""))
        arguments = params.get("arguments") or {}
        try:
            return _response(request_id, call_tool(name, arguments))
        except Exception as exc:  # noqa: BLE001 - isolate tool failures from the server loop.
            return _response(request_id, _tool_error(f"{type(exc).__name__}: {exc}"))
    if request_id is None:
        return None
    return _error(request_id, -32601, f"Method not found: {method}")


def main() -> int:
    for raw_message in sys.stdin.buffer:
        if not raw_message.strip():
            continue
        try:
            message = json.loads(raw_message)
        except json.JSONDecodeError as exc:
            response = _error(None, -32700, f"Parse error: {exc}")
        else:
            response = handle_message(message)
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
