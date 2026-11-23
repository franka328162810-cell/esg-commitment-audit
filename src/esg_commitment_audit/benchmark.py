from __future__ import annotations

import hashlib
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import yaml

from .api import audit_revisability_bytes
from .benchmark_models import (
    BenchmarkCaseResult,
    BenchmarkDataset,
    BenchmarkGateResult,
    BenchmarkMetrics,
    BenchmarkMismatch,
    BenchmarkReport,
    BenchmarkThresholds,
)
from .revisability import CORE_RULES
from .revisability_models import (
    REVISABILITY_METHODOLOGY_VERSION,
    EvidenceGrade,
)

POSITIVE_GRADES = {
    EvidenceGrade.ASSERTED,
    EvidenceGrade.DOCUMENTED,
    EvidenceGrade.CONTRADICTED,
}


@dataclass(frozen=True)
class Observation:
    split: str
    document_id: str
    check_key: str
    expected: EvidenceGrade
    actual: EvidenceGrade
    evidence_count: int
    rationale: str | None
    evidence_excerpt: str | None


def load_benchmark_dataset(path: str | Path) -> BenchmarkDataset:
    dataset_path = Path(path)
    data = yaml.safe_load(dataset_path.read_text(encoding="utf-8"))
    return BenchmarkDataset.model_validate(data)


def _validate_dataset(dataset: BenchmarkDataset) -> None:
    required_keys = {rule.key for rule in CORE_RULES}
    if dataset.methodology_version != REVISABILITY_METHODOLOGY_VERSION:
        raise ValueError(
            "Benchmark methodology does not match the frozen rule methodology: "
            f"{dataset.methodology_version} != {REVISABILITY_METHODOLOGY_VERSION}"
        )

    document_ids = [document.id for document in dataset.documents]
    if len(document_ids) != len(set(document_ids)):
        raise ValueError("Benchmark document IDs must be unique.")

    source_files = [document.source_file for document in dataset.documents]
    if len(source_files) != len(set(source_files)):
        raise ValueError("Benchmark source files must be unique.")

    split_counts = Counter(document.split for document in dataset.documents)
    if split_counts["calibration"] == 0 or split_counts["evaluation"] == 0:
        raise ValueError(
            "Benchmark requires at least one calibration and one evaluation document."
        )

    for document in dataset.documents:
        expected_keys = set(document.expected_grades)
        extra = sorted(expected_keys - required_keys)
        if extra:
            raise ValueError(
                f"{document.id}: expected grades contain unknown core controls: {extra}."
            )

        evidence_keys = set(document.evidence)
        positive_keys = {
            key
            for key, grade in document.expected_grades.items()
            if grade in POSITIVE_GRADES
        }
        unexpected_evidence = sorted(evidence_keys - positive_keys)
        if unexpected_evidence:
            raise ValueError(
                f"{document.id}: evidence annotations point to controls that are "
                f"not expected to be non-absent: {unexpected_evidence}."
            )
        if positive_keys and not evidence_keys:
            raise ValueError(
                f"{document.id}: at least one non-absent label needs a short "
                "evidence annotation."
            )


def _safe_source_path(sources_dir: Path, source_file: str) -> Path:
    root = sources_dir.resolve()
    candidate = (root / source_file).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError(f"Source file escapes the benchmark directory: {source_file}")
    if not candidate.is_file():
        raise ValueError(f"Benchmark source file not found: {candidate}")
    return candidate


def _ratio(numerator: int, denominator: int) -> float:
    return 1.0 if denominator == 0 else numerator / denominator


def _metrics(
    observations: list[Observation],
    thresholds: BenchmarkThresholds,
) -> BenchmarkMetrics:
    total = len(observations)
    exact = sum(item.expected == item.actual for item in observations)
    expected_positive = [
        item for item in observations if item.expected in POSITIVE_GRADES
    ]
    predicted_positive = [
        item for item in observations if item.actual in POSITIVE_GRADES
    ]
    true_positive = [
        item
        for item in observations
        if item.expected in POSITIVE_GRADES and item.actual in POSITIVE_GRADES
    ]
    false_positive = [
        item
        for item in observations
        if item.expected == EvidenceGrade.ABSENT and item.actual in POSITIVE_GRADES
    ]
    false_negative = [
        item
        for item in observations
        if item.expected in POSITIVE_GRADES and item.actual == EvidenceGrade.ABSENT
    ]
    grade_mismatch = [item for item in true_positive if item.expected != item.actual]

    expected_documented = [
        item for item in observations if item.expected == EvidenceGrade.DOCUMENTED
    ]
    predicted_documented = [
        item for item in observations if item.actual == EvidenceGrade.DOCUMENTED
    ]
    documented_true_positive = [
        item
        for item in observations
        if item.actual == EvidenceGrade.DOCUMENTED
        and item.expected == EvidenceGrade.DOCUMENTED
    ]
    positive_with_evidence = sum(
        item.actual in POSITIVE_GRADES and item.evidence_count > 0
        for item in observations
    )

    precision = _ratio(len(true_positive), len(predicted_positive))
    recall = _ratio(len(true_positive), len(expected_positive))
    return BenchmarkMetrics(
        total_decisions=total,
        exact_correct=exact,
        exact_grade_accuracy=_ratio(exact, total),
        expected_positive_count=len(expected_positive),
        predicted_positive_count=len(predicted_positive),
        true_positive_count=len(true_positive),
        false_positive_count=len(false_positive),
        false_negative_count=len(false_negative),
        grade_mismatch_count=len(grade_mismatch),
        positive_precision=precision,
        positive_recall=recall,
        positive_f1=_ratio(2 * precision * recall, precision + recall),
        documented_precision=_ratio(
            len(documented_true_positive), len(predicted_documented)
        ),
        documented_recall=_ratio(
            len(documented_true_positive), len(expected_documented)
        ),
        predicted_positive_evidence_coverage=_ratio(
            positive_with_evidence, len(predicted_positive)
        ),
    )


