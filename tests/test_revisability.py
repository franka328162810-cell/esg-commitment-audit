from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from esg_commitment_audit.api import audit_revisability_text
from esg_commitment_audit.revisability_models import EvidenceGrade
from esg_commitment_audit.revisability_report import (
    render_revisability_html,
    render_revisability_json,
    render_revisability_markdown,
)
from esg_commitment_audit.web import app

client = TestClient(app)


def _all_checks(report):
    return [check for dimension in report.dimensions for check in dimension.checks]


def test_strong_policy_establishes_documented_text_controls() -> None:
    text = Path("examples/revisability_strong_policy.md").read_text(encoding="utf-8")
    report = audit_revisability_text(text)

    assert report.profile == "general"
    assert report.summary.check_count == 28
    assert report.summary.documented_count == 28
    assert report.summary.absent_count == 0
    assert report.summary.asserted_count == 0
    assert report.summary.contradicted_count == 0
    assert all(check.evidence for check in _all_checks(report))


def test_generic_responsible_ai_language_is_asserted_not_documented() -> None:
    report = audit_revisability_text(
        "We follow responsible AI principles and ethical values."
    )
    checks = {check.key: check for check in _all_checks(report)}

    assert checks["alignment_target"].grade == EvidenceGrade.ASSERTED
    assert checks["revision_authority"].grade == EvidenceGrade.ABSENT
    assert report.summary.asserted_count >= 1
    assert report.summary.absent_count > report.summary.documented_count


def test_hard_lock_is_contradicted_and_warned() -> None:
    report = audit_revisability_text(
        "This alignment policy cannot be amended or revised."
    )
    checks = {check.key: check for check in _all_checks(report)}

    assert checks["revision_authority"].grade == EvidenceGrade.CONTRADICTED
    assert any("hard lock" in warning for warning in report.warnings)


def test_change_without_notice_is_contradicted() -> None:
    report = audit_revisability_text(
        "The provider may change this policy at any time without notice."
    )
    checks = {check.key: check for check in _all_checks(report)}

    assert checks["notice"].grade == EvidenceGrade.CONTRADICTED
    assert any("without notice" in warning for warning in report.warnings)


def test_negative_notice_safeguard_is_not_a_risk() -> None:
    report = audit_revisability_text(
        "We will not change this policy without advance notice to affected users."
    )

    assert not any("without notice" in warning for warning in report.warnings)


@pytest.mark.parametrize(
    ("profile", "text", "expected_key"),
    [
        (
            "news_media",
            (
                "AI-generated content must carry a content provenance label. "
                "The correction policy and retraction procedure are published."
            ),
            "content_provenance",
        ),
        (
            "advertising",
            (
                "Client disclosure and client approval are required. "
                "Rights clearance, talent consent, and a licence record are retained."
            ),
            "client_disclosure",
        ),
        (
            "insurance",
            (
                "An adverse action notice states the reason for the decision. "
                "A qualified human review is available to contest a denial."
            ),
            "adverse_action_explanation",
        ),
        (
            "industrial_design",
            (
                "The design file records a hash, provenance, and CAD version. "
                "Design freeze and design release require approval."
            ),
            "design_provenance",
        ),
    ],
)
def test_profile_adds_sector_specific_checks(
    profile: str,
    text: str,
    expected_key: str,
) -> None:
    report = audit_revisability_text(text, profile=profile)
    checks = {check.key: check for check in _all_checks(report)}

    assert report.summary.check_count == 30
    assert expected_key in checks
    assert checks[expected_key].grade == EvidenceGrade.DOCUMENTED


def test_unknown_profile_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unknown review profile"):
        audit_revisability_text("AI policy.", profile="government")


def test_report_renderers_distinguish_text_evidence_and_claim_boundary() -> None:
    report = audit_revisability_text(
        "The policy is reviewed annually. Users may appeal."
    )
    markdown = render_revisability_markdown(report)
    html = render_revisability_html(report)
    payload = json.loads(render_revisability_json(report))

    assert "E0-E2 text evidence" in markdown
    assert "Evidence still required" in markdown
    assert "AI Alignment Revisability Audit" in html
    assert "Claim boundary" in html
    assert payload["report_type"] == "ai-alignment-revisability"
    assert payload["profile"] == "general"


def test_revisability_web_page_and_text_endpoint() -> None:
    page = client.get("/revisability")
    response = client.post(
        "/api/revisability-text",
        json={
            "text": "The AI policy is reviewed annually. Users may appeal.",
            "filename": "policy.txt",
            "profile": "general",
        },
    )

    assert page.status_code == 200
    assert "AI Alignment Revisability Audit" in page.text
    assert response.status_code == 200
    payload = response.json()
    assert payload["report"]["report_type"] == "ai-alignment-revisability"
    assert payload["report"]["summary"]["check_count"] == 28
    assert "AI Alignment Revisability Audit" in payload["html"]
    assert "# AI Alignment Revisability Audit" in payload["markdown"]


def test_revisability_upload_rejects_unsupported_file() -> None:
    response = client.post(
        "/api/revisability",
        files={"file": ("policy.csv", b"a,b\n1,2", "text/csv")},
        data={"profile": "general"},
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]
