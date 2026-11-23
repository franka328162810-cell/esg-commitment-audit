from __future__ import annotations

import os
import tempfile
from io import BytesIO
from pathlib import Path
from urllib.parse import unquote

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pypdf import PdfReader

from esg_commitment_audit.api import (
    audit_bytes,
    audit_governance_bytes,
    audit_revisability_bytes,
)
from esg_commitment_audit.evidence_pack import audit_evidence_pack_zip

MAX_UPLOAD_BYTES = 50 * 1024 * 1024
MAX_EVIDENCE_PACK_BYTES = 100 * 1024 * 1024

app = FastAPI(
    title="ESG Commitment Audit Container",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
app.state.internal_token = os.environ.get("ESG_INTERNAL_TOKEN", "")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


async def _copy_upload_to_temp(
    request: Request,
    max_bytes: int,
) -> Path:
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > max_bytes:
        raise HTTPException(status_code=413, detail="Upload is too large")
    descriptor, raw_path = tempfile.mkstemp(prefix="ics-evidence-pack-", suffix=".zip")
    path = Path(raw_path)
    total = 0
    try:
        with os.fdopen(descriptor, "wb") as handle:
            async for chunk in request.stream():
                total += len(chunk)
                if total > max_bytes:
                    raise HTTPException(status_code=413, detail="Upload is too large")
                handle.write(chunk)
    except Exception:
        path.unlink(missing_ok=True)
        raise
    return path


@app.post("/audit")
async def audit(
    request: Request,
    x_esg_filename: str = Header("upload.pdf"),
    x_esg_max_pages: str = Header("100"),
    x_esg_weights: str = Header("default"),
    x_esg_mode: str = Header("commitment"),
    x_esg_profile: str = Header("general"),
    x_esg_internal_token: str = Header(""),
) -> JSONResponse:
    expected_token = request.app.state.internal_token
    if expected_token and x_esg_internal_token != expected_token:
        raise HTTPException(status_code=401, detail="Invalid internal token")
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Upload is too large")
    data = await request.body()
    if not data:
        raise HTTPException(status_code=400, detail="Upload is empty")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Upload is too large")
    try:
        max_pages = int(x_esg_max_pages)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail="Invalid page limit") from exc
    if max_pages < 1:
        raise HTTPException(status_code=500, detail="Invalid page limit")
    filename = unquote(x_esg_filename)
    mode = x_esg_mode.strip().lower()
    if mode not in {"commitment", "recursive-freedom", "ai-revisability"}:
        raise HTTPException(status_code=400, detail="Unknown audit mode")
    profile = x_esg_profile.strip().lower()
    if profile not in {
        "general",
        "news_media",
        "advertising",
        "insurance",
        "industrial_design",
    }:
        raise HTTPException(status_code=400, detail="Unknown review profile")
    if filename.lower().endswith(".pdf"):
        try:
            page_count = len(PdfReader(BytesIO(data)).pages)
        except Exception as exc:
            raise HTTPException(
                status_code=400,
                detail="The PDF file could not be parsed.",
            ) from exc
        if page_count > max_pages:
            raise HTTPException(
                status_code=413,
                detail=f"PDF exceeds the {max_pages}-page limit",
            )
    try:
        if mode == "recursive-freedom":
            report = audit_governance_bytes(data, filename)
        elif mode == "ai-revisability":
            report = audit_revisability_bytes(
                data,
                filename,
                profile=profile,
            )
        else:
            report = audit_bytes(
                data,
                filename=filename,
                weight_preset=x_esg_weights,
            )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return JSONResponse(report.model_dump(mode="json"))


@app.post("/evidence-pack")
async def evidence_pack(
    request: Request,
    x_esg_filename: str = Header("evidence-pack.zip"),
    x_esg_internal_token: str = Header(""),
) -> JSONResponse:
    expected_token = request.app.state.internal_token
    if expected_token and x_esg_internal_token != expected_token:
        raise HTTPException(status_code=401, detail="Invalid internal token")
    filename = unquote(x_esg_filename)
    if not filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Evidence pack must be a ZIP file")

    upload_path: Path | None = None
    try:
        upload_path = await _copy_upload_to_temp(request, MAX_EVIDENCE_PACK_BYTES)
        report = audit_evidence_pack_zip(upload_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        if upload_path is not None:
            upload_path.unlink(missing_ok=True)
    return JSONResponse(report.model_dump(mode="json"))
