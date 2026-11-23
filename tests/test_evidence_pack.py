from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from esg_commitment_audit.evidence_pack import (
    audit_evidence_pack,
    audit_evidence_pack_zip,
    seal_evidence_pack_manifest,
)
from esg_commitment_audit.evidence_pack_report import (
    render_evidence_pack_html,
    render_evidence_pack_json,
    render_evidence_pack_markdown,
)
from esg_commitment_audit.revisability_cli import main
from esg_commitment_audit.revisability_models import EvidenceGrade
from esg_commitment_audit.web import create_app


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_pack(tmp_path: Path, *, mismatched_hash: bool = False) -> Path:
    policy = Path("examples/revisability_strong_policy.md").read_bytes()
    (tmp_path / "policy.md").write_bytes(policy)

    artifacts = {
        "approval-record.txt": b"AI Governance Board approved revision 2.1 on 2026-11-20.",
        "rollback-drill.txt": b"Rollback drill completed 2026-11-18 with all checks passed.",
        "monitoring-snapshot.json": b'{"metric":"drift","threshold":0.1,"status":"ok"}',
        "independent-review.txt": b"Independent reviewer examined oversight evidence.",
    }
    for name, data in artifacts.items():
        (tmp_path / name).write_bytes(data)

    approval_hash = _sha256(artifacts["approval-record.txt"])
    if mismatched_hash:
        approval_hash = "0" * 64

    manifest = {
        "manifest_version": "1.0",
        "organization": "Example AI Company",
        "reviewed_at": "2026-11-23",
        "profile": "general",
        "base_document": "policy.md",
        "artifacts": [
            {
                "path": "approval-record.txt",
                "artifact_type": "approval_record",
                "issued_at": "2026-11-20",
                "issuer": "AI Governance Board",
                "supports": ["revision_authority"],
                "expected_sha256": approval_hash,
            },
            {
                "path": "rollback-drill.txt",
                "artifact_type": "rollback_drill",
                "issued_at": "2026-11-18",
                "issuer": "Incident Response Team",
                "supports": ["rollback_evidence"],
                "expected_sha256": _sha256(artifacts["rollback-drill.txt"]),
            },
            {
                "path": "monitoring-snapshot.json",
                "artifact_type": "monitoring_snapshot",
                "issued_at": "2026-11-19",
                "issuer": "AI Operations",
                "supports": ["monitoring_metrics"],
                "expected_sha256": _sha256(artifacts["monitoring-snapshot.json"]),
            },
            {
                "path": "independent-review.txt",
                "artifact_type": "independent_review",
                "issued_at": "2026-11-21",
                "issuer": "Independent AI Review Panel",
                "supports": ["independent_oversight"],
                "independent": True,
                "expected_sha256": _sha256(artifacts["independent-review.txt"]),
            },
        ],
    }
    manifest_path = tmp_path / "manifest.yaml"
    manifest_path.write_text(
        yaml.safe_dump(manifest, sort_keys=False),
        encoding="utf-8",
    )
    return manifest_path


def _write_zip(pack_path: Path) -> Path:
    archive_path = pack_path.parent / "evidence-pack.zip"
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in pack_path.parent.iterdir():
            if path == archive_path or not path.is_file():
                continue
            archive.write(path, path.name)
    return archive_path


def test_evidence_pack_promotes_documented_controls(tmp_path: Path) -> None:
    report = audit_evidence_pack(_write_pack(tmp_path))
    promotions = {item.check_key: item for item in report.promotions}

    assert all(
        item.eligible_for_operational_evidence for item in report.artifact_inventory
    )
    assert promotions["revision_authority"].baseline_grade == EvidenceGrade.DOCUMENTED
    assert promotions["revision_authority"].proposed_grade == (
        EvidenceGrade.OPERATIONALLY_EVIDENCED
    )
    assert promotions["rollback_evidence"].proposed_grade == (
        EvidenceGrade.OPERATIONALLY_EVIDENCED
    )
    assert promotions["independent_oversight"].proposed_grade == (
        EvidenceGrade.INDEPENDENTLY_VERIFIED
    )
    assert all(item.requires_human_confirmation for item in report.promotions)


