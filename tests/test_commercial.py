from __future__ import annotations

import hashlib
import hmac
import json
import time
from pathlib import Path

from fastapi.testclient import TestClient

from esg_commitment_audit.commercial import ServiceSettings, create_commercial_app


def _client(
    tmp_path: Path,
    *,
    secret: str | None = None,
    stripe_secret: str | None = None,
) -> tuple[TestClient, object]:
    app = create_commercial_app(
        ServiceSettings(
            data_dir=tmp_path,
            max_workers=1,
            report_retention_days=7,
            billing_webhook_secret=secret,
            stripe_webhook_secret=stripe_secret,
            inline_worker=True,
        )
    )
    return TestClient(app), app.state.store


def test_commercial_audit_quota_and_tenant_isolation(tmp_path: Path) -> None:
    client, store = _client(tmp_path)
    first_org = store.create_organization("First", "trial", 1)
    first_key = store.create_api_key(first_org, "test")
    second_org = store.create_organization("Second", "trial", 5)
    second_key = store.create_api_key(second_org, "test")
    headers = {"Authorization": f"Bearer {first_key}"}

    with client:
        response = client.post(
            "/v1/audits",
            headers=headers,
            files={
                "file": (
                    "report.txt",
                    "公司承诺到2030年将碳排放减少50%。".encode(),
                    "text/plain",
                )
            },
        )
        assert response.status_code == 202
        job = response.json()
        assert job["status"] == "completed"

        status = client.get(f"/v1/audits/{job['id']}", headers=headers)
        assert status.status_code == 200
        assert status.json()["status"] == "completed"

        report = client.get(f"/v1/audits/{job['id']}/report", headers=headers)
        assert report.status_code == 200
        assert report.json()["summary"]["commitment_count"] == 1

        account = client.get("/v1/account", headers=headers)
        assert account.json()["documents_used"] == 1
        assert account.json()["remaining_documents"] == 0

        second_headers = {"Authorization": f"Bearer {second_key}"}
        assert (
            client.get(f"/v1/audits/{job['id']}", headers=second_headers).status_code
            == 404
        )

        exhausted = client.post(
            "/v1/audits",
            headers=headers,
            files={"file": ("again.txt", b"We commit to net zero by 2040.")},
        )
        assert exhausted.status_code == 429


def test_commercial_rejects_missing_auth_and_invalid_weights(
    tmp_path: Path,
) -> None:
    client, store = _client(tmp_path)
    organization_id = store.create_organization("Test", "starter")
    api_key = store.create_api_key(organization_id, "test")

    with client:
        assert client.get("/v1/account").status_code == 401
        invalid = client.post(
            "/v1/audits",
            headers={"Authorization": f"Bearer {api_key}"},
            data={"weights": "unknown"},
            files={"file": ("report.txt", b"We commit to net zero by 2040.")},
        )
        assert invalid.status_code == 400
        account = client.get(
            "/v1/account",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        assert account.json()["documents_used"] == 0


def test_billing_webhook_verifies_signature_and_updates_plan(
    tmp_path: Path,
) -> None:
    secret = "test-webhook-secret"
    client, store = _client(tmp_path, secret=secret)
    organization_id = store.create_organization("Billing", "trial")
    payload = json.dumps(
        {
            "organization_id": organization_id,
            "event": "subscription.activated",
            "plan": "pro",
        }
    ).encode()
    timestamp = str(int(time.time()))
    signature = hmac.new(
        secret.encode(),
        f"{timestamp}.".encode() + payload,
        hashlib.sha256,
    ).hexdigest()

    with client:
        accepted = client.post(
            "/v1/billing/webhook",
            content=payload,
            headers={
                "Content-Type": "application/json",
                "X-ESG-Signature": f"sha256={signature}",
                "X-ESG-Timestamp": timestamp,
            },
        )
        assert accepted.status_code == 200
        assert store.account(organization_id)["plan"] == "pro"

        rejected = client.post(
            "/v1/billing/webhook",
            content=payload,
            headers={"X-ESG-Signature": "sha256=bad"},
        )
        assert rejected.status_code == 401


def test_revoked_api_key_cannot_authenticate(tmp_path: Path) -> None:
    _client_instance, store = _client(tmp_path)
    organization_id = store.create_organization("Revocation", "starter")
    key_id, token = store.create_api_key_record(organization_id, "test")

    assert store.authenticate(token) is not None
    assert store.revoke_api_key(key_id) is True
    assert store.authenticate(token) is None


def test_stripe_webhook_signature_and_subscription_update(tmp_path: Path) -> None:
    secret = "stripe-test-secret"
    client, store = _client(tmp_path, stripe_secret=secret)
    organization_id = store.create_organization("Stripe", "trial")
    payload = json.dumps(
        {
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "metadata": {
                        "organization_id": organization_id,
                        "plan": "starter",
                    }
                }
            },
        }
    ).encode()
    timestamp = str(int(time.time()))
    signature = hmac.new(
        secret.encode(),
        f"{timestamp}.".encode() + payload,
        hashlib.sha256,
    ).hexdigest()

    with client:
        updated = client.post(
            "/v1/billing/stripe-webhook",
            content=payload,
            headers={
                "Content-Type": "application/json",
                "Stripe-Signature": f"t={timestamp},v1={signature}",
            },
        )
        assert updated.status_code == 200
        assert store.account(organization_id)["plan"] == "starter"
