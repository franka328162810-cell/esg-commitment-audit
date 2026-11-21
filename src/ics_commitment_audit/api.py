from __future__ import annotations

from .audit import audit_document
from .governance import audit_governance_document
from .ingest import ingest_bytes
from .models import AuditReport, GovernanceReport


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
