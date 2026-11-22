from __future__ import annotations

import json
from pathlib import Path

from esg_commitment_audit.api import audit_text


def test_internal_benchmark_meets_v01_thresholds() -> None:
    cases = [
        json.loads(line)
        for line in Path("tests/fixtures/benchmark.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    true_positive = false_positive = false_negative = 0
    category_total = category_correct = 0

    for case in cases:
        report = audit_text(case["text"], "benchmark.txt")
        predicted = report.summary.commitment_count > 0
        expected = case["expected"]
        if predicted and expected:
            true_positive += 1
            category_total += 1
            actual_categories = {item.category for item in report.commitments}
            if case["category"] in actual_categories:
                category_correct += 1
        elif predicted and not expected:
            false_positive += 1
        elif not predicted and expected:
            false_negative += 1

    precision = true_positive / max(1, true_positive + false_positive)
    recall = true_positive / max(1, true_positive + false_negative)
    category_accuracy = category_correct / max(1, category_total)

    assert precision >= 0.85, f"precision={precision:.3f}"
    assert recall >= 0.85, f"recall={recall:.3f}"
    assert category_accuracy >= 0.80, f"category_accuracy={category_accuracy:.3f}"
