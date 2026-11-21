from __future__ import annotations

import json
from pathlib import Path


def _review() -> dict:
    return json.loads(
        Path("validation/real_report_review_v011_2026-11-21.json").read_text(
            encoding="utf-8"
        )
    )


def test_v011_validation_metrics_match_manual_labels() -> None:
    review = _review()
    candidates = [
        candidate
        for report in review["reports"]
        for values in report["candidate_labels"].values()
        for candidate in values
    ]
    true_positives = [
        candidate
        for report in review["reports"]
        for candidate in report["candidate_labels"]["true_positive"]
    ]
    category_correct = [
        candidate
        for report in review["reports"]
        for candidate in report["top_level_category_correct"]
    ]
    subcategory_correct = [
        candidate
        for report in review["reports"]
        for candidate in report["subcategory_correct"]
    ]
    manual_commitments = sum(
        report["manual_commitment_count"] for report in review["reports"]
    )
    recalled = sum(
        report["manual_commitments_recalled"] for report in review["reports"]
    )

    summary = review["summary"]
    assert summary["sampled_candidates"] == len(candidates) == 31
    assert summary["true_positive_candidates"] == len(true_positives) == 26
    assert summary["false_positive_candidates"] == len(candidates) - len(true_positives)
    assert (
        round(len(true_positives) / len(candidates), 4)
        == summary["candidate_precision"]
    )
    assert summary["manual_unique_commitments"] == manual_commitments == 43
    assert summary["manual_unique_commitments_recalled"] == recalled == 31
    assert (
        round(recalled / manual_commitments, 4) == summary["unique_commitment_recall"]
    )
    assert (
        round(len(category_correct) / len(true_positives), 4)
        == summary["top_level_category_accuracy_on_true_positive_candidates"]
    )
    assert (
        round(len(subcategory_correct) / len(true_positives), 4)
        == summary["subcategory_accuracy_on_true_positive_candidates"]
    )
