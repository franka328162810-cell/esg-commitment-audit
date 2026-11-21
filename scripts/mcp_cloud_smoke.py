from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

from ics_commitment_audit.mcp_server import call_tool


def result_content(result: dict[str, Any]) -> dict[str, Any]:
    if result.get("isError"):
        raise RuntimeError(result)
    value = result.get("structuredContent")
    if not isinstance(value, dict):
        raise TypeError("MCP tool did not return structured content")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-url",
        default="https://ics-commitment-audit-api.franka328162810.workers.dev",
    )
    parser.add_argument("--api-key-file", type=Path, required=True)
    parser.add_argument("--document", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    api_key = str(json.loads(args.api_key_file.read_text(encoding="utf-8"))["api_key"])
    os.environ["ICS_AUDIT_API_URL"] = args.base_url
    os.environ["ICS_AUDIT_API_KEY"] = api_key

    submitted = result_content(
        call_tool(
            "submit_cloud_audit",
            {"path": str(args.document.resolve()), "weights": "default"},
        )
    )
    job_id = str(submitted["id"])
    deadline = time.time() + args.timeout
    status = submitted
    while time.time() < deadline:
        time.sleep(4)
        status = result_content(
            call_tool(
                "get_cloud_audit",
                {"job_id": job_id, "include_report": False},
            )
        )
        if status.get("status") in {"completed", "failed", "cancelled"}:
            break
    if status.get("status") != "completed":
        raise RuntimeError(f"Cloud audit did not complete: {status}")

    completed = result_content(
        call_tool(
            "get_cloud_audit",
            {"job_id": job_id, "include_report": True},
        )
    )
    report = completed["report"]
    evidence_count = sum(
        1 for commitment in report["commitments"] if commitment.get("evidence")
    )
    summary = {
        "job_id": job_id,
        "status": status["status"],
        "attempts": status.get("attempts"),
        "report_version": report["report_version"],
        "commitment_count": len(report["commitments"]),
        "evidence_count": evidence_count,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
