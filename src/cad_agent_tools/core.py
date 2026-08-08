from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import __version__
from .inspectors import inspect_format_metadata, sha256_file
from .models import InspectionResult, NotAssessed, Notice
from .security import validate_input_path
from .settings import Settings


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_request_id() -> str:
    return f"CAD-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"


def failed_result(request_id: str, code: str, message: str) -> dict[str, Any]:
    return InspectionResult(
        schema_version="1.0.0",
        request_id=request_id,
        status="failed",
        tool={
            "name": "cad_inspect_model",
            "package": "cad-agent-tools",
            "version": __version__,
            "backend": "python-baseline",
            "occt_version": "NOT_ASSESSED",
        },
        errors=[Notice(code=code, message=message)],
        not_assessed=[NotAssessed(item="cad_model_inspection", reason=message)],
        timing={"finished_at": utc_now()},
    ).to_dict()


def _write_report(path: Path, result: dict[str, Any]) -> None:
    input_info = result.get("input") or {}
    import_info = result.get("import") or {}
    lines = [
        "# CAD 文件初步检查报告",
        "",
        f"- 请求：`{result['request_id']}`",
        f"- 状态：**{str(result['status']).upper()}**",
        f"- 文件：`{input_info.get('file_name', 'unknown')}`",
        f"- 大小：{input_info.get('file_size_bytes', 'unknown')} bytes",
        f"- SHA-256：`{input_info.get('sha256', 'unknown')}`",
        f"- 识别格式：`{input_info.get('format_detected', 'unknown')}`",
        "",
        "## 已执行",
        "",
        "- 本地文件存在性、扩展名、大小和 SHA-256 检查。",
        "- 文件格式的轻量文本或二进制头部检查。",
        "",
        "```json",
        json.dumps(import_info, ensure_ascii=False, indent=2),
        "```",
        "",
        "## 未执行",
        "",
    ]
    for item in result.get("not_assessed", []):
        lines.append(f"- `{item['item']}`：{item['reason']}")
    lines.extend(
        [
            "",
            "> 本报告不包含 OCCT 几何传输、拓扑统计、B-Rep 有效性或模型修复结论。",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def inspect_model(
    file_path: str,
    *,
    generate_report: bool = True,
    settings: Settings | None = None,
) -> dict[str, Any]:
    request_id = new_request_id()
    started = time.perf_counter()
    started_at = utc_now()
    settings = settings or Settings.load()

    try:
        path = validate_input_path(file_path, settings)
    except (OSError, ValueError) as exc:
        return failed_result(request_id, "INVALID_INPUT", str(exc))

    try:
        format_metadata = inspect_format_metadata(path)
        digest = sha256_file(path)
    except OSError as exc:
        return failed_result(request_id, "FILE_READ_FAILED", str(exc))

    result_obj = InspectionResult(
        schema_version="1.0.0",
        request_id=request_id,
        status="partial",
        tool={
            "name": "cad_inspect_model",
            "package": "cad-agent-tools",
            "version": __version__,
            "backend": "python-baseline",
            "occt_version": "NOT_ASSESSED",
        },
        input={
            "file_name": path.name,
            "file_path": str(path),
            "file_size_bytes": path.stat().st_size,
            "sha256": digest,
            "format_detected": format_metadata.get("format", path.suffix.lower().lstrip(".")),
            "read_only": True,
        },
        import_info={
            "lightweight_metadata": format_metadata,
            "geometry_transfer_performed": False,
        },
        warnings=[
            Notice(
                code="PYTHON_BASELINE_ONLY",
                message=(
                    "The install-and-run Python package performed a lightweight file inspection. "
                    "No OCCT geometry kernel operation was executed."
                ),
            )
        ],
        not_assessed=[
            NotAssessed("assembly_structure", "Requires a CAD kernel/XCAF backend"),
            NotAssessed("topology_counts", "Requires a CAD kernel backend"),
            NotAssessed("brep_validation", "Requires BRepCheck or an equivalent kernel check"),
            NotAssessed("free_and_non_manifold_edges", "Requires topology traversal"),
            NotAssessed("tolerance_distribution", "Requires loaded B-Rep entities"),
            NotAssessed("geometry_repair", "This package version is read-only"),
        ],
        timing={"started_at": started_at},
    )
    result = result_obj.to_dict()

    settings.job_root.mkdir(parents=True, exist_ok=True)
    job_dir = settings.job_root / request_id
    job_dir.mkdir(parents=False, exist_ok=False)
    result_path = job_dir / "result.json"

    if generate_report:
        report_path = job_dir / "report.md"
        result["artifacts"].append(
            {
                "type": "report",
                "path": str(report_path),
                "media_type": "text/markdown",
            }
        )
        _write_report(report_path, result)

    result["timing"]["finished_at"] = utc_now()
    result["timing"]["duration_ms"] = round((time.perf_counter() - started) * 1000, 3)
    result["local_execution"] = {
        "transport": "stdio",
        "network_service": False,
        "listening_port": None,
        "job_dir": str(job_dir),
        "job_root_source": settings.job_root_source,
    }
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    result["artifacts"].append(
        {
            "type": "raw-result",
            "path": str(result_path),
            "media_type": "application/json",
        }
    )
    # Rewrite once so result.json also contains its own artifact entry.
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result
