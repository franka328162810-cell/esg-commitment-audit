from __future__ import annotations

from importlib.resources import files

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import __version__
from .api import (
    audit_bytes,
    audit_revisability_bytes,
    audit_revisability_text,
    audit_revisability_version_bytes,
    audit_text,
)
from .report import render_html, render_markdown, report_to_dict
from .revisability_report import (
    render_revisability_html,
    render_revisability_markdown,
    revisability_report_to_dict,
)
from .revisability_version_report import (
    render_version_trace_html,
    render_version_trace_markdown,
    version_trace_report_to_dict,
)

MAX_UPLOAD_BYTES = 20 * 1024 * 1024


class TextAuditRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2_000_000)
    filename: str = "pasted-text.txt"
    weights: str = "default"


class RevisabilityTextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2_000_000)
    filename: str = "ai-policy.txt"
    profile: str = "general"


def create_app() -> FastAPI:
    resource_root = files("esg_commitment_audit").joinpath("resources")
    static_root = resource_root.joinpath("static")
    template_root = resource_root.joinpath("templates")

    app = FastAPI(
        title="ESG Commitment Audit Workbench",
        version=__version__,
        docs_url="/api/docs",
        redoc_url=None,
    )
    app.mount("/static", StaticFiles(directory=str(static_root)), name="static")

    @app.middleware("http")
    async def security_headers(request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self' 'unsafe-inline'; "
            "script-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
        )
        return response

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(str(template_root.joinpath("index.html")))

    @app.get("/revisability", include_in_schema=False)
    def revisability_index() -> FileResponse:
        return FileResponse(str(template_root.joinpath("revisability.html")))

    @app.get("/revisability/versions", include_in_schema=False)
    def revisability_versions_index() -> FileResponse:
        return FileResponse(str(template_root.joinpath("revisability_versions.html")))

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    def response_payload(report) -> JSONResponse:
        return JSONResponse(
            {
                "report": report_to_dict(report),
                "markdown": render_markdown(report),
                "html": render_html(report),
            }
        )

    def revisability_response_payload(report) -> JSONResponse:
        return JSONResponse(
            {
                "report": revisability_report_to_dict(report),
                "markdown": render_revisability_markdown(report),
                "html": render_revisability_html(report),
            }
        )

    def version_trace_response_payload(report) -> JSONResponse:
        return JSONResponse(
            {
                "report": version_trace_report_to_dict(report),
                "markdown": render_version_trace_markdown(report),
                "html": render_version_trace_html(report),
            }
        )

    @app.post("/api/audit")
    async def audit_upload(
        file: UploadFile = File(...),  # noqa: B008 - standard FastAPI dependency signature.
        weights: str = Form("default"),
    ) -> JSONResponse:
        data = await file.read(MAX_UPLOAD_BYTES + 1)
        if len(data) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413, detail="File exceeds the 20 MB local limit."
            )
        try:
            report = audit_bytes(
                data, file.filename or "upload.txt", weight_preset=weights
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return response_payload(report)

    @app.post("/api/audit-text")
    def audit_pasted_text(request: TextAuditRequest) -> JSONResponse:
        try:
            report = audit_text(
                request.text,
                filename=request.filename,
                weight_preset=request.weights,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return response_payload(report)

    @app.post("/api/revisability")
    async def revisability_upload(
        file: UploadFile = File(...),  # noqa: B008 - standard FastAPI dependency signature.
        profile: str = Form("general"),
    ) -> JSONResponse:
        data = await file.read(MAX_UPLOAD_BYTES + 1)
        if len(data) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail="File exceeds the 20 MB local limit.",
            )
        try:
            report = audit_revisability_bytes(
                data,
                file.filename or "ai-policy.txt",
                profile=profile,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return revisability_response_payload(report)

    @app.post("/api/revisability-text")
    def revisability_pasted_text(
        request: RevisabilityTextRequest,
    ) -> JSONResponse:
        try:
            report = audit_revisability_text(
                request.text,
                filename=request.filename,
                profile=request.profile,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return revisability_response_payload(report)

    @app.post("/api/revisability-version")
    async def revisability_version_upload(
        previous_file: UploadFile = File(...),  # noqa: B008
        current_file: UploadFile = File(...),  # noqa: B008
        profile: str = Form("general"),
    ) -> JSONResponse:
        previous_data = await previous_file.read(MAX_UPLOAD_BYTES + 1)
        current_data = await current_file.read(MAX_UPLOAD_BYTES + 1)
        if (
            len(previous_data) > MAX_UPLOAD_BYTES
            or len(current_data) > MAX_UPLOAD_BYTES
        ):
            raise HTTPException(
                status_code=413,
                detail="Each file must be no larger than the 20 MB local limit.",
            )
        try:
            report = audit_revisability_version_bytes(
                previous_data,
                previous_file.filename or "previous-ai-policy.txt",
                current_data,
                current_file.filename or "current-ai-policy.txt",
                profile=profile,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return version_trace_response_payload(report)

    return app


app = create_app()
