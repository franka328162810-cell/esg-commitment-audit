from __future__ import annotations

from pathlib import Path

from esg_commitment_audit.esg_cli import main


def test_esg_product_cli_writes_markdown(tmp_path: Path, capsys) -> None:
    output = tmp_path / "esg-audit.md"
    exit_code = main(
        [
            "audit",
            "examples/strong_commitment.txt",
            "--output",
            str(output),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "ESG Commitment Audit Report" in output.read_text(encoding="utf-8")
    assert str(output.resolve()) in captured.out
