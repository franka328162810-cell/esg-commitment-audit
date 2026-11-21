from __future__ import annotations

from importlib.resources import files

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .api import audit_bytes, audit_text
from .report import render_html, render_markdown, report_to_dict

MAX_UPLOAD_BYTES = 20 * 1024 * 1024


class TextAuditRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2_000_000)
    filename: str = "pasted-text.txt"
    weights: str = "default"


def create_app() -> FastAPI:
    resource_root = files("ics_commitment_audit").joinpath("resources")
    static_root = resource_root.joinpath("static")
    template_root = resource_root.joinpath("templates")

    app = FastAPI(
        title="ICS Commitment Audit Workbench",
        version="0.3.0",
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

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": "0.3.0"}

    def response_payload(report) -> JSONResponse:
        return JSONResponse(
            {
                "report": report_to_dict(report),
                "markdown": render_markdown(report),
                "html": render_html(report),
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

    return app


app = create_app()
