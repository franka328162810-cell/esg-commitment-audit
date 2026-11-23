from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

from .revisability_models import EvidenceGrade

BenchmarkSplit = Literal["calibration", "evaluation"]
MismatchKind = Literal["false_positive", "false_negative", "grade_mismatch"]
InstrumentType = Literal[
    "company_policy",
    "voluntary_framework",
    "binding_law",
    "binding_regulation",
    "executive_order",
    "regulatory_guidance",
    "official_enactment_summary",
    "official_policy",
]
CaptureType = Literal["full_text", "official_summary", "official_index"]


class BenchmarkEvidence(BaseModel):
    locator: str = Field(min_length=1, max_length=200)
    excerpt: str = Field(min_length=1, max_length=500)
    rationale: str = Field(min_length=1, max_length=1000)


class BenchmarkThresholds(BaseModel):
    minimum_exact_grade_accuracy: float = Field(default=0.80, ge=0, le=1)
    minimum_positive_precision: float = Field(default=0.85, ge=0, le=1)
    minimum_positive_recall: float = Field(default=0.85, ge=0, le=1)
    minimum_evidence_coverage: float = Field(default=1.0, ge=0, le=1)


class BenchmarkDocument(BaseModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]+$")
    title: str = Field(min_length=1, max_length=300)
    url: str = Field(min_length=1, max_length=1000)
    jurisdiction: str = Field(min_length=1, max_length=120)
    instrument_type: InstrumentType
    capture_type: CaptureType
    language: Literal["en", "zh"]
    source_file: str = Field(min_length=1, max_length=300)
    sha256: str = Field(pattern=r"^[0-9a-fA-F]{64}$")
    split: BenchmarkSplit
    expected_grades: dict[str, EvidenceGrade]
    evidence: dict[str, BenchmarkEvidence] = Field(default_factory=dict)
    notes: str | None = Field(default=None, max_length=2000)


class BenchmarkDataset(BaseModel):
    benchmark_id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]+$")
    benchmark_version: str = Field(min_length=1, max_length=50)
    frozen_at: date
    methodology_version: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=300)
    description: str = Field(min_length=1, max_length=3000)
    claim_boundary: str = Field(min_length=1, max_length=3000)
    thresholds: BenchmarkThresholds = Field(default_factory=BenchmarkThresholds)
    documents: list[BenchmarkDocument] = Field(min_length=1)


class BenchmarkMetrics(BaseModel):
    total_decisions: int
    exact_correct: int
    exact_grade_accuracy: float
    expected_positive_count: int
    predicted_positive_count: int
    true_positive_count: int
    false_positive_count: int
    false_negative_count: int
    grade_mismatch_count: int
    positive_precision: float
    positive_recall: float
    positive_f1: float
    documented_precision: float
    documented_recall: float
    predicted_positive_evidence_coverage: float


class BenchmarkGateResult(BaseModel):
    exact_grade_accuracy: bool
    positive_precision: bool
    positive_recall: bool
    evidence_coverage: bool
    passed: bool


class BenchmarkMismatch(BaseModel):
    document_id: str
    split: BenchmarkSplit
    check_key: str
    expected_grade: EvidenceGrade
    actual_grade: EvidenceGrade
    kind: MismatchKind
    rationale: str | None = None
    evidence_excerpt: str | None = None


class BenchmarkCaseResult(BaseModel):
    document_id: str
    title: str
    jurisdiction: str
    instrument_type: InstrumentType
    capture_type: CaptureType
    split: BenchmarkSplit
    source_sha256: str
    actual_grades: dict[str, EvidenceGrade]
    differences: list[str] = Field(default_factory=list)


class BenchmarkReport(BaseModel):
    report_version: str = "0.5.0.dev1"
    report_type: Literal["ai-revisability-benchmark"] = "ai-revisability-benchmark"
    generated_at: datetime
    benchmark_id: str
    benchmark_version: str
    frozen_at: date
    methodology_version: str
    title: str
    description: str
    claim_boundary: str
    thresholds: BenchmarkThresholds
    overall: BenchmarkMetrics
    calibration: BenchmarkMetrics
    evaluation: BenchmarkMetrics
    confusion_matrix: dict[str, dict[str, int]]
    gate: BenchmarkGateResult
    mismatches: list[BenchmarkMismatch]
    case_results: list[BenchmarkCaseResult]
