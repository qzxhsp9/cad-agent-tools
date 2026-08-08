from __future__ import annotations

import json
import os
import platform
import shutil
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import __version__
from .security import SUPPORTED_EXTENSIONS
from .settings import Settings


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _path_state(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "exists": path.exists(),
        "is_directory": path.is_dir(),
        "readable": os.access(path, os.R_OK) if path.exists() else False,
        "writable": os.access(path, os.W_OK) if path.exists() else False,
    }


def build_runtime_probe(settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or Settings.load()
    command_path = shutil.which("cad-agent-tools")
    package_dir = Path(__file__).resolve().parent

    job_root_ready = True
    job_root_error: str | None = None
    try:
        settings.job_root.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        job_root_ready = False
        job_root_error = str(exc)

    return {
        "status": "success" if job_root_ready else "partial",
        "package": {
            "name": "cad-agent-tools",
            "version": __version__,
            "installation": "directly-installed-python-command",
            "entry_command": "cad-agent-tools",
            "entry_command_resolved": command_path,
            "package_directory": str(package_dir),
            "transport": "stdio",
            "network_service": False,
            "listening_port": None,
            "lifecycle": "launched-on-demand-by-mcp-host",
        },
        "runtime": {
            "timestamp": utc_now(),
            "system": platform.system(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "hostname": socket.gethostname(),
            "python": sys.version,
            "python_executable": sys.executable,
            "cwd": str(Path.cwd()),
            "pid": os.getpid(),
        },
        "configuration": {
            "backend": "python-baseline",
            "supported_extensions": sorted(SUPPORTED_EXTENSIONS),
            "allowed_roots": [_path_state(path) for path in settings.allowed_roots],
            "allowed_roots_source": settings.allowed_roots_source,
            "job_root": str(settings.job_root),
            "job_root_source": settings.job_root_source,
            "job_root_ready": job_root_ready,
            "job_root_error": job_root_error,
            "log_file": str(settings.log_file),
            "log_file_source": settings.log_file_source,
            "max_file_mb": settings.max_file_mb,
            "log_level": settings.log_level,
        },
        "next_check": (
            "Call cad_inspect_model with an uploaded CAD file path under an allowed root."
            if job_root_ready
            else "Fix the job-root permission error before calling cad_inspect_model."
        ),
    }


def append_startup_event(
    settings: Settings,
    *,
    event: str,
    level: str = "INFO",
    details: dict[str, Any] | None = None,
) -> None:
    """Append a compact JSON-lines startup event without writing to stdout."""

    payload = {
        "timestamp": utc_now(),
        "level": level,
        "event": event,
        "version": __version__,
        "pid": os.getpid(),
        "python_executable": sys.executable,
        "cwd": str(Path.cwd()),
        "details": details or {},
    }
    try:
        settings.log_file.parent.mkdir(parents=True, exist_ok=True)
        with settings.log_file.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
            stream.write("\n")
    except OSError:
        # Diagnostics must never prevent the MCP process from starting.
        return
