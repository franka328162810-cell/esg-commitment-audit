from __future__ import annotations

from pathlib import Path

from esg_commitment_audit.api import audit_bytes


def test_strong_sample_scores_higher_than_vague_sample() -> None:
    strong = audit_bytes(
        Path("examples/strong_commitment.txt").read_bytes(),
        "strong_commitment.txt",
    )
    vague = audit_bytes(
        Path("examples/vague_statement.txt").read_bytes(),
        "vague_statement.txt",
    )
    assert strong.summary.commitment_count == 1
    assert vague.summary.commitment_count == 1
    assert strong.commitments[0].crv_score > vague.commitments[0].crv_score
    assert strong.commitments[0].crv_score >= 0.70
    assert vague.commitments[0].crv_score < 0.50


def test_every_present_check_has_source_evidence() -> None:
    report = audit_bytes(
        Path("examples/strong_commitment.txt").read_bytes(),
        "strong_commitment.txt",
    )
    for commitment in report.commitments:
        for dimension in commitment.dimensions:
            for check in dimension.checks:
                if check.status.value == "present":
                    assert check.evidence
                    assert check.evidence[0].excerpt


def test_conflicting_targets_create_document_warning() -> None:
    report = audit_bytes(
        Path("examples/conflicting_commitments.txt").read_bytes(),
        "conflicting_commitments.txt",
    )
    assert report.summary.commitment_count >= 2
    joined = " ".join(report.summary.document_warnings)
    assert "不同百分比目标" in joined


def test_weight_preset_changes_aggregate_score() -> None:
    data = Path("examples/strong_commitment.txt").read_bytes()
    default = audit_bytes(data, "strong.txt", "default")
    obs = audit_bytes(data, "strong.txt", "obs-priority")
    assert default.commitments[0].crv_score != obs.commitments[0].crv_score
    assert default.weights.name == "default"
    assert obs.weights.name == "obs-priority"


def test_no_commitment_returns_explicit_warning() -> None:
    report = audit_bytes(
        b"This section describes historical procurement data only.",
        "empty.txt",
    )
    assert report.summary.commitment_count == 0
    assert report.summary.average_crv is None
    assert report.summary.document_warnings
