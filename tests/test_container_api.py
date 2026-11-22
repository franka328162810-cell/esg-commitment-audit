from __future__ import annotations

import importlib.util
from io import BytesIO
from pathlib import Path
from types import ModuleType

from fastapi.testclient import TestClient
from pypdf import PdfWriter


def _load_container_module() -> ModuleType:
    path = Path("cloudflare/container_api.py")
    spec = importlib.util.spec_from_file_location("ics_container_api", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


container_api = _load_container_module()
client = TestClient(container_api.app)


def test_container_routes_ai_policy_mode() -> None:
    response = client.post(
        "/audit",
        headers={
            "x-esg-filename": "ai%20policy.txt",
            "x-esg-mode": "recursive-freedom",
        },
        content=(
            b"Policy owner: Chief AI Officer.\n"
            b"The policy is reviewed annually.\n"
            b"Users may appeal and request human review."
        ),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["report_type"] == "recursive-freedom"
    assert payload["document"]["filename"] == "ai policy.txt"
    assert len(payload["checks"]) == 10


def test_container_keeps_esg_mode_as_default() -> None:
    response = client.post(
        "/audit",
        headers={"x-esg-filename": "commitment.txt"},
        content=(
            b"The company commits to reducing emissions by 50% by 2030, "
            b"against a 2020 baseline."
        ),
    )

    assert response.status_code == 200
    payload = response.json()
    assert "commitments" in payload
    assert "report_type" not in payload


def test_container_rejects_unknown_mode() -> None:
    response = client.post(
        "/audit",
        headers={
            "x-esg-filename": "policy.txt",
            "x-esg-mode": "unknown",
        },
        content=b"Policy text.",
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unknown audit mode"


def test_container_rejects_pdf_over_page_limit_in_both_modes() -> None:
    writer = PdfWriter()
    for _ in range(101):
        writer.add_blank_page(width=612, height=792)
    output = BytesIO()
    writer.write(output)

    for mode in ("commitment", "recursive-freedom"):
        response = client.post(
            "/audit",
            headers={
                "x-esg-filename": "long.pdf",
                "x-esg-mode": mode,
            },
            content=output.getvalue(),
        )
        assert response.status_code == 413
        assert "100-page limit" in response.json()["detail"]
