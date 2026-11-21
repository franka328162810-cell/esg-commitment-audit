from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def calculate_metrics(review: dict[str, Any]) -> dict[str, Any]:
    reports = review["reports"]
    manual = [
        commitment for report in reports for commitment in report["manual_commitments"]
    ]
    candidates = [
        decision for report in reports for decision in report["candidate_decisions"]
    ]
    true_candidates = [
        decision for decision in candidates if decision["verdict"] == "true_positive"
    ]
    duplicate_candidates = [
        decision for decision in candidates if decision["verdict"] == "duplicate"
    ]
    recalled_ids = {
        manual_id for decision in true_candidates for manual_id in decision["matches"]
    }
    manual_by_id = {commitment["manual_id"]: commitment for commitment in manual}

    category_correct = sum(
        bool(decision["category_correct"]) for decision in true_candidates
    )
    subcategory_correct = sum(
        bool(decision["subcategory_correct"]) for decision in true_candidates
    )
    pages_present = all(
        manual_by_id[manual_id]["page"] is not None
        for decision in true_candidates
        for manual_id in decision["matches"]
        if manual_id in manual_by_id
    )
    unknown_matches = sorted(recalled_ids - set(manual_by_id))

    return {
        "sampled_candidates": len(candidates),
        "true_positive_candidates": len(true_candidates),
        "false_positive_candidates": sum(
            decision["verdict"] == "false_positive" for decision in candidates
        ),
        "duplicate_candidates": len(duplicate_candidates),
        "candidate_precision": round(len(true_candidates) / max(1, len(candidates)), 4),
        "manual_unique_commitments": len(manual),
        "manual_unique_commitments_recalled": len(recalled_ids),
        "unique_commitment_recall": round(
            len(recalled_ids) / max(1, len(manual)),
            4,
        ),
        "top_level_category_accuracy": round(
            category_correct / max(1, len(true_candidates)),
            4,
        ),
        "subcategory_accuracy": round(
            subcategory_correct / max(1, len(true_candidates)),
            4,
        ),
        "page_citation_coverage": 1.0 if pages_present and not unknown_matches else 0.0,
        "unknown_manual_matches": unknown_matches,
    }


def gate_status(
    metrics: dict[str, Any], thresholds: dict[str, float]
) -> dict[str, bool]:
    return {
        "candidate_precision": metrics["candidate_precision"]
        >= thresholds["candidate_precision"],
        "unique_commitment_recall": metrics["unique_commitment_recall"]
        >= thresholds["unique_commitment_recall"],
        "top_level_category_accuracy": metrics["top_level_category_accuracy"]
        >= thresholds["top_level_category_accuracy"],
        "page_citation_coverage": metrics["page_citation_coverage"]
        >= thresholds["page_citation_coverage"],
        "sample_size": metrics["manual_unique_commitments"]
        >= thresholds["minimum_manual_commitments"],
        "duplicate_candidates_merged": metrics["duplicate_candidates"] == 0,
        "no_unknown_manual_matches": not metrics["unknown_manual_matches"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "review",
        nargs="?",
        default="validation/real_report_review_v011_gate_2026-11-21.json",
    )
    args = parser.parse_args()
    review = json.loads(Path(args.review).read_text(encoding="utf-8"))
    metrics = calculate_metrics(review)
    status = gate_status(metrics, review["thresholds"])
    print(json.dumps({"metrics": metrics, "gate_status": status}, indent=2))
    raise SystemExit(0 if all(status.values()) else 1)


if __name__ == "__main__":
    main()
