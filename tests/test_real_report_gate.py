from __future__ import annotations

import json
from pathlib import Path

from validation.check_gate import calculate_metrics, gate_status


def test_real_report_gate_matches_recorded_summary() -> None:
    review = json.loads(
        Path("validation/real_report_review_v011_gate_2026-11-21.json").read_text(
            encoding="utf-8"
        )
    )
    metrics = calculate_metrics(review)
    status = gate_status(metrics, review["thresholds"])

    assert metrics == review["summary"]
    assert all(status.values()), status
