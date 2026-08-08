from __future__ import annotations

import json
import os
import tempfile
import sys
from dataclasses import dataclass
from pathlib import Path


ENV_ALLOWED_ROOTS = "CAD_AGENT_ALLOWED_ROOTS"
ENV_JOB_ROOT = "CAD_AGENT_JOB_ROOT"
ENV_MAX_FILE_MB = "CAD_AGENT_MAX_FILE_MB"
ENV_LOG_LEVEL = "CAD_AGENT_LOG_LEVEL"


def _default_user_cache_root() -> Path:
    """Return a per-user cache directory using only the Python standard library."""

    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA")
        if base:
            return Path(base) / "cad-agent-tools"
        return Path.home() / "AppData" / "Local" / "cad-agent-tools"

    if sys.platform == "darwin":
        return Path.home() / "Library" / "Caches" / "cad-agent-tools"

    xdg_cache = os.environ.get("XDG_CACHE_HOME")
    if xdg_cache:
        return Path(xdg_cache) / "cad-agent-tools"
    return Path.home() / ".cache" / "cad-agent-tools"


def _deduplicate_paths(paths: list[Path]) -> tuple[Path, ...]:
    result: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        try:
            resolved = path.expanduser().resolve(strict=False)
        except OSError:
            continue
        key = os.path.normcase(str(resolved))
        if key not in seen:
            seen.add(key)
            result.append(resolved)
    return tuple(result)


def _parse_root_list(raw: str) -> list[Path]:
    value = raw.strip()
    if not value:
        return []

    # JSON arrays avoid ambiguity on Windows drive letters and Unix path separators.
    if value.startswith("["):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{ENV_ALLOWED_ROOTS} is not valid JSON") from exc
        if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
            raise ValueError(f"{ENV_ALLOWED_ROOTS} JSON value must be a string array")
        return [Path(item) for item in parsed if item.strip()]

    # Native os.pathsep is ';' on Windows and ':' on Unix.
    return [Path(item.strip()) for item in value.split(os.pathsep) if item.strip()]


@dataclass(frozen=True, slots=True)
class Settings:
    allowed_roots: tuple[Path, ...]
    job_root: Path
    max_file_mb: int
    log_level: str
    allowed_roots_source: str
    job_root_source: str

    @classmethod
    def load(cls) -> "Settings":
        configured_roots = os.environ.get(ENV_ALLOWED_ROOTS, "")
        if configured_roots.strip():
            roots = _deduplicate_paths(_parse_root_list(configured_roots))
            roots_source = ENV_ALLOWED_ROOTS
        else:
            # Zero-configuration defaults: an MCP host normally materializes uploads in
            # its working directory or the operating-system temporary directory.
            roots = _deduplicate_paths([Path.cwd(), Path(tempfile.gettempdir())])
            roots_source = "automatic:cwd+temp"

        configured_job_root = os.environ.get(ENV_JOB_ROOT, "").strip()
        if configured_job_root:
            job_root = Path(configured_job_root).expanduser().resolve(strict=False)
            job_source = ENV_JOB_ROOT
        else:
            job_root = (_default_user_cache_root() / "jobs").resolve(strict=False)
            job_source = "automatic:platform-user-cache"

        raw_max_mb = os.environ.get(ENV_MAX_FILE_MB, "2048")
        try:
            max_file_mb = int(raw_max_mb)
        except ValueError as exc:
            raise ValueError(f"{ENV_MAX_FILE_MB} must be an integer") from exc
        if max_file_mb <= 0:
            raise ValueError(f"{ENV_MAX_FILE_MB} must be greater than zero")

        log_level = os.environ.get(ENV_LOG_LEVEL, "WARNING").strip().upper() or "WARNING"
        return cls(
            allowed_roots=roots,
            job_root=job_root,
            max_file_mb=max_file_mb,
            log_level=log_level,
            allowed_roots_source=roots_source,
            job_root_source=job_source,
        )
