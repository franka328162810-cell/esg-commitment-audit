from __future__ import annotations

import json
from importlib.resources import files

from jinja2 import Environment, FileSystemLoader

from .models import AuditReport, CheckStatus


def report_to_dict(report: AuditReport) -> dict:
    return report.model_dump(mode="json")


def render_json(report: AuditReport) -> str:
    return json.dumps(report_to_dict(report), ensure_ascii=False, indent=2)


def _escape_table(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(report: AuditReport) -> str:
    lines = [
        "# ICS Commitment Audit Report",
        "",
        f"- Source: `{report.document.filename}`",
        f"- SHA-256: `{report.document.sha256}`",
        f"- Generated: {report.generated_at.isoformat()}",
        f"- Weight preset: `{report.weights.name}`",
        (
            f"- Weights: V_obs={report.weights.V_obs:.2f}, "
            f"V_enf={report.weights.V_enf:.2f}, V_rev={report.weights.V_rev:.2f}"
        ),
        "",
        "## Summary",
        "",
        f"- Commitments detected: {report.summary.commitment_count}",
        (
            f"- Average CRV structure score: {report.summary.average_crv:.4f}"
            if report.summary.average_crv is not None
            else "- Average CRV structure score: not available"
        ),
        (
            f"- High / moderate / limited: {report.summary.high_structure_count} / "
            f"{report.summary.moderate_structure_count} / "
            f"{report.summary.limited_structure_count}"
        ),
        "",
    ]

    if report.summary.document_warnings:
        lines.extend(["### Document warnings", ""])
        lines.extend(f"- {warning}" for warning in report.summary.document_warnings)
        lines.append("")

    if report.commitments:
        lines.extend(
            [
                "## Commitment overview",
                "",
                "| ID | Category | CRV | Grade | Source |",
                "|---|---|---:|---|---|",
            ]
        )
        for item in report.commitments:
            source = (
                f"p.{item.evidence.page_number}"
                if item.evidence.page_number
                else f"paragraph {item.evidence.paragraph_index}"
            )
            lines.append(
                f"| {_escape_table(item.commitment_id)} | "
                f"{_escape_table(item.subcategory)} | {item.crv_score:.4f} | "
                f"{_escape_table(item.grade)} | {_escape_table(source)} |"
            )
        lines.append("")

    for item in report.commitments:
        lines.extend(
            [
                f"## {item.commitment_id} — {item.subcategory}",
                "",
                f"> {item.evidence.excerpt}",
                "",
                f"- Strength: `{item.strength}`",
                f"- Extraction confidence: `{item.extraction_confidence:.2f}`",
                f"- CRV structure score: **{item.crv_score:.4f}** ({item.grade})",
                "",
            ]
        )
        for dimension in item.dimensions:
            lines.append(
                f"### {dimension.label} (`{dimension.key}`): {dimension.score:.4f}"
            )
            lines.extend(
                [
                    "",
                    "| Check | Status | Points | Evidence / note |",
                    "|---|---|---:|---|",
                ]
            )
            for check in dimension.checks:
                support = check.evidence[0].excerpt if check.evidence else check.note
                lines.append(
                    f"| {_escape_table(check.label)} | `{check.status.value}` | "
                    f"{check.points:.2f}/{check.weight:.2f} | "
                    f"{_escape_table(support)} |"
                )
            lines.append("")
        if item.warnings:
            lines.extend(["### Warnings", ""])
            lines.extend(f"- {warning}" for warning in item.warnings)
            lines.append("")
        if item.recommendations:
            lines.extend(["### Suggested text improvements", ""])
            lines.extend(
                f"- {recommendation}" for recommendation in item.recommendations
            )
            lines.append("")

    lines.extend(["## Disclaimer", "", report.disclaimer, ""])
    return "\n".join(lines)


def _template_environment() -> Environment:
    template_dir = files("ics_commitment_audit").joinpath("resources/templates")
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=True,
    )


def render_html(report: AuditReport) -> str:
    template = _template_environment().get_template("report.html.j2")
    return template.render(
        report=report,
        status_present=CheckStatus.PRESENT,
        status_partial=CheckStatus.PARTIAL,
    )
