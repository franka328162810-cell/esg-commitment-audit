from __future__ import annotations

import os
from io import BytesIO
from urllib.parse import unquote

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pypdf import PdfReader

from ics_commitment_audit.api import audit_bytes, audit_governance_bytes

MAX_UPLOAD_BYTES = 50 * 1024 * 1024

app = FastAPI(
    title="ICS Commitment Audit Container",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
app.state.internal_token = os.environ.get("ICS_INTERNAL_TOKEN", "")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/audit")
async def audit(
    request: Request,
    x_ics_filename: str = Header("upload.pdf"),
    x_ics_max_pages: str = Header("100"),
    x_ics_weights: str = Header("default"),
    x_ics_mode: str = Header("commitment"),
    x_ics_internal_token: str = Header(""),
) -> JSONResponse:
    expected_token = request.app.state.internal_token
    if expected_token and x_ics_internal_token != expected_token:
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
        max_pages = int(x_ics_max_pages)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail="Invalid page limit") from exc
    if max_pages < 1:
        raise HTTPException(status_code=500, detail="Invalid page limit")
    filename = unquote(x_ics_filename)
    mode = x_ics_mode.strip().lower()
    if mode not in {"commitment", "recursive-freedom"}:
        raise HTTPException(status_code=400, detail="Unknown audit mode")
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
        else:
            report = audit_bytes(
                data,
                filename=filename,
                weight_preset=x_ics_weights,
            )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return JSONResponse(report.model_dump(mode="json"))
