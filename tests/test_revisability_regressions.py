from __future__ import annotations

from esg_commitment_audit.api import audit_revisability_text
from esg_commitment_audit.revisability_models import EvidenceGrade


def _checks(text: str) -> dict[str, EvidenceGrade]:
    report = audit_revisability_text(text)
    return {
        check.key: check.grade
        for dimension in report.dimensions
        for check in dimension.checks
    }


def test_legal_address_is_not_an_alignment_constitution() -> None:
    checks = _checks(
        "Send the report to 14th Street and Constitution Avenue NW, Washington, DC."
    )

    assert checks["alignment_target"] == EvidenceGrade.ABSENT


def test_unrelated_cannot_change_language_is_not_revision_contradiction() -> None:
    checks = _checks("The sensor value cannot be changed by the user of the device.")

    assert checks["revision_authority"] == EvidenceGrade.ABSENT


def test_page_version_label_is_not_a_policy_version_identifier() -> None:
    checks = _checks("| Caption Version | Documents |")

    assert checks["version_identifier"] == EvidenceGrade.ABSENT


def test_early_warning_notice_is_not_policy_change_notice() -> None:
    checks = _checks(
        "The evaluation runs frequently enough that we have notice before a "
        "capability threshold is reached."
    )

    assert checks["notice"] == EvidenceGrade.ABSENT


def test_ultimate_human_responsibility_is_not_policy_owner() -> None:
    checks = _checks(
        "Human beings are the ultimate responsible subjects and must remain "
        "accountable."
    )

    assert checks["accountable_owner"] == EvidenceGrade.ABSENT


def test_personal_data_retention_is_not_audit_evidence_retention() -> None:
    checks = _checks(
        "The provider may retain personal information only for the minimum period."
    )

    assert checks["retention"] == EvidenceGrade.ABSENT


def test_review_and_evolve_periodically_is_review_cadence_not_staged_change() -> None:
    checks = _checks(
        "We will review and evolve the Framework periodically. As we pilot the "
        "Framework, we will calibrate the mitigations."
    )

    assert checks["review_cadence"] == EvidenceGrade.DOCUMENTED
    assert checks["gradual_change"] == EvidenceGrade.ABSENT


def test_eu_style_stop_button_is_documented_interruptibility() -> None:
    checks = _checks(
        "Natural persons must be able to interrupt the system through a stop "
        "button that brings the system to a safe state."
    )

    assert checks["interruptibility"] == EvidenceGrade.DOCUMENTED


def test_automatic_logs_and_retention_are_documented_controls() -> None:
    checks = _checks(
        "High-risk systems must automatically generate logs. Providers must keep "
        "the logs for at least six months."
    )

    assert checks["audit_logs"] == EvidenceGrade.DOCUMENTED
    assert checks["retention"] == EvidenceGrade.DOCUMENTED


def test_conflicts_of_interest_for_auditors_support_anti_abuse() -> None:
    checks = _checks(
        "Independent auditors must satisfy requirements on independence and "
        "absence of conflicts of interest."
    )

    assert checks["independent_oversight"] == EvidenceGrade.DOCUMENTED
    assert checks["anti_abuse"] == EvidenceGrade.DOCUMENTED
