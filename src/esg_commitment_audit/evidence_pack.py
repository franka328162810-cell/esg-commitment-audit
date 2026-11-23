from __future__ import annotations

import hashlib
import shutil
import tempfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath

import yaml

from .api import audit_revisability_bytes
from .evidence_pack_models import (
    ArtifactInventoryItem,
    ArtifactType,
    ControlPromotion,
    EvidenceArtifactSpec,
    EvidencePackManifest,
    EvidencePackReport,
    UnresolvedControl,
)
from .revisability_models import EvidenceGrade

MAX_ARTIFACT_BYTES = 50 * 1024 * 1024
MAX_TOTAL_ARTIFACT_BYTES = 200 * 1024 * 1024
MAX_BUNDLE_ENTRIES = 1000
MAX_COMPRESSION_RATIO = 1000

PACK_DISCLAIMER = (
    "This evidence-pack review verifies declared file hashes and proposes "
    "evidence-grade changes. It does not prove that the underlying event "
    "occurred, that the issuer is authoritative, or that an independent review "
    "was adequate. Every E3 or E4 proposal requires human confirmation."
)

ARTIFACT_CONTROL_MAP: dict[ArtifactType, set[str]] = {
    "policy_document": set(),
    "change_log": {
        "version_identifier",
        "change_log",
        "prior_version_access",
    },
    "approval_record": {
        "accountable_owner",
        "revision_authority",
        "protected_clauses",
        "capability_gate",
    },
    "board_minutes": {
        "accountable_owner",
        "revision_authority",
        "independent_oversight",
        "stakeholder_participation",
    },
    "exception_log": {
        "anti_abuse",
        "monitoring_metrics",
        "protected_clauses",
    },
    "appeal_record": {
        "appeal",
        "explanation",
        "refusal_exit",
    },
    "monitoring_snapshot": {
        "monitoring_metrics",
        "audit_logs",
        "retention",
        "interruptibility",
    },
    "rollback_drill": {
        "rollback_condition",
        "rollback_authority",
        "rollback_evidence",
        "capability_gate",
        "interruptibility",
    },
    "evaluation_report": {
        "uncertainty",
        "capability_gate",
        "monitoring_metrics",
        "content_provenance",
    },
    "model_signature": {
        "version_identifier",
        "design_provenance",
    },
    "independent_review": {
        "independent_oversight",
        "anti_abuse",
        "protected_clauses",
    },
    "other": set(),
}

CONTROL_ARTIFACT_OPTIONS: dict[str, list[ArtifactType]] = {}
for artifact_type, controls in ARTIFACT_CONTROL_MAP.items():
    for control in controls:
        CONTROL_ARTIFACT_OPTIONS.setdefault(control, []).append(artifact_type)


def load_manifest(path: Path) -> EvidencePackManifest:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return EvidencePackManifest.model_validate(data)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_artifact_path(base_dir: Path, relative: str) -> Path:
    candidate = (base_dir / relative).resolve()
    if not candidate.is_relative_to(base_dir.resolve()):
        raise ValueError(f"Artifact escapes the manifest directory: {relative}")
    return candidate


def _safe_zip_path(root: Path, member_name: str) -> Path:
    normalized = member_name.replace("\\", "/")
    member = PurePosixPath(normalized)
    if (
        member.is_absolute()
        or not member.parts
        or ".." in member.parts
        or any(part in {"", "."} for part in member.parts)
        or any(":" in part for part in member.parts)
    ):
        raise ValueError(f"Unsafe ZIP entry path: {member_name}")
    return root.joinpath(*member.parts)


