from __future__ import annotations

from .audit import audit_document
from .governance import audit_governance_document
from .ingest import ingest_bytes
from .models import AuditReport, GovernanceReport
from .revisability import audit_revisability_document
from .revisability_models import ReviewProfile, RevisabilityReport
from .revisability_versions import (
    VersionTraceReport,
    audit_revisability_version_documents,
)


def audit_bytes(
    data: bytes,
    filename: str,
    weight_preset: str = "default",
) -> AuditReport:
    document = ingest_bytes(data, filename)
    return audit_document(document, weight_preset=weight_preset)


def audit_text(
    text: str,
    filename: str = "pasted-text.txt",
    weight_preset: str = "default",
) -> AuditReport:
    return audit_bytes(text.encode("utf-8"), filename, weight_preset=weight_preset)


def audit_governance_bytes(
    data: bytes,
    filename: str,
) -> GovernanceReport:
    document = ingest_bytes(data, filename)
    return audit_governance_document(document)


def audit_governance_text(
    text: str,
    filename: str = "ai-policy.txt",
) -> GovernanceReport:
    return audit_governance_bytes(text.encode("utf-8"), filename)


def audit_revisability_bytes(
    data: bytes,
    filename: str,
    profile: ReviewProfile = "general",
) -> RevisabilityReport:
    document = ingest_bytes(data, filename)
    return audit_revisability_document(document, profile=profile)


def audit_revisability_text(
    text: str,
    filename: str = "ai-policy.txt",
    profile: ReviewProfile = "general",
) -> RevisabilityReport:
    return audit_revisability_bytes(
        text.encode("utf-8"),
        filename,
        profile=profile,
    )


def audit_revisability_version_bytes(
    previous_data: bytes,
    previous_filename: str,
    current_data: bytes,
    current_filename: str,
    profile: ReviewProfile = "general",
) -> VersionTraceReport:
    previous_document = ingest_bytes(previous_data, previous_filename)
    current_document = ingest_bytes(current_data, current_filename)
    return audit_revisability_version_documents(
        previous_document,
        current_document,
        profile=profile,
    )
