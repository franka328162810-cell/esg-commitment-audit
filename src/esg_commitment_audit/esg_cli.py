from __future__ import annotations

import argparse
import sys
import threading
import webbrowser
from pathlib import Path

from . import __version__
from .api import audit_bytes
from .report import render_html, render_json, render_markdown

WEIGHTS = (
    "default",
    "obs-priority",
    "enf-priority",
    "rev-priority",
    "esg-balanced",
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="esg-commitment-audit",
        description="ESG Commitment Audit workbench",
    )
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit_parser = subparsers.add_parser(
        "audit",
        help="Audit an ESG or climate commitment document",
    )
    audit_parser.add_argument("input", type=Path)
    audit_parser.add_argument("--weights", choices=WEIGHTS, default="default")
    audit_parser.add_argument(
        "--format",
        choices=("markdown", "json", "html"),
        default="markdown",
        dest="output_format",
    )
    audit_parser.add_argument("--output", type=Path)

    serve_parser = subparsers.add_parser(
        "serve",
        help="Open the local ESG Commitment Audit workbench",
    )
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", default=8765, type=int)
    serve_parser.add_argument("--no-browser", action="store_true")
    return parser


def _run_audit(args: argparse.Namespace) -> int:
    if not args.input.is_file():
        print(f"Input file not found: {args.input}", file=sys.stderr)
        return 2
    try:
        report = audit_bytes(
            args.input.read_bytes(),
            args.input.name,
            weight_preset=args.weights,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"ESG audit failed: {exc}", file=sys.stderr)
        return 2

    if args.output_format == "json":
        rendered = render_json(report)
        extension = ".json"
    elif args.output_format == "html":
        rendered = render_html(report)
        extension = ".html"
    else:
        rendered = render_markdown(report)
        extension = ".md"

    if args.output is None:
        print(rendered)
        return 0
    output = args.output
    if output.suffix.lower() != extension:
        output = output.with_suffix(extension)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    print(output.resolve())
    return 0


def _run_server(args: argparse.Namespace) -> int:
    import uvicorn

    url = f"http://{args.host}:{args.port}"
    print(f"ESG Commitment Audit: {url}")
    print("Press Ctrl+C to stop.")
    if not args.no_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    uvicorn.run(
        "esg_commitment_audit.web:app",
        host=args.host,
        port=args.port,
        log_level="info",
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "audit":
        return _run_audit(args)
    if args.command == "serve":
        return _run_server(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