def _validate_zip_archive(archive: zipfile.ZipFile) -> None:
    entries = archive.infolist()
    if len(entries) > MAX_BUNDLE_ENTRIES:
        raise ValueError(f"Evidence pack exceeds the {MAX_BUNDLE_ENTRIES}-entry limit.")

    total_uncompressed = 0
    seen: set[str] = set()
    for entry in entries:
        if entry.is_dir():
            continue
        normalized = entry.filename.replace("\\", "/")
        if normalized in seen:
            raise ValueError(f"Duplicate ZIP entry: {entry.filename}")
        seen.add(normalized)
        _safe_zip_path(Path("."), normalized)
        if entry.flag_bits & 0x1:
            raise ValueError(
                f"Encrypted ZIP entries are not supported: {entry.filename}"
            )
        file_type = (entry.external_attr >> 16) & 0o170000
        if file_type == 0o120000:
            raise ValueError(f"Symbolic links are not allowed: {entry.filename}")
        if entry.file_size > MAX_ARTIFACT_BYTES:
            raise ValueError(
                f"ZIP entry exceeds the 50 MB per-file limit: {entry.filename}"
            )
        if (
            entry.file_size > 1024 * 1024
            and entry.compress_size > 0
            and entry.file_size / entry.compress_size > MAX_COMPRESSION_RATIO
        ):
            raise ValueError(
                f"ZIP entry has an unsafe compression ratio: {entry.filename}"
            )
        total_uncompressed += entry.file_size

    if total_uncompressed > MAX_TOTAL_ARTIFACT_BYTES:
        raise ValueError("Evidence pack exceeds the 200 MB uncompressed limit.")


