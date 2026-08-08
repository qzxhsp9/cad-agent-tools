from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import unquote, urlparse

from .settings import Settings

SUPPORTED_EXTENSIONS = {".step", ".stp", ".brep", ".iges", ".igs", ".stl"}


def normalize_local_path(value: str) -> Path:
    raw = value.strip()
    if not raw:
        raise ValueError("file_path must not be empty")

    if raw.lower().startswith("file://"):
        parsed = urlparse(raw)
        raw = unquote(parsed.path)
        if os.name == "nt" and raw.startswith("/") and len(raw) >= 3 and raw[2] == ":":
            raw = raw[1:]

    return Path(raw).expanduser().resolve(strict=False)


def path_is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def validate_input_path(file_path: str, settings: Settings) -> Path:
    path = normalize_local_path(file_path)
    if not path.exists():
        raise ValueError(f"Input file does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"Input path is not a regular file: {path}")
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(f"Unsupported CAD extension '{path.suffix}'. Supported: {supported}")
    if not any(path_is_within(path, root) for root in settings.allowed_roots):
        roots = [str(root) for root in settings.allowed_roots]
        raise ValueError(
            "Input file is outside the permitted roots. "
            f"Permitted roots: {roots}. Set CAD_AGENT_ALLOWED_ROOTS only when needed."
        )
    max_bytes = settings.max_file_mb * 1024 * 1024
    if path.stat().st_size > max_bytes:
        raise ValueError(
            f"Input file exceeds CAD_AGENT_MAX_FILE_MB={settings.max_file_mb}: {path}"
        )
    return path
