from __future__ import annotations

import json
from importlib.resources import files

from jinja2 import Environment, FileSystemLoader

from .revisability_versions import StatementChange, VersionTraceReport


def version_trace_report_to_dict(report: VersionTraceReport) -> dict:
    return report.model_dump(mode="json")


def render_version_trace_json(report: VersionTraceReport) -> str:
    return json.dumps(
        version_trace_report_to_dict(report),
        ensure_ascii=False,
        indent=2,
    )


def _source_label(evidence) -> str:
    if evidence is None:
        return "N/A"
    if evidence.page_number:
        return f"p.{evidence.page_number}, paragraph {evidence.paragraph_index}"
    return f"paragraph {evidence.paragraph_index}"


def _escape_table(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _statement_text(change: StatementChange) -> str:
    if change.change_type == "removed":
        return change.previous.excerpt if change.previous else ""
    if change.change_type == "added":
        return change.current.excerpt if change.current else ""
    previous = change.previous.excerpt if change.previous else ""
    current = change.current.excerpt if change.current else ""
    return f"Previous: {previous} → Current: {current}"


def render_version_trace_markdown(report: VersionTraceReport) -> str:
    lines = [
        "# AI Alignment Revisability Version Trace",
        "",
        f"- Previous: `{report.previous.document.filename}`",
        f"- Current: `{report.current.document.filename}`",
        f"- Generated: {report.generated_at.isoformat()}",
        f"- Profile: `{report.profile}` ({report.profile_label})",
        "",
        "## Change summary",
        "",
        f"- Improved checks: {report.summary.improved_count}",
        f"- Regressed checks: {report.summary.regressed_count}",
        f"- High-materiality regressions: {report.summary.high_materiality_count}",
        f"- Added statements: {report.summary.added_statement_count}",
        f"- Removed statements: {report.summary.removed_statement_count}",
        f"- Modified statements: {report.summary.modified_statement_count}",
        "",
        "## Material check changes",
        "",
        "| Check | Previous | Current | Direction | Materiality |",
        "|---|---|---|---|---|",
    ]
    for change in report.material_changes:
        lines.append(
            f"| {_escape_table(change.label)} | `{change.previous_grade.value}` | "
            f"`{change.current_grade.value}` | `{change.direction}` | "
            f"`{change.materiality}` |"
        )
    if not report.material_changes:
        lines.append("| No material check change | — | — | — | — |")
    lines.append("")

    if report.new_warnings or report.resolved_warnings:
        lines.extend(["## Risk-warning movement", ""])
        lines.extend(f"- New: {item}" for item in report.new_warnings)
        lines.extend(f"- Resolved: {item}" for item in report.resolved_warnings)
        lines.append("")

    lines.extend(
        [
            "## Statement changes",
            "",
            "| Type | Similarity | Previous source | Current source | Text |",
            "|---|---:|---|---|---|",
        ]
    )
    for change in report.statement_changes:
        similarity = (
            f"{change.similarity:.2f}" if change.similarity is not None else "—"
        )
        lines.append(
            f"| `{change.change_type}` | {similarity} | "
            f"{_source_label(change.previous)} | {_source_label(change.current)} | "
            f"{_escape_table(_statement_text(change))} |"
        )
    if not report.statement_changes:
        lines.append("| No exact statement change | — | — | — | — |")

    lines.extend(["", "## Claim boundary", "", report.disclaimer, ""])
    return "\n".join(lines)


def _template_environment() -> Environment:
    template_dir = files("esg_commitment_audit").joinpath("resources/templates")
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=True,
    )


def render_version_trace_html(report: VersionTraceReport) -> str:
    template = _template_environment().get_template(
        "revisability_version_report.html.j2"
    )
    return template.render(report=report)
