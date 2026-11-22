from __future__ import annotations

from pathlib import Path

from esg_commitment_audit.cli import main


def test_cli_prints_markdown(capsys) -> None:
    exit_code = main(["audit", "examples/strong_commitment.txt"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "# ESG Commitment Audit Report" in captured.out


def test_cli_writes_json(tmp_path: Path, capsys) -> None:
    output = tmp_path / "report.json"
    exit_code = main(
        [
            "audit",
            "examples/strong_commitment.txt",
            "--format",
            "json",
            "--output",
            str(output),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert output.is_file()
    assert '"report_version": "0.2.0"' in output.read_text(encoding="utf-8")
    assert str(output.resolve()) in captured.out


def test_cli_returns_error_for_missing_file(capsys) -> None:
    exit_code = main(["audit", "examples/does-not-exist.txt"])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "not found" in captured.err


def test_revisability_cli_writes_html(tmp_path: Path, capsys) -> None:
    output = tmp_path / "revisability.html"
    exit_code = main(
        [
            "revisability",
            "examples/revisability_strong_policy.md",
            "--profile",
            "news_media",
            "--format",
            "html",
            "--output",
            str(output),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert output.is_file()
    assert "AI Alignment Revisability Audit" in output.read_text(encoding="utf-8")
    assert str(output.resolve()) in captured.out


def test_revisability_version_cli_writes_markdown(tmp_path: Path, capsys) -> None:
    output = tmp_path / "version-trace.md"
    exit_code = main(
        [
            "revisability-version",
            "examples/revisability_policy_v1.md",
            "examples/revisability_policy_v2.md",
            "--format",
            "markdown",
            "--output",
            str(output),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert output.is_file()
    assert "AI Alignment Revisability Version Trace" in output.read_text(
        encoding="utf-8"
    )
    assert str(output.resolve()) in captured.out
