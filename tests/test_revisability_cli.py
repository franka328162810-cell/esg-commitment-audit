from __future__ import annotations

from pathlib import Path

from esg_commitment_audit.revisability_cli import main


def test_product_cli_runs_single_document_audit(tmp_path: Path, capsys) -> None:
    output = tmp_path / "audit.md"
    exit_code = main(
        [
            "audit",
            "examples/revisability_strong_policy.md",
            "--profile",
            "news_media",
            "--output",
            str(output),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "AI Alignment Revisability Audit" in output.read_text(encoding="utf-8")
    assert str(output.resolve()) in captured.out


def test_product_cli_compares_versions(tmp_path: Path, capsys) -> None:
    output = tmp_path / "compare.json"
    exit_code = main(
        [
            "compare",
            "examples/revisability_policy_v1.md",
            "examples/revisability_policy_v2.md",
            "--format",
            "json",
            "--output",
            str(output),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert '"report_type": "ai-revisability-version-trace"' in output.read_text(
        encoding="utf-8"
    )
    assert str(output.resolve()) in captured.out
