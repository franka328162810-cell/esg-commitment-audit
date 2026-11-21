from __future__ import annotations

import argparse
import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument(
        "--plan",
        choices=("trial", "starter", "pro", "enterprise"),
        default="trial",
    )
    parser.add_argument(
        "--url",
        default=os.environ.get(
            "ICS_AUDIT_API_URL",
            "https://ics-commitment-audit-api.franka328162810.workers.dev",
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / ".ics-crv-service/cloudflare-pilot.json",
    )
    args = parser.parse_args()

    admin_token = os.environ.get("ICS_ADMIN_TOKEN", "")
    if not admin_token:
        token_file = ROOT / ".ics-crv-service/cloudflare-secrets.json"
        if token_file.is_file():
            admin_token = str(
                json.loads(token_file.read_text(encoding="utf-8")).get(
                    "ICS_ADMIN_TOKEN",
                    "",
                )
            )
    if not admin_token:
        raise SystemExit("ICS_ADMIN_TOKEN is not configured")

    body = json.dumps({"name": args.name, "plan": args.plan}).encode("utf-8")
    request = urllib.request.Request(
        f"{args.url.rstrip('/')}/v1/admin/organizations",
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-ICS-Admin-Token": admin_token,
            "User-Agent": "ics-commitment-audit-provisioner/0.3.0",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        result = json.loads(response.read().decode("utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "organization_id": result["organization_id"],
                "api_key_id": result["api_key_id"],
                "plan": result["plan"],
                "output": str(args.output),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
