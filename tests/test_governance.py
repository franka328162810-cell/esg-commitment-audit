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


def test_generic_consent_is_not_a_refusal_or_exit_route() -> None:
    report = audit_governance_text(
        "Do not process personal data without the person's consent."
    )
    check = next(item for item in report.checks if item.key == "refusal_exit")

    assert check.status == CheckStatus.MISSING
    assert check.evidence == []


def test_general_oversight_language_is_not_independent_oversight() -> None:
    report = audit_governance_text(
        "The programme will not evade legal oversight or accountability."
    )
    check = next(item for item in report.checks if item.key == "independent_oversight")

    assert check.status == CheckStatus.MISSING


def test_suspending_user_access_is_not_policy_rollback() -> None:
    report = audit_governance_text(
        "We may suspend or terminate your access if you violate this policy."
    )
    check = next(item for item in report.checks if item.key == "rollback_deprecation")

    assert check.status == CheckStatus.MISSING


def test_human_in_the_loop_review_is_not_policy_review_cadence() -> None:
    report = audit_governance_text(
        "A qualified person must review a high-risk recommendation before delivery."
    )
    check = next(item for item in report.checks if item.key == "review_cadence")

    assert check.status == CheckStatus.MISSING


def test_scope_check_requires_scope_owner_and_effective_date() -> None:
    partial = audit_governance_text("This policy applies to all users.")
    complete = audit_governance_text(
        "Effective date: 1 January 2027. "
        "This policy applies to all users. "
        "Policy owner: Chief AI Officer."
    )
    partial_check = next(
        item for item in partial.checks if item.key == "scope_and_owner"
    )
    complete_check = next(
        item for item in complete.checks if item.key == "scope_and_owner"
    )

    assert partial_check.status == CheckStatus.PARTIAL
    assert complete_check.status == CheckStatus.PRESENT


def test_external_reviewers_count_as_independent_oversight() -> None:
    report = audit_governance_text(
        "The board approves external reviewers for the public risk report."
    )
    check = next(item for item in report.checks if item.key == "independent_oversight")

    assert check.status == CheckStatus.PRESENT
    assert check.evidence


def test_public_update_page_is_partial_notice_without_advance_period() -> None:
    report = audit_governance_text(
        "We will use this page to inform the public of future policy developments."
    )
    check = next(item for item in report.checks if item.key == "notice")

    assert check.status == CheckStatus.PARTIAL


def test_notice_before_change_is_present() -> None:
    report = audit_governance_text(
        "We will notify affected users at least 30 days before changing this policy."
    )
    check = next(item for item in report.checks if item.key == "notice")

    assert check.status == CheckStatus.PRESENT


def test_plural_audit_logs_count_as_monitoring_evidence() -> None:
    report = audit_governance_text(
        "Audit logs are retained and reviewed by an independent team."
    )
    check = next(item for item in report.checks if item.key == "monitoring_audit")

    assert check.status == CheckStatus.PRESENT
