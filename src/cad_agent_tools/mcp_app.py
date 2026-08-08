from __future__ import annotations

import logging
from typing import Any

from mcp.server import MCPServer

from . import __version__
from .diagnostics import build_runtime_probe

LOGGER = logging.getLogger(__name__)

mcp = MCPServer(
    "cad-agent-tools",
    title="CAD Agent Tools",
    description=(
        "Directly installed local CAD inspection tools. The MCP host starts this Python "
        "command on demand over stdio; no HTTP service or listening port is used."
    ),
    instructions=(
        "Use cad_runtime_probe to inspect the runtime. Use cad_inspect_model for a local "
        "CAD attachment path. Treat only returned fields as facts. Anything in not_assessed "
        "was not checked."
    ),
    version=__version__,
)


@mcp.tool()
def cad_runtime_probe() -> dict[str, Any]:
    """Report package, PATH, stdio runtime, readable roots and diagnostic-log location."""

    return build_runtime_probe()


@mcp.tool()
def cad_inspect_model(file_path: str, generate_report: bool = True) -> dict[str, Any]:
    """Perform a read-only lightweight inspection of a STEP/STP/BREP/IGES/STL file.

    Args:
        file_path: Local path or file:// URI supplied by the MCP host for an uploaded CAD file.
        generate_report: Generate a Markdown report in the package-managed user cache.
    """

    # Keep startup fast: load the file-inspection implementation only when this tool is called.
    from .core import inspect_model

    return inspect_model(file_path, generate_report=generate_report)


def run_stdio() -> None:
    """Run the MCP process over stdio. It opens no port and starts no network service."""

    LOGGER.info("MCP stdio loop starting; tools=2")
    mcp.run(transport="stdio")
