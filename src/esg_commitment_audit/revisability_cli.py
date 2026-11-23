from __future__ import annotations

import argparse
import sys
import threading
import webbrowser
from pathlib import Path

from . import __version__
from .api import audit_revisability_bytes, audit_revisability_version_bytes
from .benchmark import audit_revisability_benchmark
from .benchmark_report import render_benchmark_json, render_benchmark_markdown
from .evidence_pack import audit_evidence_pack_bundle, seal_evidence_pack_manifest
from .evidence_pack_report import (
    render_evidence_pack_html,
    render_evidence_pack_json,
    render_evidence_pack_markdown,
)
from .revisability_report import (
    render_revisability_html,
    render_revisability_json,
    render_revisability_markdown,
)
from .revisability_version_report import (
    render_version_trace_html,
    render_version_trace_json,
    render_version_trace_markdown,
)

PROFILES = (
    "general",
    "news_media",
    "advertising",
    "insurance",
    "industrial_design",
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-revisability-audit",
        description="AI Alignment Revisability Audit workbench",
    )
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit_parser = subparsers.add_parser(
        "audit",
        help="Audit one AI policy, constitution, model card, or governance document",
    )
    audit_parser.add_argument("input", type=Path)
    audit_parser.add_argument("--profile", choices=PROFILES, default="general")
    audit_parser.add_argument(
        "--format",
        choices=("markdown", "json", "html"),
        default="markdown",
        dest="output_format",
    )
    audit_parser.add_argument("--output", type=Path)

    compare_parser = subparsers.add_parser(
        "compare",
        help="Compare a previous and current AI governance document",
    )
    compare_parser.add_argument("previous", type=Path)
    compare_parser.add_argument("current", type=Path)
    compare_parser.add_argument("--profile", choices=PROFILES, default="general")
    compare_parser.add_argument(
        "--format",
        choices=("markdown", "json", "html"),
        default="markdown",
        dest="output_format",
    )
    compare_parser.add_argument("--output", type=Path)

    evidence_parser = subparsers.add_parser(
        "evidence-pack",
        help="Validate a manifest or ZIP evidence pack and propose grade upgrades",
    )
    evidence_parser.add_argument("manifest_or_zip", type=Path)
    evidence_parser.add_argument(
        "--format",
        choices=("markdown", "json", "html"),
        default="markdown",
        dest="output_format",
    )
    evidence_parser.add_argument("--output", type=Path)

    evidence_seal_parser = subparsers.add_parser(
        "evidence-pack-seal",
        help="Compute and pin SHA-256 hashes in a new sealed manifest",
    )
    evidence_seal_parser.add_argument("manifest", type=Path)
    evidence_seal_parser.add_argument("--output", type=Path)

    benchmark_parser = subparsers.add_parser(
        "benchmark",
        help="Score the frozen real-policy benchmark and evaluate release gates",
    )
    benchmark_parser.add_argument("dataset", type=Path)
    benchmark_parser.add_argument(
        "--sources",
        type=Path,
        help="Directory containing source snapshots; defaults to dataset directory",
    )
    benchmark_parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        dest="output_format",
    )
    benchmark_parser.add_argument("--output", type=Path)
    benchmark_parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with status 1 when a benchmark gate fails",
    )

    serve_parser = subparsers.add_parser(
        "serve",
        help="Open the local AI Revisability Audit workbench",
    )
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", default=8765, type=int)
    serve_parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open the default browser automatically",
    )
    return parser


def _render_audit(report, output_format: str) -> tuple[str, str]:
    if output_format == "json":
        return render_revisability_json(report), ".json"
    if output_format == "html":
        return render_revisability_html(report), ".html"
    return render_revisability_markdown(report), ".md"


def _render_compare(report, output_format: str) -> tuple[str, str]:
    if output_format == "json":
        return render_version_trace_json(report), ".json"
    if output_format == "html":
        return render_version_trace_html(report), ".html"
    return render_version_trace_markdown(report), ".md"


def _emit(rendered: str, output: Path | None, extension: str) -> int:
    if output is None:
        print(rendered)
        return 0
    final_output = (
        output if output.suffix.lower() == extension else output.with_suffix(extension)
    )
    final_output.parent.mkdir(parents=True, exist_ok=True)
    final_output.write_text(rendered, encoding="utf-8")
    print(final_output.resolve())
    return 0


def _run_audit(args: argparse.Namespace) -> int:
    if not args.input.is_file():
        print(f"Input file not found: {args.input}", file=sys.stderr)
        return 2
    try:
        report = audit_revisability_bytes(
            args.input.read_bytes(),
            args.input.name,
            profile=args.profile,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Revisability audit failed: {exc}", file=sys.stderr)
        return 2
    rendered, extension = _render_audit(report, args.output_format)
    return _emit(rendered, args.output, extension)


def _run_compare(args: argparse.Namespace) -> int:
    for path in (args.previous, args.current):
        if not path.is_file():
            print(f"Input file not found: {path}", file=sys.stderr)
            return 2
    try:
        report = audit_revisability_version_bytes(
            args.previous.read_bytes(),
            args.previous.name,
            args.current.read_bytes(),
            args.current.name,
            profile=args.profile,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Version comparison failed: {exc}", file=sys.stderr)
        return 2
    rendered, extension = _render_compare(report, args.output_format)
    return _emit(rendered, args.output, extension)


def _run_evidence_pack(args: argparse.Namespace) -> int:
    try:
        report = audit_evidence_pack_bundle(args.manifest_or_zip)
    except Exception as exc:  # noqa: BLE001
        print(f"Evidence-pack assessment failed: {exc}", file=sys.stderr)
        return 2
    if args.output_format == "json":
        rendered = render_evidence_pack_json(report)
        extension = ".json"
    elif args.output_format == "html":
        rendered = render_evidence_pack_html(report)
        extension = ".html"
    else:
        rendered = render_evidence_pack_markdown(report)
        extension = ".md"
    return _emit(rendered, args.output, extension)


def _run_evidence_pack_seal(args: argparse.Namespace) -> int:
    try:
        output = seal_evidence_pack_manifest(args.manifest, args.output)
    except Exception as exc:  # noqa: BLE001
        print(f"Evidence-pack sealing failed: {exc}", file=sys.stderr)
        return 2
    print(output)
    return 0


def _run_benchmark(args: argparse.Namespace) -> int:
    sources = args.sources or args.dataset.resolve().parent / "sources"
    try:
        report = audit_revisability_benchmark(args.dataset, sources)
    except Exception as exc:  # noqa: BLE001
        print(f"Benchmark evaluation failed: {exc}", file=sys.stderr)
        return 2
    if args.output_format == "json":
        rendered = render_benchmark_json(report)
        extension = ".json"
    else:
        rendered = render_benchmark_markdown(report)
        extension = ".md"
    exit_code = _emit(rendered, args.output, extension)
    if exit_code != 0:
        return exit_code
    if args.strict and not report.gate.passed:
        return 1
    return 0


def _run_server(args: argparse.Namespace) -> int:
    import uvicorn

    url = f"http://{args.host}:{args.port}/revisability"
    print(f"AI Alignment Revisability Audit: {url}")
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
    if args.command == "compare":
        return _run_compare(args)
    if args.command == "evidence-pack":
        return _run_evidence_pack(args)
    if args.command == "evidence-pack-seal":
        return _run_evidence_pack_seal(args)
    if args.command == "benchmark":
        return _run_benchmark(args)
    if args.command == "serve":
        return _run_server(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
