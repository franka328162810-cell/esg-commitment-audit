from __future__ import annotations

import re
from collections import Counter
from datetime import UTC, datetime
from difflib import SequenceMatcher
from typing import Literal

from pydantic import BaseModel, Field

from .models import EvidenceSpan, IngestedDocument
from .revisability import audit_revisability_document
from .revisability_models import (
    EvidenceGrade,
    ReviewProfile,
    RevisabilityCheck,
    RevisabilityReport,
)


class CheckChange(BaseModel):
    key: str
    label: str
    previous_grade: EvidenceGrade
    current_grade: EvidenceGrade
    direction: Literal["improved", "regressed", "unchanged", "changed"]
    materiality: Literal["high", "medium", "low", "positive"]
    previous_evidence: EvidenceSpan | None = None
    current_evidence: EvidenceSpan | None = None


class StatementChange(BaseModel):
    change_type: Literal["added", "removed", "modified"]
    previous: EvidenceSpan | None = None
    current: EvidenceSpan | None = None
    similarity: float | None = Field(default=None, ge=0.0, le=1.0)


class VersionTraceSummary(BaseModel):
    improved_count: int
    regressed_count: int
    unchanged_count: int
    changed_count: int
    high_materiality_count: int
    added_statement_count: int
    removed_statement_count: int
    modified_statement_count: int


class VersionTraceReport(BaseModel):
    report_version: str = "0.6.0"
    report_type: Literal["ai-revisability-version-trace"] = (
        "ai-revisability-version-trace"
    )
    generated_at: datetime
    profile: ReviewProfile
    profile_label: str
    previous: RevisabilityReport
    current: RevisabilityReport
    summary: VersionTraceSummary
    check_changes: list[CheckChange]
    material_changes: list[CheckChange]
    statement_changes: list[StatementChange]
    new_warnings: list[str] = Field(default_factory=list)
    resolved_warnings: list[str] = Field(default_factory=list)
    disclaimer: str


VERSION_DISCLAIMER = (
    "This report compares two written versions using rule-based document "
    "evidence. It can identify declared changes, grade movement, and new "
    "warnings. It does not prove why a change was made, whether approval "
    "occurred, whether the change operated, or whether the revised system is "
    "safe or compliant."
)


GRADE_RANK = {
    EvidenceGrade.CONTRADICTED: -1,
    EvidenceGrade.ABSENT: 0,
    EvidenceGrade.ASSERTED: 1,
    EvidenceGrade.DOCUMENTED: 2,
    EvidenceGrade.OPERATIONALLY_EVIDENCED: 3,
    EvidenceGrade.INDEPENDENTLY_VERIFIED: 4,
}


def _sentence_units(text: str) -> list[str]:
    return [
        item.strip()
        for item in re.split(r"(?<=[。！？!?;；])\s*|\n+", text)
        if item.strip()
    ]


def _evidence(
    document: IngestedDocument,
    block_id: str,
    unit_index: int,
) -> EvidenceSpan:
    block = next(item for item in document.blocks if item.block_id == block_id)
    units = _sentence_units(block.text)
    unit = units[min(unit_index, len(units) - 1)] if units else block.text
    excerpt = unit[:420] + ("…" if len(unit) > 420 else "")
    return EvidenceSpan(
        block_id=block.block_id,
        paragraph_index=block.paragraph_index,
        unit_index=unit_index,
        page_number=block.page_number,
        section=block.section,
        source_type=block.source_type,
        table_role=block.table_role,
        text=unit,
        excerpt=excerpt,
    )


