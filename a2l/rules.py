"""Versioned, explainable rule packs.

The prototype ships with ``rules/generic_180.json``: a deliberately generic,
educational rule pack that is *not* a real PDK.  A production deployment must
replace it with a foundry/company rule pack and calibrate the overhead factors
against completed layouts.

Rules are data, not code.  Every area number in the report can be traced back
to a rule key, which is the minimum requirement for a layout engineer to trust
an early estimate.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class RuleError(ValueError):
    pass


@dataclass
class Rules:
    data: dict[str, Any]
    path: Path | None = None

    @property
    def name(self) -> str:
        return str(self.data.get("name", "unknown"))

    @property
    def description(self) -> str:
        return str(self.data.get("description", ""))

    @property
    def confidence(self) -> str:
        return str(self.data.get("confidence", "unspecified"))

    @property
    def owner(self) -> str:
        return str(self.data.get("owner", "analog design engineer"))

    @property
    def approval(self) -> str:
        return str(self.data.get("approval", "requires analog owner approval"))

    def section(self, name: str) -> dict[str, Any]:
        value = self.data.get(name, {})
        if not isinstance(value, dict):
            raise RuleError(f"rule section {name!r} must be an object")
        return value

    def get(self, section: str, key: str, default: Any = None) -> Any:
        return self.section(section).get(key, default)

    def mos(self, key: str, default: Any = None) -> Any:
        return self.get("mos", key, default)

    def matching(self, key: str, default: Any = None) -> Any:
        return self.get("matching", key, default)

    def block(self, key: str, default: Any = None) -> Any:
        return self.get("block", key, default)

    def cap(self, key: str, default: Any = None) -> Any:
        return self.get("cap", key, default)

    def layout_delta(self, key: str, default: Any = None) -> Any:
        return self.get("layout_delta", key, default)

    def estimate(self, key: str, default: Any = None) -> Any:
        return self.get("estimate", key, default)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "path": str(self.path) if self.path else None,
            "confidence": self.confidence,
            "owner": self.owner,
            "approval": self.approval,
            "description": self.description,
            "data": self.data,
        }


_REQUIRED_SECTIONS = ("mos", "matching", "block", "estimate")


def load_rules(path: str | Path) -> Rules:
    file_path = Path(path)
    if not file_path.exists():
        raise RuleError(f"rule pack not found: {file_path}")

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuleError(f"invalid JSON in rule pack {file_path}: {exc}") from exc

    if not isinstance(data, dict):
        raise RuleError("rule pack must be a JSON object")
    for key in ("name", "owner", "approval"):
        if not str(data.get(key, "")).strip():
            raise RuleError(
                f"rule pack is missing {key!r}; role/rule ownership must be explicit "
                "(see rules/README.md)"
            )
    for section in _REQUIRED_SECTIONS:
        if section not in data:
            raise RuleError(f"rule pack is missing required section {section!r}")
        if not isinstance(data[section], dict):
            raise RuleError(f"rule section {section!r} must be an object")

    return Rules(data=data, path=file_path)


def default_rules_path() -> Path:
    """Locate the bundled generic rule pack.

    Works both from the repository root and when the package is installed next
    to the ``rules`` directory.
    """

    candidates = [
        Path(__file__).resolve().parent.parent / "rules" / "generic_180.json",
        Path.cwd() / "rules" / "generic_180.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise RuleError(
        "could not find rules/generic_180.json; pass --rules explicitly or run from the repository root"
    )
