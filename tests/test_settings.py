from __future__ import annotations

from pathlib import Path

from cad_agent_tools.settings import Settings


def test_defaults_do_not_require_fixed_directories(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("CAD_AGENT_ALLOWED_ROOTS", raising=False)
    monkeypatch.delenv("CAD_AGENT_JOB_ROOT", raising=False)
    settings = Settings.load()
    assert tmp_path.resolve() in settings.allowed_roots
    assert settings.allowed_roots_source == "automatic:cwd+temp"
    assert settings.job_root_source == "automatic:platform-user-cache"
    assert "D:/" not in str(settings.job_root)
