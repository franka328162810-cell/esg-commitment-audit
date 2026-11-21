from __future__ import annotations

import argparse
import io
import json
import math
import os
import statistics
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from docx import Document


@dataclass(frozen=True)
class Sample:
    name: str
    content_type: str
    data: bytes


def minimal_pdf(text: str) -> bytes:
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = f"BT /F1 12 Tf 72 720 Td ({escaped}) Tj ET".encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>"
        ),
        b"<< /Length "
        + str(len(stream)).encode()
        + b" >>\nstream\n"
        + stream
        + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for index, body in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{index} 0 obj\n".encode())
        output.extend(body)
        output.extend(b"\nendobj\n")
    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode())
    output.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode()
    )
    return bytes(output)


def docx_bytes() -> bytes:
    buffer = io.BytesIO()
    document = Document()
    document.add_heading("Climate commitments", level=1)
    document.add_paragraph(
        "We commit to reduce absolute Scope 1 and Scope 2 emissions by 50% "
        "by 2030 against a 2022 baseline."
    )
    table = document.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "Review"
    table.cell(0, 1).text = "The target is reviewed annually by the board."
    document.save(buffer)
    return buffer.getvalue()


def sample_documents() -> list[Sample]:
    return [
        Sample(
            "load_text.txt",
            "text/plain; charset=utf-8",
            (
                "环境\n\n公司承诺到2030年将范围1和范围2碳排放较2022年减少50%，"
                "并由董事会每年复核执行进展。\n"
            ).encode(),
        ),
        Sample(
            "load_report.docx",
            ("application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
            docx_bytes(),
        ),
        Sample(
            "load_report.pdf",
            "application/pdf",
            minimal_pdf("We commit to net zero by 2040 and review progress annually."),
        ),
    ]


def request(
    base_url: str,
    api_key: str,
    method: str,
    path: str,
    *,
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, dict[str, Any], float]:
    request_headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "User-Agent": "ics-commitment-audit-cloud-smoke/0.2.0",
    }
    if headers:
        request_headers.update(headers)
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}{path}",
        data=data,
        method=method,
        headers=request_headers,
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            raw = response.read()
            status = response.status
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        status = exc.code
    elapsed_ms = (time.perf_counter() - started) * 1000
    text = raw.decode("utf-8", errors="replace")
    try:
        payload = json.loads(text) if text else {}
    except json.JSONDecodeError:
        payload = {"raw": text[:500]}
    return status, payload, elapsed_ms


def audit_sample(base_url: str, api_key: str, sample: Sample) -> dict[str, Any]:
    status, submitted, submit_ms = request(
        base_url,
        api_key,
        "POST",
        "/v1/audits",
        data=sample.data,
        headers={
            "Content-Type": sample.content_type,
            "X-ICS-Filename": sample.name,
            "X-ICS-Weights": "default",
        },
    )
    if status != 202:
        return {
            "sample": sample.name,
            "ok": False,
            "submit_status": status,
            "submit_ms": round(submit_ms, 2),
            "error": submitted.get("error", submitted),
        }
    job_id = str(submitted["id"])
    started = time.perf_counter()
    job: dict[str, Any] = {}
    while time.perf_counter() - started < 300:
        status, job, _ = request(base_url, api_key, "GET", f"/v1/audits/{job_id}")
        if status != 200:
            break
        if job.get("status") in {"completed", "failed", "cancelled"}:
            break
        time.sleep(2)
    total_ms = submit_ms + (time.perf_counter() - started) * 1000
    report_ok = False
    if job.get("status") == "completed":
        report_status, report, _ = request(
            base_url,
            api_key,
            "GET",
            f"/v1/audits/{job_id}/report",
        )
        report_ok = report_status == 200 and isinstance(report.get("commitments"), list)
    return {
        "sample": sample.name,
        "ok": job.get("status") == "completed" and report_ok,
        "job_id": job_id,
        "status": job.get("status"),
        "attempts": job.get("attempts"),
        "submit_ms": round(submit_ms, 2),
        "end_to_end_ms": round(total_ms, 2),
        "report_ok": report_ok,
        "error": job.get("error"),
    }


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, math.ceil(fraction * len(ordered)) - 1)
    return ordered[index]


def health_probe(base_url: str, api_key: str) -> dict[str, Any]:
    status, payload, latency_ms = request(base_url, api_key, "GET", "/v1/health")
    return {"status": status, "latency_ms": latency_ms, "payload": payload}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-url",
        default="https://ics-commitment-audit-api.franka328162810.workers.dev",
    )
    parser.add_argument("--api-key-file", type=Path)
    parser.add_argument("--health-requests", type=int, default=30)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    api_key = os.environ.get("ICS_AUDIT_API_KEY", "")
    if not api_key and args.api_key_file:
        api_key = str(
            json.loads(args.api_key_file.read_text(encoding="utf-8"))["api_key"]
        )
    if not api_key:
        raise SystemExit("Set ICS_AUDIT_API_KEY or pass --api-key-file")

    def timed_health() -> dict[str, Any]:
        return health_probe(args.base_url, api_key)

    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=min(10, args.health_requests)) as pool:
        health = list(pool.map(lambda _: timed_health(), range(args.health_requests)))
    health_wall_ms = (time.perf_counter() - started) * 1000

    samples = sample_documents()

    with ThreadPoolExecutor(max_workers=len(samples)) as pool:
        audits = list(
            pool.map(
                lambda sample: audit_sample(args.base_url, api_key, sample), samples
            )
        )

    health_latencies = [item["latency_ms"] for item in health]
    audit_latencies = [
        float(item["end_to_end_ms"])
        for item in audits
        if isinstance(item.get("end_to_end_ms"), (int, float))
    ]
    result = {
        "service": args.base_url,
        "health": {
            "requests": len(health),
            "successes": sum(item["status"] == 200 for item in health),
            "wall_ms": round(health_wall_ms, 2),
            "p50_ms": round(statistics.median(health_latencies), 2),
            "p95_ms": round(percentile(health_latencies, 0.95), 2),
        },
        "audits": {
            "submitted": len(audits),
            "successes": sum(item["ok"] for item in audits),
            "p50_end_to_end_ms": round(statistics.median(audit_latencies), 2)
            if audit_latencies
            else 0,
            "p95_end_to_end_ms": round(percentile(audit_latencies, 0.95), 2)
            if audit_latencies
            else 0,
            "results": audits,
        },
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if result["audits"]["successes"] == len(audits) else 1


if __name__ == "__main__":
    raise SystemExit(main())
