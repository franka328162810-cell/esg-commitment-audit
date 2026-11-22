from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class CheckStatus(str, Enum):
    PRESENT = "present"
    PARTIAL = "partial"
    MISSING = "missing"


class DocumentBlock(BaseModel):
    block_id: str
    text: str
    paragraph_index: int
    page_number: int | None = None
    section: str | None = None
    is_heading: bool = False
    source_type: Literal["paragraph", "table"] = "paragraph"
    table_role: Literal["target", "progress", "neutral"] | None = None


class IngestedDocument(BaseModel):
    filename: str
    extension: str
    sha256: str
    character_count: int
    blocks: list[DocumentBlock]
    warnings: list[str] = Field(default_factory=list)


class EvidenceSpan(BaseModel):
    block_id: str
    paragraph_index: int
    unit_index: int | None = None
    page_number: int | None = None
    section: str | None = None
    source_type: Literal["paragraph", "table"] = "paragraph"
    table_role: Literal["target", "progress", "neutral"] | None = None
    text: str
    excerpt: str


class CommitmentFacts(BaseModel):
    quantitative_expressions: list[str] = Field(default_factory=list)
    target_percentages: list[float] = Field(default_factory=list)
    baseline_year: int | None = None
    target_year: int | None = None
    all_years: list[int] = Field(default_factory=list)
    milestone_years: list[int] = Field(default_factory=list)
    scopes_covered: list[str] = Field(default_factory=list)
    reporting_standards: list[str] = Field(default_factory=list)
    responsible_bodies: list[str] = Field(default_factory=list)
    assurance_terms: list[str] = Field(default_factory=list)
    reporting_terms: list[str] = Field(default_factory=list)
    binding_terms: list[str] = Field(default_factory=list)
    remedy_terms: list[str] = Field(default_factory=list)
    review_terms: list[str] = Field(default_factory=list)
    revision_trigger_terms: list[str] = Field(default_factory=list)
    withdrawal_terms: list[str] = Field(default_factory=list)
    mitigation_terms: list[str] = Field(default_factory=list)
    conditional_terms: list[str] = Field(default_factory=list)
    method_terms: list[str] = Field(default_factory=list)
    staged_terms: list[str] = Field(default_factory=list)


class CommitmentRecord(BaseModel):
    commitment_id: str
    candidate_key: str
    text: str
    strength: Literal["strong", "medium", "weak"]
    extraction_confidence: float = Field(ge=0.0, le=1.0)
    category: Literal["E", "S", "G"]
    subcategory: str
    evidence: EvidenceSpan
    related_evidence: list[EvidenceSpan] = Field(default_factory=list)
    duplicate_evidence: list[EvidenceSpan] = Field(default_factory=list)
    evidence_by_fact: dict[str, list[EvidenceSpan]] = Field(default_factory=dict)
    facts: CommitmentFacts


class CheckResult(BaseModel):
    key: str
    label: str
    status: CheckStatus
    weight: float = Field(ge=0.0, le=1.0)
    points: float = Field(ge=0.0, le=1.0)
    evidence: list[EvidenceSpan] = Field(default_factory=list)
    note: str


class DimensionResult(BaseModel):
    key: Literal["V_obs", "V_enf", "V_rev"]
    label: str
    score: float = Field(ge=0.0, le=1.0)
    checks: list[CheckResult]


class CommitmentAudit(BaseModel):
    commitment_id: str
    candidate_key: str
    text: str
    strength: Literal["strong", "medium", "weak"]
    extraction_confidence: float = Field(ge=0.0, le=1.0)
    category: Literal["E", "S", "G"]
    subcategory: str
    evidence: EvidenceSpan
    facts: CommitmentFacts
    dimensions: list[DimensionResult]
    crv_score: float = Field(ge=0.0, le=1.0)
    grade: str
    warnings: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class DocumentSummary(BaseModel):
    filename: str
    extension: str
    sha256: str
    character_count: int
    block_count: int
    parse_warnings: list[str] = Field(default_factory=list)


class ReportSummary(BaseModel):
    commitment_count: int
    average_crv: float | None = None
    high_structure_count: int
    moderate_structure_count: int
    limited_structure_count: int
    document_warnings: list[str] = Field(default_factory=list)


class WeightPreset(BaseModel):
    name: str
    V_obs: float
    V_enf: float
    V_rev: float


class AuditReport(BaseModel):
    report_version: str = "0.2.0"
    methodology_version: str = "CRV-ESG-structure-v0.1"
    generated_at: datetime
    document: DocumentSummary
    weights: WeightPreset
    summary: ReportSummary
    commitments: list[CommitmentAudit]
    disclaimer: str


class GovernanceCheck(BaseModel):
    key: str
    label: str
    status: CheckStatus
    note: str
    evidence: list[EvidenceSpan] = Field(default_factory=list)


class GovernanceSummary(BaseModel):
    check_count: int
    present_count: int
    partial_count: int
    missing_count: int
    document_warnings: list[str] = Field(default_factory=list)


class GovernanceReport(BaseModel):
    report_version: str = "0.3.1"
    report_type: Literal["recursive-freedom"] = "recursive-freedom"
    methodology_version: str = "RFP-AI-policy-structure-v0.2"
    generated_at: datetime
    document: DocumentSummary
    summary: GovernanceSummary
    checks: list[GovernanceCheck]
    recommendations: list[str] = Field(default_factory=list)
    disclaimer: str