def seal_evidence_pack_manifest(
    manifest_path: str | Path,
    output_path: str | Path | None = None,
) -> Path:
    manifest_file = Path(manifest_path).resolve()
    if not manifest_file.is_file():
        raise ValueError(f"Manifest not found: {manifest_file}")
    data = yaml.safe_load(manifest_file.read_text(encoding="utf-8"))
    manifest = EvidencePackManifest.model_validate(data)
    base_dir = manifest_file.parent
    base_path = _safe_artifact_path(base_dir, manifest.base_document)
    if not base_path.is_file():
        raise ValueError(f"Base document not found: {manifest.base_document}")
    if base_path.stat().st_size > MAX_ARTIFACT_BYTES:
        raise ValueError("Base document exceeds the 50 MB per-file limit.")

    total_size = base_path.stat().st_size
    for artifact in manifest.artifacts:
        artifact_path = _safe_artifact_path(base_dir, artifact.path)
        if not artifact_path.is_file():
            raise ValueError(f"Artifact not found: {artifact.path}")
        byte_count = artifact_path.stat().st_size
        if byte_count > MAX_ARTIFACT_BYTES:
            raise ValueError(
                f"Artifact exceeds the 50 MB per-file limit: {artifact.path}"
            )
        total_size += byte_count
        artifact.expected_sha256 = _sha256(artifact_path)
    if total_size > MAX_TOTAL_ARTIFACT_BYTES:
        raise ValueError("Evidence pack exceeds the 200 MB total artifact limit.")

    sealed = manifest.model_dump(mode="json", exclude_none=True)
    final_output = (
        Path(output_path).resolve()
        if output_path is not None
        else manifest_file.with_name(f"{manifest_file.stem}.sealed.yaml")
    )
    if final_output == manifest_file:
        raise ValueError(
            "Sealed manifest output must differ from the editable manifest."
        )
    final_output.parent.mkdir(parents=True, exist_ok=True)
    final_output.write_text(
        yaml.safe_dump(sealed, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return final_output


def _inventory_artifact(
    base_dir: Path,
    spec: EvidenceArtifactSpec,
) -> ArtifactInventoryItem:
    warnings: list[str] = []
    path = _safe_artifact_path(base_dir, spec.path)
    exists = path.is_file()
    byte_count: int | None = None
    actual_hash: str | None = None
    hash_matches: bool | None = None
    eligible = False

    if not exists:
        warnings.append("Artifact file does not exist.")
    else:
        byte_count = path.stat().st_size
        if byte_count > MAX_ARTIFACT_BYTES:
            warnings.append("Artifact exceeds the 50 MB per-file limit.")
        else:
            actual_hash = _sha256(path)
            if spec.expected_sha256:
                hash_matches = actual_hash.lower() == spec.expected_sha256.lower()
                if not hash_matches:
                    warnings.append("Artifact SHA-256 does not match the manifest.")
            else:
                warnings.append("Manifest does not pin an expected SHA-256.")

    if spec.issued_at is None:
        warnings.append("Artifact has no issue date.")
    if not spec.issuer or not spec.issuer.strip():
        warnings.append("Artifact has no issuer.")
    if spec.artifact_type == "independent_review" and not spec.independent:
        warnings.append("Independent-review artifact is not marked independent.")
    if spec.artifact_type in {"other", "policy_document"}:
        warnings.append("Artifact type alone cannot support an operational grade.")

    eligible = (
        exists
        and byte_count is not None
        and byte_count <= MAX_ARTIFACT_BYTES
        and hash_matches is True
        and spec.issued_at is not None
        and bool(spec.issuer and spec.issuer.strip())
        and spec.artifact_type not in {"other", "policy_document"}
    )
    if spec.artifact_type == "independent_review" and not spec.independent:
        eligible = False

    return ArtifactInventoryItem(
        path=spec.path,
        artifact_type=spec.artifact_type,
        exists=exists,
        byte_count=byte_count,
        actual_sha256=actual_hash,
        hash_matches=hash_matches,
        issued_at=spec.issued_at,
        issuer=spec.issuer,
        independent=spec.independent,
        supports=spec.supports,
        eligible_for_operational_evidence=eligible,
        warnings=warnings,
    )


def audit_evidence_pack(
    manifest_path: str | Path,
) -> EvidencePackReport:
    manifest_file = Path(manifest_path).resolve()
    if not manifest_file.is_file():
        raise ValueError(f"Manifest not found: {manifest_file}")
    manifest = load_manifest(manifest_file)
    base_dir = manifest_file.parent

    base_path = _safe_artifact_path(base_dir, manifest.base_document)
    if not base_path.is_file():
        raise ValueError(f"Base document not found: {manifest.base_document}")
    base_data = base_path.read_bytes()
    base_audit = audit_revisability_bytes(
        base_data,
        base_path.name,
        profile=manifest.profile,
    )
    baseline_grades = {
        check.key: check.grade
        for dimension in base_audit.dimensions
        for check in dimension.checks
    }

    inventory = [_inventory_artifact(base_dir, spec) for spec in manifest.artifacts]
    total_size = sum(item.byte_count or 0 for item in inventory)
    warnings: list[str] = []
    if total_size > MAX_TOTAL_ARTIFACT_BYTES:
        warnings.append("Evidence pack exceeds the 200 MB total artifact limit.")

    promotion_map: dict[
        str, list[tuple[EvidenceArtifactSpec, ArtifactInventoryItem]]
    ] = {}
    for spec, item in zip(manifest.artifacts, inventory):
        if not item.eligible_for_operational_evidence:
            continue
        allowed = ARTIFACT_CONTROL_MAP[spec.artifact_type]
        for check_key in spec.supports:
            if check_key not in baseline_grades:
                warnings.append(
                    f"{spec.path}: support target '{check_key}' is not in the audit profile."
                )
                continue
            if check_key not in allowed:
                warnings.append(
                    f"{spec.path}: artifact type '{spec.artifact_type}' is not "
                    f"compatible with '{check_key}'."
                )
                continue
            promotion_map.setdefault(check_key, []).append((spec, item))

    promotions: list[ControlPromotion] = []
    for check_key, support in promotion_map.items():
        baseline = baseline_grades[check_key]
        artifact_paths = sorted({spec.path for spec, _ in support})
        if baseline in {EvidenceGrade.ABSENT, EvidenceGrade.ASSERTED}:
            proposed = EvidenceGrade.DOCUMENTED
            rationale = (
                "Specific artifact evidence supports the control, but the base "
                "governance document does not establish a documented control. "
                "The pack proposes E2 at most."
            )
        elif baseline == EvidenceGrade.DOCUMENTED:
            proposed = EvidenceGrade.OPERATIONALLY_EVIDENCED
            rationale = (
                "A dated, issuer-identified and hash-matched artifact supports "
                "the documented control. Human confirmation is required before E3."
            )
        elif baseline == EvidenceGrade.CONTRADICTED:
            proposed = EvidenceGrade.DOCUMENTED
            rationale = (
                "Artifact evidence may resolve a textual conflict, but the base "
                "document still contains contradictory language."
            )
        else:
            proposed = baseline
            rationale = "Artifact evidence does not change the current grade."

        independent_support = [
            spec
            for spec, item in support
            if item.independent and spec.artifact_type == "independent_review"
        ]
        if check_key == "independent_oversight" and independent_support:
            proposed = EvidenceGrade.INDEPENDENTLY_VERIFIED
            rationale = (
                "A dated, hash-matched independent-review artifact names an "
                "independent issuer. Human confirmation is required before E4."
            )

        if proposed != baseline:
            promotions.append(
                ControlPromotion(
                    check_key=check_key,
                    baseline_grade=baseline,
                    proposed_grade=proposed,
                    supporting_artifacts=artifact_paths,
                    rationale=rationale,
                )
            )

    unresolved: list[UnresolvedControl] = []
    promoted_keys = {item.check_key for item in promotions}
    for check_key, grade in baseline_grades.items():
        if check_key in promoted_keys:
            continue
        if grade == EvidenceGrade.INDEPENDENTLY_VERIFIED:
            continue
        options = CONTROL_ARTIFACT_OPTIONS.get(check_key)
        if not options:
            continue
        unresolved.append(
            UnresolvedControl(
                check_key=check_key,
                baseline_grade=grade,
                missing_artifact_types=options,
                note=(
                    "No compatible, dated, issuer-identified, hash-pinned "
                    "artifact was accepted for promotion."
                ),
            )
        )

    return EvidencePackReport(
        generated_at=datetime.now(UTC),
        organization=manifest.organization,
        reviewed_at=manifest.reviewed_at,
        profile=manifest.profile,
        base_document=manifest.base_document,
        base_document_sha256=hashlib.sha256(base_data).hexdigest(),
        artifact_inventory=inventory,
        baseline_grades=baseline_grades,
        promotions=promotions,
        unresolved_controls=unresolved,
        warnings=list(dict.fromkeys(warnings)),
        disclaimer=PACK_DISCLAIMER,
    )


def audit_evidence_pack_zip(
    zip_path: str | Path,
) -> EvidencePackReport:
    archive_path = Path(zip_path).resolve()
    if not archive_path.is_file():
        raise ValueError(f"Evidence-pack ZIP not found: {archive_path}")
    try:
        archive = zipfile.ZipFile(archive_path)
    except zipfile.BadZipFile as exc:
        raise ValueError("Evidence pack is not a valid ZIP archive.") from exc

    with archive, tempfile.TemporaryDirectory(prefix="ics-evidence-pack-") as temp:
        _validate_zip_archive(archive)
        root = Path(temp).resolve()
        extracted: list[Path] = []
        for entry in archive.infolist():
            if entry.is_dir():
                continue
            destination = _safe_zip_path(root, entry.filename)
            destination.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(entry, "r") as source, destination.open("wb") as target:
                shutil.copyfileobj(source, target, length=1024 * 1024)
            extracted.append(destination)

        manifests = [
            path
            for path in extracted
            if path.name.lower() in {"manifest.yaml", "manifest.yml", "manifest.json"}
        ]
        if not manifests:
            raise ValueError(
                "Evidence-pack ZIP must contain manifest.yaml or manifest.json."
            )
        if len(manifests) > 1:
            raise ValueError("Evidence-pack ZIP must contain exactly one manifest.")
        return audit_evidence_pack(manifests[0])


def audit_evidence_pack_bundle(path: str | Path) -> EvidencePackReport:
    bundle_path = Path(path)
    if bundle_path.suffix.lower() == ".zip":
        return audit_evidence_pack_zip(bundle_path)
    return audit_evidence_pack(bundle_path)
