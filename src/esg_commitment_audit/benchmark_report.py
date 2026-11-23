from __future__ import annotations

import json

from .benchmark_models import BenchmarkMetrics, BenchmarkReport


def benchmark_report_to_dict(report: BenchmarkReport) -> dict:
    return report.model_dump(mode="json")


def render_benchmark_json(report: BenchmarkReport) -> str:
    return json.dumps(benchmark_report_to_dict(report), ensure_ascii=False, indent=2)


def _percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def _metrics_table(name: str, metrics: BenchmarkMetrics) -> list[str]:
    return [
        f"### {name}",
        "",
        "| Metric | Result |",
        "|---|---:|",
        f"| Decisions | {metrics.total_decisions} |",
        f"| Exact grade accuracy | {_percent(metrics.exact_grade_accuracy)} |",
        f"| Positive precision | {_percent(metrics.positive_precision)} |",
        f"| Positive recall | {_percent(metrics.positive_recall)} |",
        f"| Positive F1 | {_percent(metrics.positive_f1)} |",
        f"| Documented precision | {_percent(metrics.documented_precision)} |",
        f"| Documented recall | {_percent(metrics.documented_recall)} |",
        (
            "| Predicted-positive evidence coverage | "
            f"{_percent(metrics.predicted_positive_evidence_coverage)} |"
        ),
        f"| False positives | {metrics.false_positive_count} |",
        f"| False negatives | {metrics.false_negative_count} |",
        f"| Positive grade mismatches | {metrics.grade_mismatch_count} |",
        "",
    ]


def render_benchmark_markdown(report: BenchmarkReport) -> str:
    gate_label = "PASS" if report.gate.passed else "FAIL"
    lines = [
        f"# {report.title}",
        "",
        f"- Benchmark: `{report.benchmark_id}` `{report.benchmark_version}`",
        f"- Frozen: {report.frozen_at.isoformat()}",
        f"- Methodology: `{report.methodology_version}`",
        f"- Gate: **{gate_label}**",
        "",
        report.description,
        "",
        "## Gate",
        "",
        "| Check | Result |",
        "|---|---|",
        f"| Exact grade accuracy | {'pass' if report.gate.exact_grade_accuracy else 'fail'} |",
        f"| Positive precision | {'pass' if report.gate.positive_precision else 'fail'} |",
        f"| Positive recall | {'pass' if report.gate.positive_recall else 'fail'} |",
        f"| Evidence coverage | {'pass' if report.gate.evidence_coverage else 'fail'} |",
        "",
        "## Metrics",
        "",
    ]
    lines.extend(_metrics_table("Overall", report.overall))
    lines.extend(_metrics_table("Calibration split", report.calibration))
    lines.extend(_metrics_table("Frozen evaluation split", report.evaluation))

    lines.extend(
        [
            "## Mismatches",
            "",
            "| Document | Control | Expected | Actual | Type |",
            "|---|---|---|---|---|",
        ]
    )
    for item in report.mismatches:
        lines.append(
            f"| `{item.document_id}` | `{item.check_key}` | "
            f"`{item.expected_grade.value}` | `{item.actual_grade.value}` | "
            f"{item.kind} |"
        )
    if not report.mismatches:
        lines.append("| None | — | — | — | — |")

    lines.extend(
        [
            "",
            "## Case results",
            "",
            "| Document | Jurisdiction | Type | Capture | Split | Differences |",
            "|---|---|---|---|---|---:|",
        ]
    )
    for item in report.case_results:
        lines.append(
            f"| {item.title} (`{item.document_id}`) | {item.jurisdiction} | "
            f"`{item.instrument_type}` | `{item.capture_type}` | {item.split} | "
            f"{len(item.differences)} |"
        )

    lines.extend(["", "## Claim boundary", "", report.claim_boundary, ""])
    return "\n".join(lines)
