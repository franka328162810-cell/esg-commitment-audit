from __future__ import annotations

import json
from pathlib import Path


def test_real_report_review_metrics_match_labels() -> None:
    review = json.loads(
        Path("validation/real_report_review_2026-11-21.json").read_text(
            encoding="utf-8"
        )
    )
    candidates = [
        candidate
        for report in review["reports"]
        for candidate in report["candidate_labels"]
    ]
    true_positives = [
        candidate for candidate in candidates if candidate["label"] == "true_positive"
    ]

    summary = review["summary"]
    assert summary["sampled_candidates"] == len(candidates) == 37
    assert summary["sampled_true_positive_candidates"] == len(true_positives) == 13
    assert summary["sampled_false_positive_candidates"] == len(candidates) - len(
        true_positives
    )
    assert (
        round(len(true_positives) / len(candidates), 4)
        == summary["candidate_precision"]
    )
    assert summary["sampled_unique_manual_commitments"] == 14
    assert summary["sampled_manual_commitments_recalled"] == 14
    assert summary["page_citation_coverage"] == 1.0
