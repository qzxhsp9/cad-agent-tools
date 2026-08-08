from __future__ import annotations

from pathlib import Path

from cad_agent_tools.core import inspect_model
from cad_agent_tools.settings import Settings


STEP_SAMPLE = """ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('sample'),'2;1');
FILE_NAME('box.step','2026-08-08T00:00:00',('OpenAI'),('CAD'),'','','');
FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));
ENDSEC;
DATA;
#1=SI_UNIT(.MILLI.,.METRE.);
#2=CARTESIAN_POINT('',(0.,0.,0.));
ENDSEC;
END-ISO-10303-21;
"""


def make_settings(tmp_path: Path) -> Settings:
    return Settings(
        allowed_roots=(tmp_path.resolve(),),
        job_root=(tmp_path / "jobs").resolve(),
        max_file_mb=10,
        log_level="WARNING",
        allowed_roots_source="test",
        job_root_source="test",
    )


def test_step_lightweight_inspection(tmp_path: Path) -> None:
    step = tmp_path / "box.step"
    step.write_text(STEP_SAMPLE, encoding="utf-8")
    result = inspect_model(str(step), settings=make_settings(tmp_path))
    assert result["status"] == "partial"
    assert result["input"]["format_detected"] == "step"
    metadata = result["import"]["lightweight_metadata"]
    assert metadata["iso_10303_21_envelope"] is True
    assert metadata["entity_count_in_scanned_prefix"] == 2
    assert "millimetre" in metadata["unit_hints"]
    assert result["local_execution"]["network_service"] is False


def test_rejects_path_outside_allowed_root(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    outside = tmp_path / "outside"
    allowed.mkdir()
    outside.mkdir()
    step = outside / "box.step"
    step.write_text(STEP_SAMPLE, encoding="utf-8")
    settings = Settings(
        allowed_roots=(allowed.resolve(),),
        job_root=(tmp_path / "jobs").resolve(),
        max_file_mb=10,
        log_level="WARNING",
        allowed_roots_source="test",
        job_root_source="test",
    )
    result = inspect_model(str(step), settings=settings)
    assert result["status"] == "failed"
    assert result["errors"][0]["code"] == "INVALID_INPUT"