def test_hash_mismatch_prevents_grade_promotion(tmp_path: Path) -> None:
    report = audit_evidence_pack(_write_pack(tmp_path, mismatched_hash=True))
    approval = next(
        item for item in report.artifact_inventory if item.path == "approval-record.txt"
    )

    assert approval.hash_matches is False
    assert approval.eligible_for_operational_evidence is False
    assert "revision_authority" not in {item.check_key for item in report.promotions}
    assert any("does not match" in item for item in approval.warnings)


def test_artifact_path_cannot_escape_manifest_directory(tmp_path: Path) -> None:
    manifest = _write_pack(tmp_path)
    data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    data["artifacts"][0]["path"] = "../../outside.txt"
    manifest.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="escapes the manifest directory"):
        audit_evidence_pack(manifest)


def test_incompatible_artifact_is_warned_not_promoted(tmp_path: Path) -> None:
    manifest = _write_pack(tmp_path)
    data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    data["artifacts"][1]["supports"] = ["notice"]
    manifest.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    report = audit_evidence_pack(manifest)

    assert "notice" not in {item.check_key for item in report.promotions}
    assert any("not compatible with 'notice'" in item for item in report.warnings)


def test_evidence_pack_renderers_include_hash_and_claim_boundary(
    tmp_path: Path,
) -> None:
    report = audit_evidence_pack(_write_pack(tmp_path))
    markdown = render_evidence_pack_markdown(report)
    html = render_evidence_pack_html(report)
    payload = render_evidence_pack_json(report)

    assert "Artifact inventory" in markdown
    assert "Human confirmation" in markdown
    assert "requires human confirmation" in markdown
    assert "true" in markdown
    assert "AI Revisability Evidence-Pack Assessment" in html
    assert "Claim boundary" in html
    assert '"report_type": "ai-revisability-evidence-pack"' in payload


def test_evidence_pack_cli_writes_json(tmp_path: Path, capsys) -> None:
    manifest = _write_pack(tmp_path)
    output = tmp_path / "evidence-pack.json"
    exit_code = main(
        [
            "evidence-pack",
            str(manifest),
            "--format",
            "json",
            "--output",
            str(output),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert output.is_file()
    assert "ai-revisability-evidence-pack" in output.read_text(encoding="utf-8")
    assert str(output.resolve()) in captured.out


def test_evidence_pack_zip_is_validated_in_place(tmp_path: Path) -> None:
    pack_path = _write_pack(tmp_path)
    archive_path = _write_zip(pack_path)

    report = audit_evidence_pack_zip(archive_path)

    assert report.organization == "Example AI Company"
    assert report.promotions
    assert archive_path.is_file()


def test_zip_path_traversal_is_rejected(tmp_path: Path) -> None:
    archive_path = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("../outside.txt", b"not allowed")

    with pytest.raises(ValueError, match="Unsafe ZIP entry path"):
        audit_evidence_pack_zip(archive_path)


def test_seal_manifest_pins_hashes_without_overwriting_source(
    tmp_path: Path,
) -> None:
    manifest_path = _write_pack(tmp_path)
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    for artifact in data["artifacts"]:
        artifact.pop("expected_sha256", None)
    manifest_path.write_text(
        yaml.safe_dump(data, sort_keys=False),
        encoding="utf-8",
    )

    sealed_path = seal_evidence_pack_manifest(
        manifest_path,
        tmp_path / "sealed.yaml",
    )
    sealed = yaml.safe_load(sealed_path.read_text(encoding="utf-8"))

    assert all(item.get("expected_sha256") for item in sealed["artifacts"])
    assert (
        "expected_sha256"
        not in yaml.safe_load(manifest_path.read_text(encoding="utf-8"))["artifacts"][0]
    )


def test_evidence_pack_web_endpoint_accepts_zip(tmp_path: Path) -> None:
    manifest_path = _write_pack(tmp_path)
    archive_path = _write_zip(manifest_path)
    client = TestClient(create_app())

    with archive_path.open("rb") as handle:
        response = client.post(
            "/api/evidence-pack",
            files={"file": ("evidence-pack.zip", handle, "application/zip")},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["report"]["report_type"] == "ai-revisability-evidence-pack"
    assert payload["report"]["promotions"]
