from __future__ import annotations

import json
from pathlib import Path

from ics_commitment_audit.api import audit_bytes
from ics_commitment_audit.report import render_html, render_json, render_markdown


def _sample_report():
    return audit_bytes(
        Path("examples/strong_commitment.txt").read_bytes(),
        "strong_commitment.txt",
    )


def test_markdown_report_contains_evidence_and_disclaimer() -> None:
    markdown = render_markdown(_sample_report())
    assert "# ICS Commitment Audit Report" in markdown
    assert "## Disclaimer" in markdown
    assert "not a legal opinion" in markdown
    assert "V_obs" in markdown


def test_json_report_round_trips() -> None:
    rendered = render_json(_sample_report())
    data = json.loads(rendered)
    assert data["report_version"] == "0.2.0"
    assert data["document"]["filename"] == "strong_commitment.txt"
    assert data["commitments"]


def test_html_report_is_standalone_and_escapes_input() -> None:
    report = audit_bytes(
        "公司承诺到2030年减少碳排放50%<script>alert(1)</script>。".encode(),
        "unsafe.txt",
    )
    html = render_html(report)
    assert "<!doctype html>" in html
    assert "ICS-TEC" in html
    assert "https://" not in html
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html
