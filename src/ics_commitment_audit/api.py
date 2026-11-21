from __future__ import annotations

from .audit import audit_document
from .ingest import ingest_bytes
from .models import AuditReport


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
