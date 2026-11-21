from __future__ import annotations

from ics_commitment_audit.api import audit_governance_text
from ics_commitment_audit.models import CheckStatus


def test_complete_policy_covers_all_ten_structural_checks() -> None:
    report = audit_governance_text(
        """
        AI Use Policy
        Scope: This policy applies to all staff and contractors.
        Effective date: 1 January 2027.
        Policy owner: Chief Responsible AI Officer.
        The policy is reviewed annually by the responsible owner.
        Amend this policy only through the documented revision procedure.
        Version history and a dated change log are published.
        We will notify affected users before material changes.
        Users may request human review and appeal an automated decision.
        Users may refuse optional processing and exit the service at any time.
        An audit log and monitoring evidence are retained.
        A rollback or suspension plan is activated when controls fail.
        Independent oversight is provided by an external ethics panel.
        """
    )

    assert report.summary.check_count == 10
    assert report.summary.present_count == 10
    assert report.summary.partial_count == 0
    assert report.summary.missing_count == 0
    assert report.recommendations == []
    assert all(check.evidence for check in report.checks)


def test_sparse_policy_exposes_missing_checks_and_risk_language() -> None:
    report = audit_governance_text(
        "This policy may change without notice at our sole discretion."
    )

    assert report.summary.missing_count > 0
    assert "The document permits changes without notice." in (
        report.summary.document_warnings
    )
    assert (
        "The document gives one party broad discretionary authority."
        in report.summary.document_warnings
    )
    assert report.recommendations


def test_notice_safeguard_is_not_reported_as_a_risk() -> None:
    report = audit_governance_text(
        "We will not change this policy without advance notice to affected users."
    )

    assert "The document permits changes without notice." not in (
        report.summary.document_warnings
    )


def test_safe_notice_clause_does_not_hide_an_unsafe_clause() -> None:
    report = audit_governance_text(
        "We will not change this policy without advance notice.\n\n"
        "The vendor may terminate access without notice."
    )

    assert "The document permits changes without notice." in (
        report.summary.document_warnings
    )


def test_partial_check_keeps_evidence() -> None:
    report = audit_governance_text("The policy is reviewed when needed.")
    review = next(check for check in report.checks if check.key == "review_cadence")

    assert review.status == CheckStatus.PARTIAL
    assert review.evidence
    assert review.evidence[0].excerpt
