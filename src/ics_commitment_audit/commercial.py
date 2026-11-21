from __future__ import annotations

import hashlib
import hmac
import io
import json
import os
import secrets
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pypdf import PdfReader

from . import __version__
from .api import audit_bytes
from .ingest import SUPPORTED_EXTENSIONS
from .report import report_to_dict
from .rules import get_weight_preset

PLAN_LIMITS = {
    "trial": 5,
    "starter": 25,
    "pro": 150,
    "enterprise": 10_000,
}
MAX_ALLOWED_UPLOAD_BYTES = 50 * 1024 * 1024
DEFAULT_UPLOAD_BYTES = 20 * 1024 * 1024
MAX_PDF_PAGES = 300


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _period_key() -> str:
    return datetime.now(UTC).strftime("%Y-%m")


def _hash_api_key(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ServiceSettings:
    data_dir: Path
    max_workers: int = 2
    report_retention_days: int = 7
    billing_webhook_secret: str | None = None
    stripe_webhook_secret: str | None = None
    inline_worker: bool = False

    @classmethod
    def from_env(cls) -> ServiceSettings:
        data_dir = Path(os.environ.get("ICS_SERVICE_DATA_DIR", ".ics-crv-service"))
        return cls(
            data_dir=data_dir,
            max_workers=max(1, int(os.environ.get("ICS_SERVICE_MAX_WORKERS", "2"))),
            report_retention_days=max(
                1, int(os.environ.get("ICS_REPORT_RETENTION_DAYS", "7"))
            ),
            billing_webhook_secret=os.environ.get("ICS_BILLING_WEBHOOK_SECRET"),
            stripe_webhook_secret=os.environ.get("ICS_STRIPE_WEBHOOK_SECRET"),
            inline_worker=os.environ.get("ICS_INLINE_WORKER", "").lower()
            in {"1", "true", "yes"},
        )


class CommercialStore:
    def __init__(self, data_dir: Path, report_retention_days: int = 7) -> None:
        self.data_dir = data_dir
        self.report_retention_days = report_retention_days
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "service.sqlite3"
        self.input_dir = self.data_dir / "inputs"
        self.report_dir = self.data_dir / "reports"
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        return connection

    def initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS organizations (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    plan TEXT NOT NULL,
                    monthly_document_limit INTEGER NOT NULL,
                    documents_used INTEGER NOT NULL DEFAULT 0,
                    usage_period TEXT NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS api_keys (
                    id TEXT PRIMARY KEY,
                    organization_id TEXT NOT NULL REFERENCES organizations(id),
                    name TEXT NOT NULL,
                    key_hash TEXT NOT NULL UNIQUE,
                    prefix TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    revoked_at TEXT
                );
                CREATE TABLE IF NOT EXISTS audit_jobs (
                    id TEXT PRIMARY KEY,
                    organization_id TEXT NOT NULL REFERENCES organizations(id),
                    status TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    extension TEXT NOT NULL,
                    sha256 TEXT NOT NULL,
                    byte_count INTEGER NOT NULL,
                    weights TEXT NOT NULL,
                    input_path TEXT NOT NULL,
                    report_path TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_audit_jobs_org
                    ON audit_jobs(organization_id, created_at);
                """
            )

    def create_organization(
        self,
        name: str,
        plan: str = "trial",
        monthly_document_limit: int | None = None,
    ) -> str:
        if plan not in PLAN_LIMITS:
            raise ValueError(f"Unknown plan '{plan}'")
        organization_id = f"org_{uuid4().hex}"
        limit = monthly_document_limit or PLAN_LIMITS[plan]
        if not 1 <= limit <= 1_000_000:
            raise ValueError("Monthly document limit must be between 1 and 1,000,000")
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO organizations
                    (id, name, plan, monthly_document_limit, documents_used,
                     usage_period, active, created_at)
                VALUES (?, ?, ?, ?, 0, ?, 1, ?)
                """,
                (organization_id, name, plan, limit, _period_key(), _utc_now()),
            )
        return organization_id

    def create_api_key(self, organization_id: str, name: str) -> str:
        _, token = self.create_api_key_record(organization_id, name)
        return token

    def create_api_key_record(
        self,
        organization_id: str,
        name: str,
    ) -> tuple[str, str]:
        token = f"ics_live_{secrets.token_urlsafe(32)}"
        prefix = token[:16]
        key_id = f"key_{uuid4().hex}"
        with self._connect() as connection:
            organization = connection.execute(
                "SELECT active FROM organizations WHERE id = ?",
                (organization_id,),
            ).fetchone()
            if organization is None:
                raise ValueError("Organization not found")
            if not organization["active"]:
                raise ValueError("Organization is inactive")
            connection.execute(
                """
                INSERT INTO api_keys
                    (id, organization_id, name, key_hash, prefix, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    key_id,
                    organization_id,
                    name,
                    _hash_api_key(token),
                    prefix,
                    _utc_now(),
                ),
            )
        return key_id, token

    def revoke_api_key(self, key_id: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE api_keys
                SET revoked_at = ?
                WHERE id = ? AND revoked_at IS NULL
                """,
                (_utc_now(), key_id),
            )
        return cursor.rowcount == 1

    def list_api_keys(self, organization_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, name, prefix, created_at, revoked_at
                FROM api_keys
                WHERE organization_id = ?
                ORDER BY created_at
                """,
                (organization_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def set_plan(
        self,
        organization_id: str,
        plan: str,
        *,
        active: bool = True,
    ) -> None:
        if plan not in PLAN_LIMITS:
            raise ValueError(f"Unknown plan '{plan}'")
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE organizations
                SET plan = ?, monthly_document_limit = ?, active = ?
                WHERE id = ?
                """,
                (plan, PLAN_LIMITS[plan], int(active), organization_id),
            )
            if cursor.rowcount != 1:
                raise ValueError("Organization not found")

    def authenticate(self, token: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT o.*, k.id AS api_key_id, k.name AS api_key_name
                FROM api_keys AS k
                JOIN organizations AS o ON o.id = k.organization_id
                WHERE k.key_hash = ? AND k.revoked_at IS NULL AND o.active = 1
                """,
                (_hash_api_key(token),),
            ).fetchone()
        return dict(row) if row else None

    def account(self, organization_id: str) -> dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM organizations WHERE id = ?",
                (organization_id,),
            ).fetchone()
        if row is None:
            raise KeyError("Organization not found")
        result = dict(row)
        result["remaining_documents"] = max(
            0, result["monthly_document_limit"] - result["documents_used"]
        )
        return result

    def reserve_job(
        self,
        organization_id: str,
        *,
        filename: str,
        extension: str,
        sha256: str,
        byte_count: int,
        weights: str,
    ) -> tuple[str, Path]:
        job_id = f"job_{uuid4().hex}"
        input_path = self.input_dir / f"{job_id}{extension}"
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            organization = connection.execute(
                "SELECT * FROM organizations WHERE id = ? AND active = 1",
                (organization_id,),
            ).fetchone()
            if organization is None:
                raise PermissionError("Organization is inactive")
            current_period = _period_key()
            used = organization["documents_used"]
            if organization["usage_period"] != current_period:
                used = 0
            if used >= organization["monthly_document_limit"]:
                raise OverflowError("Monthly document quota exhausted")
            connection.execute(
                """
                UPDATE organizations
                SET documents_used = ?, usage_period = ?
                WHERE id = ?
                """,
                (used + 1, current_period, organization_id),
            )
            connection.execute(
                """
                INSERT INTO audit_jobs
                    (id, organization_id, status, filename, extension, sha256,
                     byte_count, weights, input_path, created_at)
                VALUES (?, ?, 'queued', ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    organization_id,
                    filename,
                    extension,
                    sha256,
                    byte_count,
                    weights,
                    str(input_path),
                    _utc_now(),
                ),
            )
        return job_id, input_path

    def claim_job(self, job_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE audit_jobs
                SET status = 'running', started_at = ?
                WHERE id = ? AND status = 'queued'
                """,
                (_utc_now(), job_id),
            )
            if cursor.rowcount != 1:
                return None
            row = connection.execute(
                "SELECT * FROM audit_jobs WHERE id = ?",
                (job_id,),
            ).fetchone()
        return dict(row) if row else None

    def complete_job(self, job_id: str, report_path: Path) -> None:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE audit_jobs
                SET status = 'completed', report_path = ?, completed_at = ?
                WHERE id = ? AND status = 'running'
                """,
                (str(report_path), _utc_now(), job_id),
            )
            if cursor.rowcount != 1:
                raise RuntimeError("Job is not in running state")

    def fail_job(self, job_id: str, error: str) -> None:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            job = connection.execute(
                "SELECT organization_id, status FROM audit_jobs WHERE id = ?",
                (job_id,),
            ).fetchone()
            if job is None or job["status"] in {"completed", "failed"}:
                return
            connection.execute(
                """
                UPDATE audit_jobs
                SET status = 'failed', error = ?, completed_at = ?
                WHERE id = ?
                """,
                (error[:2000], _utc_now(), job_id),
            )
            connection.execute(
                """
                UPDATE organizations
                SET documents_used = MAX(0, documents_used - 1)
                WHERE id = ?
                """,
                (job["organization_id"],),
            )

    def job_for_org(self, organization_id: str, job_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT * FROM audit_jobs
                WHERE id = ? AND organization_id = ?
                """,
                (job_id, organization_id),
            ).fetchone()
        return dict(row) if row else None

    def delete_job(self, organization_id: str, job_id: str) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT input_path, report_path FROM audit_jobs
                WHERE id = ? AND organization_id = ?
                """,
                (job_id, organization_id),
            ).fetchone()
            if row is None:
                return False
            cursor = connection.execute(
                "DELETE FROM audit_jobs WHERE id = ? AND organization_id = ?",
                (job_id, organization_id),
            )
        for key in ("input_path", "report_path"):
            path_value = row[key]
            if path_value:
                Path(path_value).unlink(missing_ok=True)
        return cursor.rowcount == 1

    def requeue_interrupted_jobs(self) -> list[str]:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE audit_jobs
                SET status = 'queued', started_at = NULL
                WHERE status = 'running'
                """
            )
            rows = connection.execute(
                "SELECT id FROM audit_jobs WHERE status = 'queued' ORDER BY created_at"
            ).fetchall()
        return [row["id"] for row in rows]

    def queued_jobs(self) -> list[str]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id FROM audit_jobs WHERE status = 'queued' ORDER BY created_at"
            ).fetchall()
        return [row["id"] for row in rows]

    def cleanup_expired_reports(self, retention_days: int) -> int:
        cutoff = time.time() - retention_days * 86400
        removed = 0
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, report_path FROM audit_jobs
                WHERE report_path IS NOT NULL AND completed_at IS NOT NULL
                """
            ).fetchall()
            for row in rows:
                path = Path(row["report_path"])
                if path.exists() and path.stat().st_mtime < cutoff:
                    path.unlink(missing_ok=True)
                    connection.execute(
                        "UPDATE audit_jobs SET report_path = NULL WHERE id = ?",
                        (row["id"],),
                    )
                    removed += 1
        return removed


class AuditExecutor:
    def __init__(
        self,
        store: CommercialStore,
        *,
        max_workers: int,
        inline: bool,
    ) -> None:
        self.store = store
        self.inline = inline
        self.pool = None if inline else ThreadPoolExecutor(max_workers=max_workers)

    def submit(self, job_id: str) -> None:
        if self.inline:
            self.process(job_id)
        else:
            assert self.pool is not None
            self.pool.submit(self.process, job_id)

    def process(self, job_id: str) -> None:
        job = self.store.claim_job(job_id)
        if job is None:
            return
        input_path = Path(job["input_path"])
        report_path = self.store.report_dir / f"{job_id}.json"
        try:
            data = input_path.read_bytes()
            report = audit_bytes(
                data,
                job["filename"],
                weight_preset=job["weights"],
            )
            temporary = report_path.with_suffix(".json.tmp")
            temporary.write_text(
                json.dumps(report_to_dict(report), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            temporary.replace(report_path)
            self.store.complete_job(job_id, report_path)
        except Exception as exc:  # noqa: BLE001 - job failures are persisted for the tenant.
            self.store.fail_job(job_id, f"{type(exc).__name__}: {exc}")
        finally:
            input_path.unlink(missing_ok=True)

    def shutdown(self) -> None:
        if self.pool is not None:
            self.pool.shutdown(wait=False, cancel_futures=False)


def _job_payload(job: dict[str, Any]) -> dict[str, Any]:
    return {
        key: job[key]
        for key in (
            "id",
            "status",
            "filename",
            "sha256",
            "byte_count",
            "weights",
            "error",
            "created_at",
            "started_at",
            "completed_at",
        )
    }


def _verify_hmac_signature(
    secret: str,
    body: bytes,
    signature: str,
    timestamp: str,
) -> bool:
    try:
        timestamp_seconds = int(timestamp)
    except ValueError:
        return False
    if abs(int(time.time()) - timestamp_seconds) > 300:
        return False
    signed_payload = f"{timestamp}.".encode() + body
    expected = hmac.new(
        secret.encode(),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()
    normalized = signature.removeprefix("sha256=")
    return hmac.compare_digest(expected, normalized)


def _verify_stripe_signature(
    secret: str,
    body: bytes,
    signature_header: str,
) -> bool:
    parts = [part.split("=", 1) for part in signature_header.split(",") if "=" in part]
    values: dict[str, list[str]] = {}
    for key, value in parts:
        values.setdefault(key, []).append(value)
    timestamp = (values.get("t") or [""])[0]
    try:
        timestamp_seconds = int(timestamp)
    except ValueError:
        return False
    if abs(int(time.time()) - timestamp_seconds) > 300:
        return False
    expected = hmac.new(
        secret.encode(),
        f"{timestamp}.".encode() + body,
        hashlib.sha256,
    ).hexdigest()
    return any(
        hmac.compare_digest(expected, signature) for signature in values.get("v1", [])
    )


def create_commercial_app(settings: ServiceSettings | None = None) -> FastAPI:
    service_settings = settings or ServiceSettings.from_env()
    store = CommercialStore(
        service_settings.data_dir,
        report_retention_days=service_settings.report_retention_days,
    )
    store.initialize()
    executor = AuditExecutor(
        store,
        max_workers=service_settings.max_workers,
        inline=service_settings.inline_worker,
    )

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        store.cleanup_expired_reports(service_settings.report_retention_days)
        for job_id in store.requeue_interrupted_jobs():
            executor.submit(job_id)
        try:
            yield
        finally:
            executor.shutdown()

    app = FastAPI(
        title="ICS Commitment Audit Commercial API",
        version=__version__,
        docs_url="/v1/docs",
        redoc_url=None,
        lifespan=lifespan,
    )
    app.state.store = store
    app.state.executor = executor
    bearer = HTTPBearer(auto_error=False)

    def current_account(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer),  # noqa: B008 - FastAPI dependency signature.
    ) -> dict[str, Any]:
        if credentials is None or credentials.scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Bearer API key required")
        account = store.authenticate(credentials.credentials)
        if account is None:
            raise HTTPException(status_code=401, detail="Invalid or revoked API key")
        return account

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    @app.get("/v1/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    @app.get("/v1/account")
    def account(
        identity: dict[str, Any] = Depends(  # noqa: B008
            current_account
        ),
    ) -> dict[str, Any]:
        result = store.account(identity["id"])
        return {
            key: result[key]
            for key in (
                "id",
                "name",
                "plan",
                "active",
                "monthly_document_limit",
                "documents_used",
                "remaining_documents",
                "usage_period",
            )
        }

    @app.post("/v1/audits", status_code=202)
    async def create_audit(
        file: UploadFile = File(...),  # noqa: B008 - FastAPI dependency signature.
        weights: str = Form("default"),
        identity: dict[str, Any] = Depends(  # noqa: B008
            current_account
        ),
    ) -> JSONResponse:
        filename = Path(file.filename or "upload.txt").name
        extension = Path(filename).suffix.lower()
        if extension not in SUPPORTED_EXTENSIONS:
            raise HTTPException(status_code=415, detail="Unsupported document type")
        data = await file.read(MAX_ALLOWED_UPLOAD_BYTES + 1)
        if len(data) > MAX_ALLOWED_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="File exceeds the 50 MB limit")
        plan_upload_limit = (
            MAX_ALLOWED_UPLOAD_BYTES
            if identity["plan"] in {"pro", "enterprise"}
            else DEFAULT_UPLOAD_BYTES
        )
        if len(data) > plan_upload_limit:
            detail = (
                "This plan supports documents up to 20 MB"
                if plan_upload_limit == DEFAULT_UPLOAD_BYTES
                else "File exceeds the service upload limit"
            )
            raise HTTPException(status_code=413, detail=detail)
        if extension == ".pdf":
            try:
                if len(PdfReader(io.BytesIO(data)).pages) > MAX_PDF_PAGES:
                    raise HTTPException(
                        status_code=413,
                        detail=f"PDF exceeds the {MAX_PDF_PAGES}-page service limit",
                    )
            except HTTPException:
                raise
            except Exception as exc:
                raise HTTPException(status_code=400, detail="Invalid PDF file") from exc
        try:
            get_weight_preset(weights)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        try:
            job_id, input_path = store.reserve_job(
                identity["id"],
                filename=filename,
                extension=extension,
                sha256=hashlib.sha256(data).hexdigest(),
                byte_count=len(data),
                weights=weights,
            )
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except OverflowError as exc:
            raise HTTPException(status_code=429, detail=str(exc)) from exc
        try:
            input_path.write_bytes(data)
        except OSError as exc:
            store.fail_job(job_id, f"Input staging failed: {exc}")
            raise HTTPException(status_code=500, detail="Input staging failed") from exc
        executor.submit(job_id)
        job = store.job_for_org(identity["id"], job_id)
        assert job is not None
        return JSONResponse(
            {
                **_job_payload(job),
                "poll_url": f"/v1/audits/{job_id}",
            },
            status_code=202,
        )

    @app.get("/v1/audits/{job_id}")
    def get_audit(
        job_id: str,
        identity: dict[str, Any] = Depends(  # noqa: B008
            current_account
        ),
    ) -> dict[str, Any]:
        job = store.job_for_org(identity["id"], job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Audit job not found")
        return _job_payload(job)

    @app.get("/v1/audits/{job_id}/report")
    def get_report(
        job_id: str,
        identity: dict[str, Any] = Depends(  # noqa: B008
            current_account
        ),
    ) -> JSONResponse:
        job = store.job_for_org(identity["id"], job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Audit job not found")
        if job["status"] != "completed":
            raise HTTPException(status_code=409, detail="Audit report is not ready")
        if not job["report_path"]:
            raise HTTPException(status_code=410, detail="Audit report has expired")
        path = Path(job["report_path"])
        if not path.exists():
            raise HTTPException(status_code=410, detail="Audit report has expired")
        return JSONResponse(json.loads(path.read_text(encoding="utf-8")))

    @app.delete("/v1/audits/{job_id}", status_code=204)
    def delete_audit(
        job_id: str,
        identity: dict[str, Any] = Depends(  # noqa: B008
            current_account
        ),
    ) -> None:
        if not store.delete_job(identity["id"], job_id):
            raise HTTPException(status_code=404, detail="Audit job not found")

    @app.post("/v1/billing/webhook")
    async def billing_webhook(request: Request) -> dict[str, str]:
        secret = service_settings.billing_webhook_secret
        if not secret:
            raise HTTPException(status_code=503, detail="Billing is not configured")
        body = await request.body()
        signature = request.headers.get("X-ICS-Signature", "")
        timestamp = request.headers.get("X-ICS-Timestamp", "")
        if not _verify_hmac_signature(secret, body, signature, timestamp):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        try:
            payload = json.loads(body)
            organization_id = str(payload["organization_id"])
            event = str(payload["event"])
            plan = str(payload["plan"])
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise HTTPException(
                status_code=400, detail="Invalid webhook payload"
            ) from exc
        if event not in {
            "subscription.activated",
            "subscription.updated",
            "subscription.cancelled",
        }:
            raise HTTPException(status_code=400, detail="Unsupported billing event")
        try:
            store.set_plan(
                organization_id,
                plan,
                active=event != "subscription.cancelled",
            )
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {"status": "accepted"}

    @app.post("/v1/billing/stripe-webhook")
    async def stripe_webhook(request: Request) -> dict[str, str]:
        secret = service_settings.stripe_webhook_secret
        if not secret:
            raise HTTPException(
                status_code=503,
                detail="Stripe billing is not configured",
            )
        body = await request.body()
        signature = request.headers.get("Stripe-Signature", "")
        if not _verify_stripe_signature(secret, body, signature):
            raise HTTPException(status_code=401, detail="Invalid Stripe signature")
        try:
            payload = json.loads(body)
            event_type = str(payload["type"])
            stripe_object = payload["data"]["object"]
            metadata = stripe_object.get("metadata") or {}
            organization_id = metadata.get("organization_id") or stripe_object.get(
                "client_reference_id"
            )
            plan = metadata.get("plan")
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise HTTPException(
                status_code=400, detail="Invalid Stripe payload"
            ) from exc
        if not organization_id or plan not in PLAN_LIMITS:
            raise HTTPException(
                status_code=400,
                detail="Stripe metadata must include organization_id and plan",
            )
        active_events = {
            "checkout.session.completed",
            "customer.subscription.created",
            "customer.subscription.updated",
        }
        inactive_events = {"customer.subscription.deleted"}
        if event_type in active_events:
            active = True
        elif event_type in inactive_events:
            active = False
        else:
            return {"status": "ignored"}
        try:
            store.set_plan(str(organization_id), str(plan), active=active)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {"status": "accepted"}

    return app


app = create_commercial_app()
