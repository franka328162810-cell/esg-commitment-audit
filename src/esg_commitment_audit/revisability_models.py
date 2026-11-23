from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

from .models import DocumentSummary, EvidenceSpan

REVISABILITY_REPORT_VERSION = "0.5.0.dev1"
REVISABILITY_METHODOLOGY_VERSION = "RFP-AI-revisability-document-v0.2"

ReviewProfile = Literal[
    "general",
    "news_media",
    "advertising",
    "insurance",
    "industrial_design",
]


class EvidenceGrade(str, Enum):
    ABSENT = "absent"
    ASSERTED = "asserted"
    DOCUMENTED = "documented"
    OPERATIONALLY_EVIDENCED = "operationally_evidenced"
    INDEPENDENTLY_VERIFIED = "independently_verified"
    CONTRADICTED = "contradicted"
    NOT_ASSESSABLE = "not_assessable"


class RevisabilityCheck(BaseModel):
    key: str
    label: str
    grade: EvidenceGrade
    rationale: str
    evidence: list[EvidenceSpan] = Field(default_factory=list)
    required_artifacts: list[str] = Field(default_factory=list)
    recommendation: str


class RevisabilityDimension(BaseModel):
    key: str
    label: str
    checks: list[RevisabilityCheck]


class RevisabilitySummary(BaseModel):
    dimension_count: int
    check_count: int
    absent_count: int
    asserted_count: int
    documented_count: int
    operationally_evidenced_count: int
    independently_verified_count: int
    contradicted_count: int
    not_assessable_count: int


class RevisabilityReport(BaseModel):
    report_version: str = REVISABILITY_REPORT_VERSION
    report_type: Literal["ai-alignment-revisability"] = "ai-alignment-revisability"
    methodology_version: str = REVISABILITY_METHODOLOGY_VERSION
    generated_at: datetime
    profile: ReviewProfile
    profile_label: str
    document: DocumentSummary
    summary: RevisabilitySummary
    dimensions: list[RevisabilityDimension]
    warnings: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    evidence_requests: list[str] = Field(default_factory=list)
    disclaimer: str
