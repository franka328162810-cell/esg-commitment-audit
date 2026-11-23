from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
import yaml

from esg_commitment_audit.benchmark import audit_revisability_benchmark
from esg_commitment_audit.revisability_cli import main
from esg_commitment_audit.revisability_models import (
    REVISABILITY_METHODOLOGY_VERSION,
)


def _dataset(tmp_path: Path, *, digest: str | None = None) -> Path:
    text = b"We may update this policy. This is a short policy statement."
    evaluation_text = b"No relevant governance control is stated here."
    source_dir = tmp_path / "sources"
    source_dir.mkdir()
    source_path = source_dir / "policy.txt"
    source_path.write_bytes(text)
    (source_dir / "index.txt").write_bytes(evaluation_text)
    dataset = {
        "benchmark_id": "test-benchmark",
        "benchmark_version": "1.0.0",
        "frozen_at": "2026-11-23",
        "methodology_version": REVISABILITY_METHODOLOGY_VERSION,
        "title": "Test Benchmark",
        "description": "Synthetic benchmark fixture.",
        "claim_boundary": "This fixture tests the scorer, not policy quality.",
        "documents": [
            {
                "id": "test-policy",
                "title": "Test Policy",
                "url": "https://example.com/test-policy",
                "jurisdiction": "Test",
                "instrument_type": "company_policy",
                "capture_type": "full_text",
                "language": "en",
                "source_file": "policy.txt",
                "sha256": digest or hashlib.sha256(text).hexdigest(),
                "split": "calibration",
                "expected_grades": {"revision_authority": "asserted"},
                "evidence": {
                    "revision_authority": {
                        "locator": "sentence 1",
                        "excerpt": "We may update this policy.",
                        "rationale": "The operator asserts revision authority.",
                    }
                },
            },
            {
                "id": "test-index",
                "title": "Test Index",
                "url": "https://example.com/test-index",
                "jurisdiction": "Test",
                "instrument_type": "official_policy",
                "capture_type": "official_index",
                "language": "en",
                "source_file": "index.txt",
                "sha256": hashlib.sha256(evaluation_text).hexdigest(),
                "split": "evaluation",
                "expected_grades": {},
            },
        ],
    }
    path = tmp_path / "dataset.yaml"
    path.write_text(yaml.safe_dump(dataset, sort_keys=False), encoding="utf-8")
    return path


def test_benchmark_scores_all_core_controls(tmp_path: Path) -> None:
    report = audit_revisability_benchmark(_dataset(tmp_path), tmp_path / "sources")

    assert report.overall.total_decisions == 56
    assert report.overall.positive_recall == 1.0
    assert report.overall.positive_precision == 1.0
    assert report.overall.predicted_positive_evidence_coverage == 1.0
    assert report.gate.passed is True


def test_benchmark_rejects_source_hash_mismatch(tmp_path: Path) -> None:
    dataset = _dataset(tmp_path, digest="0" * 64)

    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        audit_revisability_benchmark(dataset, tmp_path / "sources")


def test_benchmark_cli_writes_report(tmp_path: Path, capsys) -> None:
    dataset = _dataset(tmp_path)
    output = tmp_path / "benchmark.json"

    exit_code = main(
        [
            "benchmark",
            str(dataset),
            "--format",
            "json",
            "--output",
            str(output),
            "--strict",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert output.is_file()
    assert "ai-revisability-benchmark" in output.read_text(encoding="utf-8")
    assert str(output.resolve()) in captured.out
