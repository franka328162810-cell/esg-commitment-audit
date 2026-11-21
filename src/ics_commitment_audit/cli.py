from __future__ import annotations

import argparse
import sys
import threading
import webbrowser
from pathlib import Path

from . import __version__
from .api import audit_bytes
from .report import render_html, render_json, render_markdown


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ics-crv",
        description="Local ESG / climate commitment structure auditor",
    )
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit_parser = subparsers.add_parser("audit", help="Audit a local document")
    audit_parser.add_argument(
        "input", type=Path, help="PDF, DOCX, TXT, or Markdown file"
    )
    audit_parser.add_argument(
        "--format",
        choices=("markdown", "json", "html"),
        default="markdown",
        dest="output_format",
    )
    audit_parser.add_argument("--output", type=Path, help="Output file path")
    audit_parser.add_argument(
        "--weights",
        default="default",
        choices=(
            "default",
            "obs-priority",
            "enf-priority",
            "rev-priority",
            "esg-balanced",
        ),
    )

    serve_parser = subparsers.add_parser("serve", help="Start the local web interface")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", default=8765, type=int)
    serve_parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open the default browser automatically",
    )

    service_parser = subparsers.add_parser(
        "serve-commercial",
        help="Start the authenticated commercial API",
    )
    service_parser.add_argument("--host", default="127.0.0.1")
    service_parser.add_argument("--port", default=8766, type=int)
    return parser


def _write_output(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


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
    except Exception as exc:  # noqa: BLE001 - CLI converts parser/library failures to a clean exit code.
        print(f"Audit failed: {exc}", file=sys.stderr)
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

    if args.output:
        output = args.output
        if output.suffix.lower() != extension:
            output = output.with_suffix(extension)
        _write_output(output, rendered)
        print(output.resolve())
    else:
        print(rendered)
    return 0


def _run_server(args: argparse.Namespace) -> int:
    import uvicorn

    url = f"http://{args.host}:{args.port}"
    print(f"ICS Commitment Audit Workbench: {url}")
    print("Press Ctrl+C to stop.")
    if not args.no_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    uvicorn.run(
        "ics_commitment_audit.web:app",
        host=args.host,
        port=args.port,
        log_level="info",
    )
    return 0


def _run_commercial_server(args: argparse.Namespace) -> int:
    import uvicorn

    print(
        f"ICS commercial API: http://{args.host}:{args.port}/v1/docs",
    )
    uvicorn.run(
        "ics_commitment_audit.commercial:app",
        host=args.host,
        port=args.port,
        log_level="info",
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "audit":
        return _run_audit(args)
    if args.command == "serve":
        return _run_server(args)
    if args.command == "serve-commercial":
        return _run_commercial_server(args)
    parser.error("Unknown command")
    return 2
