from __future__ import annotations

import hashlib
import re
import struct
from pathlib import Path
from typing import Any

ENTITY_RE = re.compile(r"(?m)^\s*#\d+\s*=")
STEP_FIELD_PATTERNS = {
    "file_description": re.compile(r"FILE_DESCRIPTION\s*\((.*?)\)\s*;", re.I | re.S),
    "file_name": re.compile(r"FILE_NAME\s*\((.*?)\)\s*;", re.I | re.S),
    "file_schema": re.compile(r"FILE_SCHEMA\s*\((.*?)\)\s*;", re.I | re.S),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_text(path: Path, limit: int = 8 * 1024 * 1024) -> tuple[str, bool]:
    raw = path.read_bytes()[:limit]
    truncated = path.stat().st_size > limit
    return raw.decode("utf-8", errors="replace"), truncated


def _compact_step_value(value: str) -> str:
    return " ".join(value.replace("\r", " ").replace("\n", " ").split())[:2000]


def inspect_step(path: Path) -> dict[str, Any]:
    text, truncated = _safe_text(path)
    upper = text.upper()
    fields: dict[str, str | None] = {}
    for name, pattern in STEP_FIELD_PATTERNS.items():
        match = pattern.search(text)
        fields[name] = _compact_step_value(match.group(1)) if match else None

    unit_hints: list[str] = []
    candidates = {
        "millimetre": (".MILLI.,.METRE.", "MILLIMETRE"),
        "metre": ("SI_UNIT($,.METRE.)", "SI_UNIT(.NONE.,.METRE.)"),
        "inch": ("'INCH'", '"INCH"'),
        "degree": ("PLANE_ANGLE_UNIT", "DEGREE"),
    }
    for label, tokens in candidates.items():
        if any(token in upper for token in tokens):
            unit_hints.append(label)

    return {
        "format": "step",
        "iso_10303_21_envelope": "ISO-10303-21" in upper,
        "header": fields,
        "entity_count_in_scanned_prefix": len(ENTITY_RE.findall(text)),
        "unit_hints": unit_hints,
        "scan_truncated": truncated,
        "fact_scope": "textual STEP envelope/header scan; not a geometry transfer",
    }


def inspect_stl(path: Path) -> dict[str, Any]:
    size = path.stat().st_size
    with path.open("rb") as stream:
        head = stream.read(84)

    binary_candidate = False
    triangle_count: int | None = None
    expected_size: int | None = None
    if len(head) >= 84:
        triangle_count = struct.unpack("<I", head[80:84])[0]
        expected_size = 84 + triangle_count * 50
        binary_candidate = expected_size == size

    if binary_candidate:
        return {
            "format": "stl",
            "encoding": "binary",
            "triangle_count": triangle_count,
            "file_size_matches_triangle_count": True,
        }

    text, truncated = _safe_text(path)
    lower = text.lower()
    return {
        "format": "stl",
        "encoding": "ascii" if lower.lstrip().startswith("solid") else "unknown",
        "triangle_count_in_scanned_prefix": lower.count("facet normal"),
        "scan_truncated": truncated,
    }


def inspect_iges(path: Path) -> dict[str, Any]:
    text, truncated = _safe_text(path)
    lines = text.splitlines()
    section_counts = {key: 0 for key in ("S", "G", "D", "P", "T")}
    for line in lines:
        if len(line) >= 73 and line[72] in section_counts:
            section_counts[line[72]] += 1
    return {
        "format": "iges",
        "section_line_counts_in_scanned_prefix": section_counts,
        "scan_truncated": truncated,
        "fact_scope": "IGES record scan; not a geometry transfer",
    }


def inspect_brep(path: Path) -> dict[str, Any]:
    text, truncated = _safe_text(path, limit=256 * 1024)
    first_nonempty = next((line.strip() for line in text.splitlines() if line.strip()), "")
    return {
        "format": "brep",
        "first_nonempty_line": first_nonempty[:500],
        "looks_like_occt_brep": "DBRep_DrawableShape" in text[:4096]
        or "CASCADE Topology" in text[:4096],
        "scan_truncated": truncated,
        "fact_scope": "BREP header scan; not a B-Rep load or validity check",
    }


def inspect_format_metadata(path: Path) -> dict[str, Any]:
    ext = path.suffix.lower()
    if ext in {".step", ".stp"}:
        return inspect_step(path)
    if ext == ".stl":
        return inspect_stl(path)
    if ext in {".iges", ".igs"}:
        return inspect_iges(path)
    if ext == ".brep":
        return inspect_brep(path)
    return {"format": ext.lstrip("."), "fact_scope": "file metadata only"}
