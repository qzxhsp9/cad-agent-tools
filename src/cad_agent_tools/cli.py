from __future__ import annotations

import argparse
import json
import logging
import sys
from typing import Sequence

from . import __version__
from .core import inspect_model
from .settings import Settings


def _configure_logging() -> None:
    try:
        settings = Settings.load()
        level = settings.log_level
    except ValueError:
        level = "WARNING"
    logging.basicConfig(
        level=getattr(logging, level, logging.WARNING),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cad-agent-tools",
        description=(
            "Local stdio MCP tools for CAD files. With no subcommand, starts the MCP process."
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

    sub.add_parser("mcp", help="Start the stdio MCP process explicitly")
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    _configure_logging()
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "inspect-file":
        result = inspect_model(args.file_path, generate_report=not args.no_report)
        print(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=None if args.compact else 2,
            )
        )
        raise SystemExit(0 if result.get("status") != "failed" else 2)

    # No argument is intentionally the production MCP entry point used by AIDT/uvx.
    # Import lazily so local metadata inspection and --version remain usable even
    # while a developer is bootstrapping dependencies.
    from .mcp_app import run_stdio

    run_stdio()


if __name__ == "__main__":
    main()
