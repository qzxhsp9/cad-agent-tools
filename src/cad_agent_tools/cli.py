from __future__ import annotations

import argparse
import json
import logging
import sys
from typing import Sequence

from . import __version__
from .diagnostics import append_startup_event, build_runtime_probe
from .settings import Settings

LOGGER = logging.getLogger(__name__)


def _configure_logging() -> Settings:
    try:
        settings = Settings.load()
    except ValueError as exc:
        # Do not hide invalid configuration; write only to stderr so stdio stdout stays clean.
        sys.stderr.write(f"cad-agent-tools configuration error: {exc}\n")
        raise

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(logging.INFO)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(getattr(logging, settings.log_level, logging.WARNING))
    stderr_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    root.addHandler(stderr_handler)

    return settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cad-agent-tools",
        description=(
            "Directly installed local stdio MCP tools for CAD files. With no subcommand, "
            "starts the MCP process immediately."
        ),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command")

    inspect_parser = sub.add_parser(
        "inspect-file", help="Run the baseline file inspector without an MCP host"
    )
    inspect_parser.add_argument("file_path")
    inspect_parser.add_argument("--no-report", action="store_true")
    inspect_parser.add_argument("--compact", action="store_true")

    doctor_parser = sub.add_parser(
        "doctor", help="Print installation, PATH, runtime and writable-directory diagnostics"
    )
    doctor_parser.add_argument("--compact", action="store_true")

    sub.add_parser("mcp", help="Start the stdio MCP process explicitly")
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    settings = _configure_logging()
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "inspect-file":
        from .core import inspect_model

        result = inspect_model(args.file_path, generate_report=not args.no_report)
        print(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=None if args.compact else 2,
            )
        )
        raise SystemExit(0 if result.get("status") != "failed" else 2)

    if args.command == "doctor":
        result = build_runtime_probe(settings)
        print(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=None if args.compact else 2,
            )
        )
        raise SystemExit(0 if result.get("status") == "success" else 2)

    # No argument is intentionally the production MCP entry point used by AIDT.
    # Import lazily so --version and doctor remain available even during troubleshooting.
    append_startup_event(
        settings,
        event="stdio_start_requested",
        details={"argv": list(sys.argv), "mode": args.command or "default"},
    )
    LOGGER.info("Starting cad-agent-tools %s over stdio", __version__)
    try:
        from .mcp_app import run_stdio

        run_stdio()
    except BaseException as exc:
        append_startup_event(
            settings,
            event="stdio_start_failed",
            level="ERROR",
            details={"error_type": type(exc).__name__, "message": str(exc)},
        )
        LOGGER.exception("cad-agent-tools stdio process terminated during startup or execution")
        raise


if __name__ == "__main__":
    main()