def _mismatch_kind(
    expected: EvidenceGrade,
    actual: EvidenceGrade,
) -> str:
    if expected == EvidenceGrade.ABSENT and actual in POSITIVE_GRADES:
        return "false_positive"
    if expected in POSITIVE_GRADES and actual == EvidenceGrade.ABSENT:
        return "false_negative"
    return "grade_mismatch"


def audit_revisability_benchmark(
    dataset_path: str | Path,
    sources_dir: str | Path,
) -> BenchmarkReport:
    dataset = load_benchmark_dataset(dataset_path)
    _validate_dataset(dataset)
    sources_root = Path(sources_dir)

    observations: list[Observation] = []
    mismatches: list[BenchmarkMismatch] = []
    case_results: list[BenchmarkCaseResult] = []
    required_keys = {rule.key for rule in CORE_RULES}

    for document in dataset.documents:
        source_path = _safe_source_path(sources_root, document.source_file)
        source_data = source_path.read_bytes()
        actual_sha256 = hashlib.sha256(source_data).hexdigest()
        if actual_sha256.lower() != document.sha256.lower():
            raise ValueError(
                f"{document.id}: SHA-256 mismatch; expected {document.sha256}, "
                f"found {actual_sha256}."
            )

        report = audit_revisability_bytes(
            source_data,
            source_path.name,
            profile="general",
        )
        checks = {
            check.key: check
            for dimension in report.dimensions
            for check in dimension.checks
        }
        differences: list[str] = []

        for check_key in required_keys:
            expected = document.expected_grades.get(
                check_key,
                EvidenceGrade.ABSENT,
            )
            check = checks[check_key]
            observation = Observation(
                split=document.split,
                document_id=document.id,
                check_key=check_key,
                expected=expected,
                actual=check.grade,
                evidence_count=len(check.evidence),
                rationale=(
                    document.evidence[check_key].rationale
                    if check_key in document.evidence
                    else None
                ),
                evidence_excerpt=(
                    check.evidence[0].excerpt if check.evidence else None
                ),
            )
            observations.append(observation)
            if expected != check.grade:
                differences.append(check_key)
                mismatches.append(
                    BenchmarkMismatch(
                        document_id=document.id,
                        split=document.split,
                        check_key=check_key,
                        expected_grade=expected,
                        actual_grade=check.grade,
                        kind=_mismatch_kind(expected, check.grade),
                        rationale=observation.rationale,
                        evidence_excerpt=observation.evidence_excerpt,
                    )
                )

        case_results.append(
            BenchmarkCaseResult(
                document_id=document.id,
                title=document.title,
                jurisdiction=document.jurisdiction,
                instrument_type=document.instrument_type,
                capture_type=document.capture_type,
                split=document.split,
                source_sha256=actual_sha256,
                actual_grades={key: check.grade for key, check in checks.items()},
                differences=differences,
            )
        )

    overall = _metrics(observations, dataset.thresholds)
    calibration = _metrics(
        [item for item in observations if item.split == "calibration"],
        dataset.thresholds,
    )
    evaluation = _metrics(
        [item for item in observations if item.split == "evaluation"],
        dataset.thresholds,
    )
    grades = [grade.value for grade in EvidenceGrade]
    matrix_counts = Counter(
        (item.expected.value, item.actual.value) for item in observations
    )
    confusion_matrix = {
        expected: {actual: matrix_counts[(expected, actual)] for actual in grades}
        for expected in grades
    }

    exact_gate = (
        min(
            overall.exact_grade_accuracy,
            calibration.exact_grade_accuracy,
            evaluation.exact_grade_accuracy,
        )
        >= dataset.thresholds.minimum_exact_grade_accuracy
    )
    precision_gate = (
        min(overall.positive_precision, evaluation.positive_precision)
        >= dataset.thresholds.minimum_positive_precision
    )
    recall_gate = (
        min(overall.positive_recall, evaluation.positive_recall)
        >= dataset.thresholds.minimum_positive_recall
    )
    evidence_gate = (
        min(
            overall.predicted_positive_evidence_coverage,
            evaluation.predicted_positive_evidence_coverage,
        )
        >= dataset.thresholds.minimum_evidence_coverage
    )
    passed_gate = BenchmarkGateResult(
        exact_grade_accuracy=exact_gate,
        positive_precision=precision_gate,
        positive_recall=recall_gate,
        evidence_coverage=evidence_gate,
        passed=all((exact_gate, precision_gate, recall_gate, evidence_gate)),
    )

    return BenchmarkReport(
        generated_at=datetime.now(UTC),
        benchmark_id=dataset.benchmark_id,
        benchmark_version=dataset.benchmark_version,
        frozen_at=dataset.frozen_at,
        methodology_version=dataset.methodology_version,
        title=dataset.title,
        description=dataset.description,
        claim_boundary=dataset.claim_boundary,
        thresholds=dataset.thresholds,
        overall=overall,
        calibration=calibration,
        evaluation=evaluation,
        confusion_matrix=confusion_matrix,
        gate=passed_gate,
        mismatches=mismatches,
        case_results=case_results,
    )
