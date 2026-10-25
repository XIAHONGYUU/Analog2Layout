"""Device-role taxonomy for analog schematic/layout handoff.

A *role* describes what a device is doing in the circuit (input pair, current
mirror, cascode, ...), not how it is drawn.  The role is the bridge between a
schematic that only knows W/L and a layout engineer who needs to know which
devices must be matched, isolated, or duplicated.

Real simulation/verification netlists usually carry semantics only in instance
names, so the name token is the primary reference source::

    M1_DP n1 vinp ntail vss nmos w=5u l=0.5u nf=4

An explicit annotation is an optional confirmed override::

    M1 n1 vinp ntail vss nmos w=5u l=0.5u nf=4 role=input_pair match=DP
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


ROLE_OWNER = "analog design engineer"
ROLE_POLICY = (
    "The role taxonomy is owned by the analog design team. AI/agents may "
    "propose roles and flag gaps, but they do not approve taxonomy changes."
)


@dataclass(frozen=True)
class RoleSpec:
    id: str
    label_zh: str
    label_en: str
    short: str
    band: str
    side: str
    priority: int
    critical: bool = False
    needs_match: bool = False
    needs_dummy: bool = False
    needs_isolation: bool = False
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "label_zh": self.label_zh,
            "label_en": self.label_en,
            "short": self.short,
            "band": self.band,
            "side": self.side,
            "priority": self.priority,
            "critical": self.critical,
            "needs_match": self.needs_match,
            "needs_dummy": self.needs_dummy,
            "needs_isolation": self.needs_isolation,
            "description": self.description,
        }


def _role(
    role_id: str,
    zh: str,
    en: str,
    short: str,
    band: str,
    side: str,
    priority: int,
    *,
    critical: bool = False,
    needs_match: bool = False,
    needs_dummy: bool = False,
    needs_isolation: bool = False,
    description: str = "",
) -> RoleSpec:
    return RoleSpec(
        id=role_id,
        label_zh=zh,
        label_en=en,
        short=short,
        band=band,
        side=side,
        priority=priority,
        critical=critical,
        needs_match=needs_match,
        needs_dummy=needs_dummy,
        needs_isolation=needs_isolation,
        description=description,
    )


# The order is not significant; ``priority`` controls placement order.
ROLES: dict[str, RoleSpec] = {
    "input_pair": _role(
        "input_pair",
        "差分输入对",
        "Input pair",
        "DP",
        "mid",
        "center",
        10,
        critical=True,
        needs_match=True,
        needs_dummy=True,
        needs_isolation=True,
        description="High-gain input pair; matching, symmetry and substrate isolation are critical.",
    ),
    "current_mirror": _role(
        "current_mirror",
        "电流镜",
        "Current mirror",
        "CM",
        "top",
        "center",
        20,
        critical=True,
        needs_match=True,
        needs_dummy=True,
        needs_isolation=True,
        description="Load or bias mirror; ratio accuracy and Vth matching dominate.",
    ),
    "cascode": _role(
        "cascode",
        "共源共栅",
        "Cascode",
        "CAS",
        "top",
        "right",
        30,
        critical=True,
        needs_match=True,
        needs_dummy=True,
        needs_isolation=True,
        description="Stacked devices for gain/isolation; source-drain routing is parasitic-sensitive.",
    ),
    "tail_current": _role(
        "tail_current",
        "尾电流源",
        "Tail current source",
        "TAIL",
        "bottom",
        "center",
        60,
        critical=True,
        needs_match=True,
        needs_dummy=True,
        needs_isolation=True,
        description="Sets the input-pair bias; needs clean, symmetric current delivery.",
    ),
    "output_stage": _role(
        "output_stage",
        "输出级",
        "Output stage",
        "OUT",
        "mid",
        "right",
        40,
        critical=False,
        needs_match=False,
        needs_dummy=True,
        needs_isolation=False,
        description="Large-signal / drive stage; current density, electromigration and area dominate.",
    ),
    "compensation": _role(
        "compensation",
        "补偿电容",
        "Compensation capacitor",
        "COMP",
        "mid",
        "right",
        50,
        critical=True,
        needs_match=False,
        needs_dummy=False,
        needs_isolation=False,
        description="Miller or feed-forward capacitor; value and parasitic coupling matter.",
    ),
    "bias": _role(
        "bias",
        "偏置",
        "Bias",
        "BIAS",
        "bottom",
        "left",
        70,
        critical=False,
        needs_match=False,
        needs_dummy=False,
        needs_isolation=False,
        description="Bias generation and distribution.",
    ),
    "enable_switch": _role(
        "enable_switch",
        "使能管",
        "Enable switch",
        "EN",
        "bottom",
        "left",
        80,
        critical=False,
        needs_match=False,
        needs_dummy=True,
        needs_isolation=False,
        description="Power-down / enable switch; charge injection and leakage matter.",
    ),
    "adj_switch": _role(
        "adj_switch",
        "配置/Trim 开关",
        "Adjust/trim switch",
        "ADJ",
        "bottom",
        "left",
        90,
        critical=False,
        needs_match=False,
        needs_dummy=True,
        needs_isolation=False,
        description="Programmable adjustment switch; switch matching and dummy balance matter.",
    ),
    "sense": _role(
        "sense",
        "检测/采样",
        "Sense",
        "SNS",
        "mid",
        "right",
        45,
        critical=True,
        needs_match=True,
        needs_dummy=True,
        needs_isolation=True,
        description="Current/voltage sense device; small parasitics can corrupt the measurement.",
    ),
    "esd": _role(
        "esd",
        "ESD 保护",
        "ESD protection",
        "ESD",
        "periphery",
        "left",
        120,
        critical=False,
        needs_match=False,
        needs_dummy=False,
        needs_isolation=False,
        description="ESD device; usually rule-driven and placed at the pad ring.",
    ),
    "dummy": _role(
        "dummy",
        "Dummy 管",
        "Dummy device",
        "DM",
        "periphery",
        "left",
        110,
        critical=False,
        needs_match=False,
        needs_dummy=False,
        needs_isolation=False,
        description="Electrically inactive device used to preserve matching or etch uniformity.",
    ),
    "decap": _role(
        "decap",
        "去耦/补偿电容",
        "Decoupling capacitor",
        "DEC",
        "periphery",
        "right",
        100,
        critical=False,
        needs_match=False,
        needs_dummy=False,
        needs_isolation=False,
        description="Supply decoupling or explicit compensation capacitor.",
    ),
    "unknown": _role(
        "unknown",
        "未标注",
        "Unknown",
        "?",
        "bottom",
        "right",
        200,
        critical=False,
        needs_match=False,
        needs_dummy=False,
        needs_isolation=False,
        description="Role not resolved; area and layout intent are unreliable.",
    ),
}


# Name heuristics are deliberately conservative and ordered from most to least
# specific.  They are only used when ``role=`` is absent.
_NAME_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(^|[^a-z])(dummy|dm)([^a-z]|$)", re.I), "dummy"),
    (re.compile(r"(^|[^a-z])(decap|dec)([^a-z]|$)", re.I), "decap"),
    (re.compile(r"(^|[^a-z])(input|inp|inn|pair|diff|dp)([^a-z]|$)", re.I), "input_pair"),
    (re.compile(r"(^|[^a-z])(mirror|mir|cm)([^a-z]|$)", re.I), "current_mirror"),
    (re.compile(r"(^|[^a-z])(cascode|cas)([^a-z]|$)", re.I), "cascode"),
    (re.compile(r"(^|[^a-z])(tail)([^a-z]|$)", re.I), "tail_current"),
    (re.compile(r"(^|[^a-z])(enable|en)([^a-z]|$)", re.I), "enable_switch"),
    (re.compile(r"(^|[^a-z])(adj|trim|sel|sw)([^a-z]|$)", re.I), "adj_switch"),
    (re.compile(r"(^|[^a-z])(output|out)([^a-z]|$)", re.I), "output_stage"),
    (re.compile(r"(^|[^a-z])(bias|nbias|pbias|vb)([^a-z]|$)", re.I), "bias"),
    (re.compile(r"(^|[^a-z])(comp|cc)([^a-z]|$)", re.I), "compensation"),
    (re.compile(r"(^|[^a-z])(sense|sns)([^a-z]|$)", re.I), "sense"),
    (re.compile(r"(^|[^a-z])(esd)([^a-z]|$)", re.I), "esd"),
)


def infer_name_token(name: str) -> tuple[str, str] | None:
    """Return ``(role_id, token)`` inferred from a device name.

    The token is the literal role tag found in the name (``DP``, ``CM``,
    ``CAS``, ...).  In real simulation/verification netlists this is often the
    only semantic information available; it is a *reference source*, not a
    guarantee.
    """

    for pattern, role_id in _NAME_PATTERNS:
        match = pattern.search(name)
        if match:
            token = match.group(2).upper()
            return role_id, token
    return None


def infer_role_from_name(name: str) -> str | None:
    """Return a role inferred from a device name, or ``None``."""

    inferred = infer_name_token(name)
    return inferred[0] if inferred else None


def get_role(role_id: str | None) -> RoleSpec:
    return ROLES.get((role_id or "unknown").strip().lower(), ROLES["unknown"])


def resolve_role(device: Any) -> tuple[str, str]:
    """Resolve a device role.

    Returns ``(role_id, source)`` where source is one of ``explicit``,
    ``name`` or ``unknown``.
    """

    explicit = getattr(device, "params", {}).get("role")
    if explicit:
        role_id = str(explicit).strip().lower()
        if role_id in ROLES:
            return role_id, "explicit"
        return "unknown", f"explicit-invalid:{role_id}"

    inferred = infer_role_from_name(getattr(device, "name", ""))
    if inferred:
        return inferred, "name"
    return "unknown", "unknown"


def annotate_devices(netlist: Any) -> list[str]:
    """Apply role/match/group/layout annotations to every device in-place.

    Returns a list of human-readable warnings.  The parser has already placed
    ``role=``, ``match=``, ``group=`` and ``layout=`` into ``device.params``;
    this function resolves the role source and records where it came from.
    """

    warnings: list[str] = []
    for device in netlist.devices:
        role_id, source = resolve_role(device)
        device.role = role_id
        device.role_source = source
        device.match = _param(device, "match")
        device.match_source = "explicit" if device.match else None
        device.group = _param(device, "group")
        device.layout = _param(device, "layout")

        if role_id == "unknown":
            warnings.append(
                f"{device.name}: no role annotation and no semantic name token; "
                "area and layout intent will be marked unknown"
            )
        elif source.startswith("explicit-invalid"):
            warnings.append(
                f"{device.name}: unknown role {source.split(':', 1)[1]!r}; falling back to unknown"
            )

        spec = get_role(role_id)
        if device.match and len(device.match.strip()) == 0:
            device.match = None

        # In name-only netlists there is no match= parameter.  If the role
        # needs matching and the name carries a role tag, use that tag as a
        # *proposed* match group.  A human/validator can still override it.
        if source == "name" and not device.group:
            token = infer_name_token(device.name)
            if token:
                device.group = token[1]

        if not device.match and source == "name" and spec.needs_match:
            token = infer_name_token(device.name)
            if token:
                device.match = token[1]
                device.match_source = "name"

        if spec.needs_match and not device.match:
            warnings.append(
                f"{device.name}: role {role_id} needs a match group; "
                "add match= or give the instance a semantic name token"
            )

    return warnings


def _param(device: Any, key: str) -> str | None:
    value = getattr(device, "params", {}).get(key)
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def role_table() -> list[dict[str, Any]]:
    return [spec.to_dict() for spec in ROLES.values()]
