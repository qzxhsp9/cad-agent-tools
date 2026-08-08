from __future__ import annotations

import json
from pathlib import Path

from cad_agent_tools.diagnostics import append_startup_event, build_runtime_probe
from cad_agent_tools.settings import Settings


def make_settings(tmp_path: Path) -> Settings:
    return Settings(
        allowed_roots=(tmp_path.resolve(),),
        job_root=(tmp_path / "jobs").resolve(),
        max_file_mb=10,
        log_level="WARNING",
        allowed_roots_source="test",
        job_root_source="test",
        log_file=(tmp_path / "logs" / "startup.jsonl").resolve(),
        log_file_source="test",
    )


def test_runtime_probe_reports_direct_stdio_command(tmp_path: Path) -> None:
    result = build_runtime_probe(make_settings(tmp_path))
    assert result["status"] == "success"
    assert result["package"]["version"] == "0.5.1"
    assert result["package"]["transport"] == "stdio"
    assert result["package"]["network_service"] is False
    assert result["configuration"]["job_root_ready"] is True


def test_startup_event_is_written_without_stdout(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    append_startup_event(settings, event="test_event", details={"ok": True})
    payload = json.loads(settings.log_file.read_text(encoding="utf-8"))
    assert payload["event"] == "test_event"
    assert payload["details"]["ok"] is True
