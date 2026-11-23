from __future__ import annotations

import json
from importlib.resources import files

from jinja2 import Environment, FileSystemLoader

from .evidence_pack_models import EvidencePackReport


def evidence_pack_to_dict(report: EvidencePackReport) -> dict:
    return report.model_dump(mode="json")


def render_evidence_pack_json(report: EvidencePackReport) -> str:
    return json.dumps(evidence_pack_to_dict(report), ensure_ascii=False, indent=2)


def render_evidence_pack_markdown(report: EvidencePackReport) -> str:
    lines = [
        "# AI Revisability Evidence-Pack Assessment",
        "",
        f"- Organization: **{report.organization}**",
        f"- Review date: {report.reviewed_at.isoformat()}",
        f"- Profile: `{report.profile}`",
        f"- Base document: `{report.base_document}`",
        f"- Base SHA-256: `{report.base_document_sha256}`",
        "",
        "## Artifact inventory",
        "",
        "| Artifact | Type | Issuer | Issued | Hash | E3 Eligible | Warnings |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in report.artifact_inventory:
        hash_status = (
            "matched"
            if item.hash_matches is True
            else "mismatch"
            if item.hash_matches is False
            else "not pinned"
        )
        lines.append(
            f"| `{item.path}` | `{item.artifact_type}` | {item.issuer or '—'} | "
            f"{item.issued_at or '—'} | {hash_status} | "
            f"{str(item.eligible_for_operational_evidence).lower()} | "
            f"{'; '.join(item.warnings) or '—'} |"
        )

    lines.extend(
        [
            "",
            "## Proposed evidence-grade promotions",
            "",
            "| Control | Baseline | Proposed | Supporting artifacts | Human confirmation |",
            "|---|---|---|---|---|",
        ]
    )
    for item in report.promotions:
        lines.append(
            f"| `{item.check_key}` | `{item.baseline_grade.value}` | "
            f"`{item.proposed_grade.value}` | "
            f"{', '.join(f'`{path}`' for path in item.supporting_artifacts)} | "
            f"{str(item.requires_human_confirmation).lower()} |"
        )
    if not report.promotions:
        lines.append("| No promotion proposed | — | — | — | — |")

    lines.extend(["", "## Remaining evidence gaps", ""])
    for item in report.unresolved_controls:
        lines.append(
            f"- `{item.check_key}` ({item.baseline_grade.value}): needs "
            f"{', '.join(item.missing_artifact_types)}"
        )
    if not report.unresolved_controls:
        lines.append("- No mapped evidence gaps.")

    if report.warnings:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in report.warnings)

    lines.extend(["", "## Claim boundary", "", report.disclaimer, ""])
    return "\n".join(lines)


def _template_environment() -> Environment:
    template_dir = files("esg_commitment_audit").joinpath("resources/templates")
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=True,
    )


def render_evidence_pack_html(report: EvidencePackReport) -> str:
    template = _template_environment().get_template("evidence_pack_report.html.j2")
    return template.render(report=report)
