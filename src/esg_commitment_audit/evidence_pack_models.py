from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

from .revisability_models import EvidenceGrade, ReviewProfile

ArtifactType = Literal[
    "policy_document",
    "change_log",
    "approval_record",
    "board_minutes",
    "exception_log",
    "appeal_record",
    "monitoring_snapshot",
    "rollback_drill",
    "evaluation_report",
    "model_signature",
    "independent_review",
    "other",
]


class EvidenceArtifactSpec(BaseModel):
    path: str
    artifact_type: ArtifactType
    issued_at: date | None = None
    issuer: str | None = None
    supports: list[str] = Field(min_length=1)
    independent: bool = False
    expected_sha256: str | None = Field(default=None, pattern=r"^[0-9a-fA-F]{64}$")
    note: str | None = None


class EvidencePackManifest(BaseModel):
    manifest_version: Literal["1.0"] = "1.0"
    organization: str = Field(min_length=1, max_length=200)
    reviewed_at: date
    profile: ReviewProfile = "general"
    base_document: str
    artifacts: list[EvidenceArtifactSpec] = Field(min_length=1)


class ArtifactInventoryItem(BaseModel):
    path: str
    artifact_type: ArtifactType
    exists: bool
    byte_count: int | None = None
    actual_sha256: str | None = None
    hash_matches: bool | None = None
    issued_at: date | None = None
    issuer: str | None = None
    independent: bool = False
    supports: list[str]
    eligible_for_operational_evidence: bool
    warnings: list[str] = Field(default_factory=list)


class ControlPromotion(BaseModel):
    check_key: str
    baseline_grade: EvidenceGrade
    proposed_grade: EvidenceGrade
    supporting_artifacts: list[str]
    rationale: str
    requires_human_confirmation: bool = True


class UnresolvedControl(BaseModel):
    check_key: str
    baseline_grade: EvidenceGrade
    missing_artifact_types: list[ArtifactType]
    note: str


class EvidencePackReport(BaseModel):
    report_version: str = "0.6.0"
    report_type: Literal["ai-revisability-evidence-pack"] = (
        "ai-revisability-evidence-pack"
    )
    generated_at: datetime
    organization: str
    reviewed_at: date
    profile: ReviewProfile
    base_document: str
    base_document_sha256: str
    artifact_inventory: list[ArtifactInventoryItem]
    baseline_grades: dict[str, EvidenceGrade]
    promotions: list[ControlPromotion]
    unresolved_controls: list[UnresolvedControl]
    warnings: list[str] = Field(default_factory=list)
    disclaimer: str