def _normalize_statement(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def _statement_map(document: IngestedDocument) -> dict[str, EvidenceSpan]:
    statements: dict[str, EvidenceSpan] = {}
    for block in document.blocks:
        if block.is_heading:
            continue
        for unit_index, unit in enumerate(_sentence_units(block.text)):
            if len(unit) < 12:
                continue
            normalized = _normalize_statement(unit)
            if normalized:
                statements[normalized] = _evidence(document, block.block_id, unit_index)
    return statements


def _flatten_checks(report: RevisabilityReport) -> dict[str, RevisabilityCheck]:
    return {
        check.key: check
        for dimension in report.dimensions
        for check in dimension.checks
    }


def _direction(
    previous: EvidenceGrade,
    current: EvidenceGrade,
) -> Literal["improved", "regressed", "unchanged", "changed"]:
    if previous == current:
        return "unchanged"
    previous_rank = GRADE_RANK.get(previous)
    current_rank = GRADE_RANK.get(current)
    if previous_rank is None or current_rank is None:
        return "changed"
    return "improved" if current_rank > previous_rank else "regressed"


def _materiality(
    previous: EvidenceGrade,
    current: EvidenceGrade,
    direction: str,
) -> Literal["high", "medium", "low", "positive"]:
    if direction == "positive":
        return "positive"
    if current == EvidenceGrade.CONTRADICTED and previous != current:
        return "high"
    if direction == "regressed":
        if previous == EvidenceGrade.DOCUMENTED and current in {
            EvidenceGrade.ASSERTED,
            EvidenceGrade.ABSENT,
            EvidenceGrade.CONTRADICTED,
        }:
            return "high"
        return "medium"
    if direction == "improved":
        return "positive"
    return "low"


def _compare_checks(
    previous: RevisabilityReport,
    current: RevisabilityReport,
) -> list[CheckChange]:
    before = _flatten_checks(previous)
    after = _flatten_checks(current)
    changes: list[CheckChange] = []
    for key, current_check in after.items():
        previous_check = before.get(key)
        if previous_check is None:
            continue
        direction = _direction(previous_check.grade, current_check.grade)
        materiality = _materiality(
            previous_check.grade,
            current_check.grade,
            "positive" if direction == "improved" else direction,
        )
        changes.append(
            CheckChange(
                key=key,
                label=current_check.label,
                previous_grade=previous_check.grade,
                current_grade=current_check.grade,
                direction=direction,
                materiality=materiality,
                previous_evidence=(
                    previous_check.evidence[0] if previous_check.evidence else None
                ),
                current_evidence=(
                    current_check.evidence[0] if current_check.evidence else None
                ),
            )
        )
    return changes


def _compare_statements(
    previous_document: IngestedDocument,
    current_document: IngestedDocument,
) -> list[StatementChange]:
    previous = _statement_map(previous_document)
    current = _statement_map(current_document)
    removed_keys = set(previous) - set(current)
    added_keys = set(current) - set(previous)
    changes: list[StatementChange] = []

    candidate_removed = list(removed_keys)[:200]
    candidate_added = list(added_keys)[:200]
    for removed_key in candidate_removed:
        if removed_key not in removed_keys:
            continue
        best_key: str | None = None
        best_ratio = 0.0
        for added_key in candidate_added:
            if added_key not in added_keys:
                continue
            ratio = SequenceMatcher(None, removed_key, added_key).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_key = added_key
        if best_key is not None and best_ratio >= 0.82:
            changes.append(
                StatementChange(
                    change_type="modified",
                    previous=previous[removed_key],
                    current=current[best_key],
                    similarity=round(best_ratio, 4),
                )
            )
            removed_keys.remove(removed_key)
            added_keys.remove(best_key)

    changes.extend(
        StatementChange(change_type="removed", previous=previous[key])
        for key in sorted(removed_keys)[:80]
    )
    changes.extend(
        StatementChange(change_type="added", current=current[key])
        for key in sorted(added_keys)[:80]
    )
    return changes[:160]


def audit_revisability_version_documents(
    previous_document: IngestedDocument,
    current_document: IngestedDocument,
    profile: ReviewProfile = "general",
) -> VersionTraceReport:
    previous_report = audit_revisability_document(previous_document, profile=profile)
    current_report = audit_revisability_document(current_document, profile=profile)
    check_changes = _compare_checks(previous_report, current_report)
    counts = Counter(change.direction for change in check_changes)
    statement_changes = _compare_statements(previous_document, current_document)
    statement_counts = Counter(change.change_type for change in statement_changes)
    material_changes = [
        change
        for change in check_changes
        if change.materiality in {"high", "medium", "positive"}
    ]
    previous_warnings = set(previous_report.warnings)
    current_warnings = set(current_report.warnings)

    return VersionTraceReport(
        generated_at=datetime.now(UTC),
        profile=profile,
        profile_label=current_report.profile_label,
        previous=previous_report,
        current=current_report,
        summary=VersionTraceSummary(
            improved_count=counts["improved"],
            regressed_count=counts["regressed"],
            unchanged_count=counts["unchanged"],
            changed_count=counts["changed"],
            high_materiality_count=sum(
                change.materiality == "high" for change in check_changes
            ),
            added_statement_count=statement_counts["added"],
            removed_statement_count=statement_counts["removed"],
            modified_statement_count=statement_counts["modified"],
        ),
        check_changes=check_changes,
        material_changes=material_changes,
        statement_changes=statement_changes,
        new_warnings=sorted(current_warnings - previous_warnings),
        resolved_warnings=sorted(previous_warnings - current_warnings),
        disclaimer=VERSION_DISCLAIMER,
    )
