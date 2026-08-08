from __future__ import annotations

import logging
import platform
import socket
import sys
from pathlib import Path
from typing import Any

from mcp.server import MCPServer

from . import __version__
from .core import inspect_model
from .security import SUPPORTED_EXTENSIONS
from .settings import Settings

LOGGER = logging.getLogger(__name__)

mcp = MCPServer(
    "cad-agent-tools",
    title="CAD Agent Tools",
    description=(
        "Install-and-run local CAD inspection tools. The MCP host starts this Python "
        "package on demand over stdio; no HTTP service or listening port is used."
    ),
    instructions=(
        "Use cad_runtime_probe to inspect the runtime. Use cad_inspect_model for a "
        "local CAD attachment path. Treat only returned fields as facts. Anything in "
        "not_assessed was not checked."
    ),
    version=__version__,
)


@mcp.tool()
def cad_runtime_probe() -> dict[str, Any]:
    """Show how this directly installed package is running and where it can read files."""

    settings = Settings.load()
    return {
        "status": "success",
        "package": {
            "name": "cad-agent-tools",
            "version": __version__,
            "installation": "python-package-index-or-git",
            "entry_command": "cad-agent-tools",
            "transport": "stdio",
            "network_service": False,
            "listening_port": None,
            "lifecycle": "launched-on-demand-by-mcp-host",
        },
        "runtime": {
            "system": platform.system(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "hostname": socket.gethostname(),
            "python": sys.version,
            "python_executable": sys.executable,
            "cwd": str(Path.cwd()),
        },
        "configuration": {
            "backend": "python-baseline",
            "supported_extensions": sorted(SUPPORTED_EXTENSIONS),
            "allowed_roots": [str(path) for path in settings.allowed_roots],
            "allowed_roots_source": settings.allowed_roots_source,
            "job_root": str(settings.job_root),
            "job_root_source": settings.job_root_source,
            "max_file_mb": settings.max_file_mb,
        },
        "next_check": "Call cad_inspect_model with an uploaded file path under an allowed root.",
    }


@mcp.tool()
def cad_inspect_model(file_path: str, generate_report: bool = True) -> dict[str, Any]:
    """Perform a read-only lightweight inspection of a STEP/STP/BREP/IGES/STL file.

    Args:
        file_path: Local path or file:// URI supplied by the MCP host for an uploaded CAD file.
        generate_report: Generate a Markdown report in the package-managed user cache.
    """

    return inspect_model(file_path, generate_report=generate_report)


def run_stdio() -> None:
    """Run the MCP process over stdio. It opens no port and starts no network service."""

    mcp.run(transport="stdio")
