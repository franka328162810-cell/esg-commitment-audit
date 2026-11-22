from __future__ import annotations

import json
from importlib.resources import files

from jinja2 import Environment, FileSystemLoader

from .revisability_models import RevisabilityReport


def revisability_report_to_dict(report: RevisabilityReport) -> dict:
    return report.model_dump(mode="json")


def render_revisability_json(report: RevisabilityReport) -> str:
    return json.dumps(
        revisability_report_to_dict(report),
        ensure_ascii=False,
        indent=2,
    )


def _source_label(evidence) -> str:
    if evidence.page_number:
        return f"p.{evidence.page_number}, paragraph {evidence.paragraph_index}"
    return f"paragraph {evidence.paragraph_index}"


def _escape_table(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_revisability_markdown(report: RevisabilityReport) -> str:
    lines = [
        "# AI Alignment Revisability Audit",
        "",
        f"- Source: `{report.document.filename}`",
        f"- SHA-256: `{report.document.sha256}`",
        f"- Generated: {report.generated_at.isoformat()}",
        f"- Profile: `{report.profile}` ({report.profile_label})",
        f"- Methodology: `{report.methodology_version}`",
        "",
        "## Evidence summary",
        "",
        f"- Review dimensions: {report.summary.dimension_count}",
        f"- Checks: {report.summary.check_count}",
        f"- Documented: {report.summary.documented_count}",
        f"- Asserted only: {report.summary.asserted_count}",
        f"- Absent: {report.summary.absent_count}",
        f"- Contradicted: {report.summary.contradicted_count}",
        f"- Operationally evidenced: {report.summary.operationally_evidenced_count}",
        f"- Independently verified: {report.summary.independently_verified_count}",
        "",
        (
            "This document-only mode can establish E0-E2 text evidence. E3 requires "
            "operation records and E4 requires independent verification."
        ),
        "",
    ]

    if report.warnings:
        lines.extend(["## Risk warnings", ""])
        lines.extend(f"- {warning}" for warning in report.warnings)
        lines.append("")

    for dimension in report.dimensions:
        lines.extend(
            [
                f"## {dimension.label}",
                "",
                "| Check | Grade | Finding | Evidence |",
                "|---|---|---|---|",
            ]
        )
        for check in dimension.checks:
            support = check.rationale
            if check.evidence:
                support = (
                    f"{check.evidence[0].excerpt} ({_source_label(check.evidence[0])})"
                )
            lines.append(
                f"| {_escape_table(check.label)} | `{check.grade.value}` | "
                f"{_escape_table(check.rationale)} | {_escape_table(support)} |"
            )
        lines.append("")

        for check in dimension.checks:
            if check.grade.value in {"absent", "asserted", "contradicted"}:
                lines.extend(
                    [
                        f"### {check.label}",
                        "",
                        f"- Grade: `{check.grade.value}`",
                        f"- Finding: {check.rationale}",
                        f"- Recommendation: {check.recommendation}",
                    ]
                )
                if check.required_artifacts:
                    lines.append("- Evidence still required:")
                    lines.extend(f"  - {item}" for item in check.required_artifacts)
                lines.append("")

    if report.recommendations:
        lines.extend(["## Priority recommendations", ""])
        lines.extend(f"- {item}" for item in report.recommendations)
        lines.append("")

    if report.evidence_requests:
        lines.extend(["## Evidence request list", ""])
        lines.extend(f"- {item}" for item in report.evidence_requests)
        lines.append("")

    lines.extend(["## Claim boundary", "", report.disclaimer, ""])
    return "\n".join(lines)


def _template_environment() -> Environment:
    template_dir = files("esg_commitment_audit").joinpath("resources/templates")
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=True,
    )


def render_revisability_html(report: RevisabilityReport) -> str:
    template = _template_environment().get_template("revisability_report.html.j2")
    return template.render(report=report)
