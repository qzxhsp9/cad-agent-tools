from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Status = Literal["success", "partial", "failed"]


@dataclass(slots=True)
class Notice:
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class NotAssessed:
    item: str
    reason: str


@dataclass(slots=True)
class Artifact:
    type: str
    path: str
    media_type: str


@dataclass(slots=True)
class InspectionResult:
    schema_version: str
    request_id: str
    status: Status
    tool: dict[str, Any]
    input: dict[str, Any] | None = None
    import_info: dict[str, Any] | None = None
    structure: dict[str, Any] | None = None
    validation: dict[str, Any] | None = None
    quality: dict[str, Any] | None = None
    properties: dict[str, Any] | None = None
    errors: list[Notice] = field(default_factory=list)
    warnings: list[Notice] = field(default_factory=list)
    not_assessed: list[NotAssessed] = field(default_factory=list)
    artifacts: list[Artifact] = field(default_factory=list)
    timing: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        # Keep the public contract's historical key while avoiding Python's import keyword.
        data["import"] = data.pop("import_info")
        return data
