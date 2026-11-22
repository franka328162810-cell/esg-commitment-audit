from __future__ import annotations

from fastapi.testclient import TestClient

from esg_commitment_audit.web import app

client = TestClient(app)


def test_index_and_health() -> None:
    index = client.get("/")
    health = client.get("/health")
    assert index.status_code == 200
    assert "ESG / 气候承诺结构审计" in index.text
    assert index.headers["cache-control"] == "no-store"
    assert index.headers["x-content-type-options"] == "nosniff"
    assert "frame-ancestors 'none'" in index.headers["content-security-policy"]
    assert health.json()["status"] == "ok"


def test_text_audit_endpoint() -> None:
    response = client.post(
        "/api/audit-text",
        json={
            "text": "公司承诺到2030年将碳排放较2020年减少50%。",
            "filename": "pasted.txt",
            "weights": "default",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["report"]["summary"]["commitment_count"] == 1
    assert "<!doctype html>" in payload["html"]
    assert "# ESG Commitment Audit Report" in payload["markdown"]


def test_upload_endpoint_rejects_unsupported_file() -> None:
    response = client.post(
        "/api/audit",
        files={"file": ("report.csv", b"a,b\n1,2", "text/csv")},
        data={"weights": "default"},
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]
