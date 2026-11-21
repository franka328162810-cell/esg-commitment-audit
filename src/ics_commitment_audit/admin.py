from __future__ import annotations

import argparse
import json
from pathlib import Path

from .commercial import PLAN_LIMITS, CommercialStore, ServiceSettings


def _store(args: argparse.Namespace) -> CommercialStore:
    data_dir = (
        Path(args.data_dir) if args.data_dir else ServiceSettings.from_env().data_dir
    )
    store = CommercialStore(data_dir)
    store.initialize()
    return store


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ics-crv-admin")
    parser.add_argument(
        "--data-dir",
        help="Service data directory; defaults to ICS_SERVICE_DATA_DIR",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create-org", help="Create an organization")
    create.add_argument("--name", required=True)
    create.add_argument("--plan", choices=sorted(PLAN_LIMITS), default="trial")
    create.add_argument("--document-limit", type=int)

    issue = subparsers.add_parser("issue-key", help="Issue a one-time API key")
    issue.add_argument("--organization-id", required=True)
    issue.add_argument("--name", default="default")

    list_keys = subparsers.add_parser("list-keys", help="List API key metadata")
    list_keys.add_argument("--organization-id", required=True)

    revoke = subparsers.add_parser("revoke-key", help="Revoke an API key")
    revoke.add_argument("--api-key-id", required=True)

    set_plan = subparsers.add_parser(
        "set-plan", help="Change a plan or activation state"
    )
    set_plan.add_argument("--organization-id", required=True)
    set_plan.add_argument("--plan", choices=sorted(PLAN_LIMITS), required=True)
    set_plan.add_argument("--inactive", action="store_true")

    account = subparsers.add_parser("account", help="Show account and usage")
    account.add_argument("--organization-id", required=True)

    args = parser.parse_args(argv)
    store = _store(args)

    if args.command == "create-org":
        organization_id = store.create_organization(
            args.name,
            args.plan,
            args.document_limit,
        )
        print(organization_id)
        return 0
    if args.command == "issue-key":
        key_id, token = store.create_api_key_record(
            args.organization_id,
            args.name,
        )
        print(json.dumps({"api_key_id": key_id, "token": token}, indent=2))
        return 0
    if args.command == "list-keys":
        print(json.dumps(store.list_api_keys(args.organization_id), indent=2))
        return 0
    if args.command == "revoke-key":
        if not store.revoke_api_key(args.api_key_id):
            print("API key not found or already revoked")
            return 1
        print("revoked")
        return 0
    if args.command == "set-plan":
        store.set_plan(
            args.organization_id,
            args.plan,
            active=not args.inactive,
        )
        print("updated")
        return 0
    if args.command == "account":
        print(json.dumps(store.account(args.organization_id), indent=2))
        return 0
    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
