from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from esg_commitment_audit.api import audit_revisability_version_bytes
from esg_commitment_audit.revisability_models import EvidenceGrade
from esg_commitment_audit.revisability_version_report import (
    render_version_trace_html,
    render_version_trace_json,
    render_version_trace_markdown,
)
from esg_commitment_audit.web import app

client = TestClient(app)


def _version_report():
    previous = Path("examples/revisability_policy_v1.md").read_bytes()
    current = Path("examples/revisability_policy_v2.md").read_bytes()
    return audit_revisability_version_bytes(
        previous,
        "policy-v1.md",
        current,
        "policy-v2.md",
    )


def test_version_trace_detects_regressions_and_new_warning() -> None:
    report = _version_report()
    changes = {change.key: change for change in report.check_changes}

    assert report.summary.regressed_count >= 4
    assert report.summary.high_materiality_count >= 3
    assert changes["review_cadence"].direction == "regressed"
    assert changes["review_cadence"].previous_grade == EvidenceGrade.DOCUMENTED
    assert changes["review_cadence"].current_grade == EvidenceGrade.ASSERTED
    assert changes["notice"].current_grade == EvidenceGrade.CONTRADICTED
    assert any("without notice" in warning for warning in report.new_warnings)


def test_version_trace_detects_added_removed_and_modified_statements() -> None:
    report = _version_report()
    types = {change.change_type for change in report.statement_changes}

    assert report.summary.added_statement_count >= 1
    assert report.summary.removed_statement_count >= 1
    assert "added" in types
    assert "removed" in types


def test_version_trace_pairs_near_identical_statement_as_modified() -> None:
    report = audit_revisability_version_bytes(
        b"Users may appeal and request independent human review.",
        "v1.txt",
        b"Users may appeal and request internal human review.",
        "v2.txt",
    )

    assert report.summary.modified_statement_count == 1
    modified = next(
        change
        for change in report.statement_changes
        if change.change_type == "modified"
    )
    assert modified.similarity is not None
    assert modified.similarity >= 0.82


def test_version_trace_renderers_include_materiality_and_boundary() -> None:
    report = _version_report()
    markdown = render_version_trace_markdown(report)
    html = render_version_trace_html(report)
    payload = json.loads(render_version_trace_json(report))

    assert "## Material check changes" in markdown
    assert "High-materiality regressions" in markdown
    assert "AI Alignment Revisability Version Trace" in html
    assert "Claim boundary" in html
    assert payload["report_type"] == "ai-revisability-version-trace"
    assert payload["previous"]["document"]["filename"] == "policy-v1.md"
    assert payload["current"]["document"]["filename"] == "policy-v2.md"


def test_version_trace_web_page_and_endpoint() -> None:
    page = client.get("/revisability/versions")
    response = client.post(
        "/api/revisability-version",
        files={
            "previous_file": (
                "policy-v1.txt",
                Path("examples/revisability_policy_v1.md").read_bytes(),
                "text/markdown",
            ),
            "current_file": (
                "policy-v2.txt",
                Path("examples/revisability_policy_v2.md").read_bytes(),
                "text/markdown",
            ),
        },
        data={"profile": "general"},
    )

    assert page.status_code == 200
    assert "AI Revisability Version Trace" in page.text
    assert response.status_code == 200
    payload = response.json()
    assert payload["report"]["report_type"] == "ai-revisability-version-trace"
    assert payload["report"]["summary"]["regressed_count"] >= 4
    assert "AI Alignment Revisability Version Trace" in payload["html"]
