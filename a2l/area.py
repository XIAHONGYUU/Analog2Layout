"""Transparent, rule-based area estimation.

This is an *early planning* model, not a signoff extractor.  It answers three
questions that are otherwise answered only after a layout engineer has drawn
the block:

1. Which devices/groups dominate the area?
2. How much area do matching dummies, guard rings and routing add?
3. How uncertain is the estimate, and which rule produced it?

Every formula below is intentionally simple and documented.  The value is
traceability and relative comparison between architectures, not absolute
accuracy.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any

from .netlist import Device, Netlist
from .roles import RoleSpec, get_role
from .rules import Rules


@dataclass
class DeviceArea:
    name: str
    role: str
    role_source: str
    group: str
    match: str | None
    layout: str | None
    kind: str
    mos_type: str | None
    nodes: list[str]
    w_um: float
    l_um: float
    nf: int
    m: int
    total_w_um: float
    w_layout_um: float
    h_layout_um: float
    area_core_um2: float
    area_ring_um2: float
    area_routing_um2: float
    area_total_um2: float
    c_pf: float = 0.0
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "role": self.role,
            "role_source": self.role_source,
            "group": self.group,
            "match": self.match,
            "layout": self.layout,
            "kind": self.kind,
            "mos_type": self.mos_type,
            "w_um": round(self.w_um, 4),
            "l_um": round(self.l_um, 4),
            "nf": self.nf,
            "m": self.m,
            "total_w_um": round(self.total_w_um, 4),
            "w_layout_um": round(self.w_layout_um, 3),
            "h_layout_um": round(self.h_layout_um, 3),
            "area_core_um2": round(self.area_core_um2, 2),
            "area_ring_um2": round(self.area_ring_um2, 2),
            "area_routing_um2": round(self.area_routing_um2, 2),
            "area_total_um2": round(self.area_total_um2, 2),
            "c_pf": round(self.c_pf, 4),
            "notes": self.notes,
        }


@dataclass
class GroupArea:
    key: str
    role: str
    match: str | None
    devices: list[DeviceArea]
    area_no_dummy_um2: float
    dummy_count: int
    existing_dummy_count: int
    area_dummy_um2: float
    overhead_fraction: float
    area_with_dummy_um2: float
    area_low_um2: float
    area_high_um2: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "role": self.role,
            "match": self.match,
            "devices": [device.name for device in self.devices],
            "device_count": len(self.devices),
            "area_no_dummy_um2": round(self.area_no_dummy_um2, 2),
            "dummy_count": self.dummy_count,
            "existing_dummy_count": self.existing_dummy_count,
            "area_dummy_um2": round(self.area_dummy_um2, 2),
            "overhead_fraction": round(self.overhead_fraction, 4),
            "area_with_dummy_um2": round(self.area_with_dummy_um2, 2),
            "area_low_um2": round(self.area_low_um2, 2),
            "area_high_um2": round(self.area_high_um2, 2),
        }


@dataclass
class AreaReport:
    design: str
    rules_name: str
    rules_confidence: str
    rules_owner: str
    rules_approval: str
    width_convention: str
    devices: list[DeviceArea]
    groups: list[GroupArea]
    summary: dict[str, Any]
    warnings: list[str]
    by_role: dict[str, float]

    def device_map(self) -> dict[str, DeviceArea]:
        return {device.name: device for device in self.devices}

    def to_dict(self) -> dict[str, Any]:
        return {
            "design": self.design,
            "rules": {
                "name": self.rules_name,
                "confidence": self.rules_confidence,
                "owner": self.rules_owner,
                "approval": self.rules_approval,
            },
            "width_convention": self.width_convention,
            "devices": [device.to_dict() for device in self.devices],
            "groups": [group.to_dict() for group in self.groups],
            "summary": self.summary,
            "by_role_um2": {key: round(value, 2) for key, value in self.by_role.items()},
            "warnings": self.warnings,
        }


def _unique_warning(warnings: list[str], message: str) -> None:
    if message not in warnings:
        warnings.append(message)


def estimate_area(
    netlist: Netlist,
    rules: Rules,
    *,
    name: str | None = None,
    area_budget_um2: float | None = None,
) -> AreaReport:
    if area_budget_um2 is not None and area_budget_um2 <= 0:
        raise ValueError("area_budget_um2 must be > 0")

    width_convention = str(rules.data.get("width_convention", "per_finger")).lower()
    if width_convention not in ("per_finger", "total"):
        width_convention = "per_finger"

    warnings: list[str] = list(netlist.warnings)
    device_areas: list[DeviceArea] = []

    for device in netlist.devices:
        try:
            area = _estimate_device(device, rules, width_convention, warnings)
        except ValueError as exc:
            _unique_warning(warnings, f"{device.name}: {exc}")
            area = _zero_device(device)
        device_areas.append(area)

    groups = _build_groups(device_areas, rules, warnings)
    summary, by_role = _summarize(
        device_areas,
        groups,
        rules,
        width_convention,
        area_budget_um2=area_budget_um2,
    )

    return AreaReport(
        design=name or netlist.name,
        rules_name=rules.name,
        rules_confidence=rules.confidence,
        rules_owner=rules.owner,
        rules_approval=rules.approval,
        width_convention=width_convention,
        devices=device_areas,
        groups=groups,
        summary=summary,
        warnings=warnings,
        by_role=by_role,
    )


def _zero_device(device: Device) -> DeviceArea:
    return DeviceArea(
        name=device.name,
        role=device.role or "unknown",
        role_source=device.role_source,
        group=device.group or device.match or device.name,
        match=device.match,
        layout=device.layout,
        kind=device.kind,
        mos_type=device.mos_type,
        nodes=list(device.nodes),
        w_um=0.0,
        l_um=0.0,
        nf=1,
        m=1,
        total_w_um=0.0,
        w_layout_um=0.0,
        h_layout_um=0.0,
        area_core_um2=0.0,
        area_ring_um2=0.0,
        area_routing_um2=0.0,
        area_total_um2=0.0,
        notes=["area unavailable"],
    )


def _estimate_device(
    device: Device,
    rules: Rules,
    width_convention: str,
    warnings: list[str],
) -> DeviceArea:
    role_id = device.role or "unknown"
    spec = get_role(role_id)
    group = device.group or device.match or device.name

    if device.kind == "cap":
        return _estimate_cap(device, rules, spec, group, warnings)

    if device.kind != "mos":
        return _zero_device(device)

    w = device.w_um
    l = device.l_um
    nf = device.nf
    m = device.m

    if w <= 0:
        raise ValueError("W must be > 0")
    if l <= 0:
        raise ValueError("L must be > 0")

    total_w = device.total_width_um(width_convention)
    w_finger = total_w / max(1, nf * m)
    max_w = float(rules.mos("max_w_per_finger_um", 10.0))
    min_l = float(rules.mos("min_l_um", 0.0))

    if w_finger > max_w + 1e-9:
        _unique_warning(
            warnings,
            f"{device.name}: W/finger={w_finger:.2f} um exceeds rule maximum {max_w:.2f} um; "
            "consider more fingers",
        )

    if min_l and l + 1e-12 < min_l:
        _unique_warning(
            warnings,
            f"{device.name}: L={l:.3f} um is below rule minimum {min_l:.3f} um",
        )

    # Layout dimensions: fingers are laid side by side; the height is one
    # finger width plus OD extension on both sides.
    sd_ext = float(rules.mos("sd_ext_um", 0.30))
    od_ext = float(rules.mos("od_ext_um", 0.25))
    contact_spacing = float(rules.mos("contact_spacing_um", 0.22))
    finger_pitch = l + 2.0 * sd_ext + contact_spacing
    n_layout_fingers = max(nf * m, int(math.ceil(total_w / max_w)) if max_w > 0 else nf * m)
    w_layout = n_layout_fingers * finger_pitch
    h_layout = w_finger + 2.0 * od_ext

    core_area = w_layout * h_layout

    ring_area = 0.0
    if spec.critical and bool(rules.matching("guard_ring_for_critical", True)):
        ring_width = float(rules.mos("guard_ring_width_um", 0.80))
        ring_area = 2.0 * (w_layout + h_layout) * ring_width + 4.0 * ring_width * ring_width

    routing_overhead = float(rules.mos("routing_overhead", 0.18))
    # Align with AnalogLoop's area model: routing overhead applies to the
    # device plus its guard ring, not only to the OD area.
    routing_area = (core_area + ring_area) * routing_overhead
    total_area = core_area + ring_area + routing_area

    notes: list[str] = []
    if spec.critical:
        notes.append("critical device: guard ring included in estimate")
    if width_convention == "per_finger":
        notes.append("w treated as per-finger width")
    else:
        notes.append("w treated as total width")

    return DeviceArea(
        name=device.name,
        role=role_id,
        role_source=device.role_source,
        group=group,
        match=device.match,
        layout=device.layout,
        kind=device.kind,
        mos_type=device.mos_type,
        nodes=list(device.nodes),
        w_um=w,
        l_um=l,
        nf=nf,
        m=m,
        total_w_um=total_w,
        w_layout_um=w_layout,
        h_layout_um=h_layout,
        area_core_um2=core_area,
        area_ring_um2=ring_area,
        area_routing_um2=routing_area,
        area_total_um2=total_area,
        notes=notes,
    )


def _estimate_cap(
    device: Device,
    rules: Rules,
    spec: RoleSpec,
    group: str,
    warnings: list[str],
) -> DeviceArea:
    c_pf = device.c_pf
    if c_pf <= 0:
        raise ValueError("capacitance must be > 0")

    density = float(rules.cap("density_ff_per_um2", 1.5))
    if density <= 0:
        raise ValueError("cap.density_ff_per_um2 must be > 0")

    aspect = float(rules.cap("aspect_ratio", 1.5))
    area = c_pf * 1000.0 / density  # 1 pF = 1000 fF
    side = math.sqrt(area / max(aspect, 0.1))
    w_layout = side * max(aspect, 0.1)
    h_layout = side

    routing_overhead = float(rules.cap("routing_overhead", 0.10))
    routing_area = area * routing_overhead
    total_area = area + routing_area

    if spec.id == "compensation":
        note = "compensation cap; keep away from noisy nodes"
    elif spec.id == "decap":
        note = "decoupling cap; place near supply pins"
    else:
        note = "capacitor area from generic density rule"

    return DeviceArea(
        name=device.name,
        role=spec.id,
        role_source=device.role_source,
        group=group,
        match=device.match,
        layout=device.layout,
        kind=device.kind,
        mos_type=None,
        nodes=list(device.nodes),
        w_um=0.0,
        l_um=0.0,
        nf=1,
        m=1,
        total_w_um=0.0,
        w_layout_um=w_layout,
        h_layout_um=h_layout,
        area_core_um2=area,
        area_ring_um2=0.0,
        area_routing_um2=routing_area,
        area_total_um2=total_area,
        c_pf=c_pf,
        notes=[note],
    )


def _build_groups(
    device_areas: list[DeviceArea],
    rules: Rules,
    warnings: list[str],
) -> list[GroupArea]:
    buckets: dict[str, list[DeviceArea]] = defaultdict(list)
    for device in device_areas:
        key = device.match or device.group or device.name
        buckets[key].append(device)

    groups: list[GroupArea] = []
    for key, devices in buckets.items():
        role = _dominant_role(devices)
        spec = get_role(role)
        match = next((device.match for device in devices if device.match), None)

        area_no_dummy = sum(device.area_total_um2 for device in devices)
        existing_dummy = sum(1 for device in devices if device.role == "dummy")
        dummy_count = 0
        if match and spec.needs_dummy:
            required = int(rules.matching("dummy_per_group", 2))
            dummy_count = max(0, required - existing_dummy)
            if len(devices) == 1:
                _unique_warning(
                    warnings,
                    f"match group {key!r} has only one device; matching assumptions are weak",
                )

        avg_area = area_no_dummy / max(1, len(devices))
        dummy_area = avg_area * dummy_count * float(rules.matching("dummy_width_factor", 1.0))

        layout_text = " ".join((device.layout or "") for device in devices).lower()
        if match:
            if "centroid" in layout_text or role == "input_pair":
                overhead = float(rules.matching("common_centroid_overhead", 0.12))
            else:
                overhead = float(rules.matching("matching_overhead", 0.06))
        else:
            overhead = 0.0

        area_with_dummy = (area_no_dummy + dummy_area) * (1.0 + overhead)
        low_factor = float(rules.estimate("low_factor", 0.80))
        high_factor = float(rules.estimate("high_factor", 1.35))

        groups.append(
            GroupArea(
                key=key,
                role=role,
                match=match,
                devices=devices,
                area_no_dummy_um2=area_no_dummy,
                dummy_count=dummy_count,
                existing_dummy_count=existing_dummy,
                area_dummy_um2=dummy_area,
                overhead_fraction=overhead,
                area_with_dummy_um2=area_with_dummy,
                area_low_um2=area_with_dummy * low_factor,
                area_high_um2=area_with_dummy * high_factor,
            )
        )

    groups.sort(key=lambda group: (-group.area_with_dummy_um2, group.key))
    return groups


def _dominant_role(devices: list[DeviceArea]) -> str:
    counts = Counter(device.role for device in devices)
    if not counts:
        return "unknown"
    # Prefer a critical role when a functional group mixes roles.
    def rank(item: tuple[str, int]) -> tuple[int, int, int]:
        role_id, count = item
        spec = get_role(role_id)
        return (1 if spec.critical else 0, count, -spec.priority)

    return max(counts.items(), key=rank)[0]


def _summarize(
    device_areas: list[DeviceArea],
    groups: list[GroupArea],
    rules: Rules,
    width_convention: str,
    *,
    area_budget_um2: float | None = None,
) -> tuple[dict[str, Any], dict[str, float]]:
    core_area = sum(device.area_core_um2 for device in device_areas)
    ring_area = sum(device.area_ring_um2 for device in device_areas)
    device_routing = sum(device.area_routing_um2 for device in device_areas)
    active_area = sum(device.area_total_um2 for device in device_areas)
    dummy_area = sum(group.area_dummy_um2 for group in groups)
    matched_area = sum(group.area_with_dummy_um2 for group in groups)
    matching_overhead = max(0.0, matched_area - active_area - dummy_area)

    periphery = float(rules.block("periphery_um", 4.0))
    routing_overhead = float(rules.block("routing_overhead", 0.10))

    def add_periphery(parts: float) -> float:
        if parts <= 0:
            return 0.0
        side = math.sqrt(parts)
        return (side + 2.0 * periphery) ** 2 * (1.0 + routing_overhead)

    block_area = add_periphery(matched_area)
    block_no_dummy = add_periphery(active_area)
    periphery_area = max(0.0, block_area - matched_area)

    low_factor = float(rules.estimate("low_factor", 0.80))
    high_factor = float(rules.estimate("high_factor", 1.35))
    reserve_fraction = float(rules.block("reserve_fraction", 0.08))
    reserve_area = block_area * reserve_fraction
    envelope_area = block_area + reserve_area

    by_role: dict[str, float] = defaultdict(float)
    for device in device_areas:
        by_role[device.role] += device.area_total_um2

    mos_count = sum(1 for device in device_areas if device.kind == "mos")
    cap_count = sum(1 for device in device_areas if device.kind == "cap")
    total_devices = len(device_areas)

    source_counts: dict[str, int] = {"name": 0, "explicit": 0, "other": 0, "unknown": 0}
    for device in device_areas:
        if device.role_source == "explicit":
            source_counts["explicit"] += 1
        elif device.role_source == "name":
            source_counts["name"] += 1
        else:
            source_counts["other"] += 1
    source_counts["unknown"] = sum(1 for device in device_areas if device.role == "unknown")
    all_roles_known = source_counts["unknown"] == 0

    dominant = sorted(by_role.items(), key=lambda item: -item[1])[:4]

    def share(area: float) -> float:
        return round(area / max(block_area, 1e-9), 4)

    low_area = block_area * low_factor
    high_area = block_area * high_factor
    if area_budget_um2 is None:
        area_gate = {
            "status": "UNSET",
            "budget_um2": None,
            "budget_mm2": None,
            "headroom_um2": None,
            "shortfall_um2": None,
            "overlap_um2": None,
        }
    else:
        budget = float(area_budget_um2)
        if high_area <= budget:
            status = "PASS"
            headroom = budget - high_area
            shortfall = 0.0
            overlap = 0.0
        elif low_area > budget:
            status = "REJECT"
            headroom = 0.0
            shortfall = low_area - budget
            overlap = 0.0
        else:
            status = "UNCERTAIN"
            headroom = 0.0
            shortfall = 0.0
            overlap = max(0.0, high_area - budget)
        area_gate = {
            "status": status,
            "budget_um2": round(budget, 2),
            "budget_mm2": round(budget / 1e6, 6),
            "headroom_um2": round(headroom, 2),
            "shortfall_um2": round(shortfall, 2),
            "overlap_um2": round(overlap, 2),
        }

    summary = {
        "device_count": total_devices,
        "mos_count": mos_count,
        "cap_count": cap_count,
        "group_count": len(groups),
        "width_convention": width_convention,
        # Five-level area hierarchy: core < active < matched < block < envelope.
        "area_core_um2": round(core_area, 2),
        "area_active_um2": round(active_area, 2),
        "area_matched_um2": round(matched_area, 2),
        "area_block_um2": round(block_area, 2),
        "area_envelope_um2": round(envelope_area, 2),
        # Breakdown buckets.
        "area_ring_um2": round(ring_area, 2),
        "area_device_routing_um2": round(device_routing, 2),
        "area_dummy_um2": round(dummy_area, 2),
        "dummy_area_um2": round(dummy_area, 2),
        "area_matching_overhead_um2": round(matching_overhead, 2),
        "area_periphery_um2": round(periphery_area, 2),
        "area_reserved_um2": round(reserve_area, 2),
        # Backward-compatible aliases.
        "area_parts_no_dummy_um2": round(active_area, 2),
        "area_parts_with_dummy_um2": round(matched_area, 2),
        "area_block_no_dummy_um2": round(block_no_dummy, 2),
        "area_block_with_dummy_um2": round(block_area, 2),
        # Fractions are relative to the committed block area.
        "area_core_fraction": share(core_area),
        "area_active_fraction": share(active_area),
        "area_matched_fraction": share(matched_area),
        "area_block_fraction": 1.0,
        "area_envelope_fraction": share(envelope_area),
        "area_ring_fraction": share(ring_area),
        "area_device_routing_fraction": share(device_routing),
        "area_dummy_fraction": share(dummy_area),
        "area_matching_fraction": share(matching_overhead),
        "area_periphery_fraction": share(periphery_area),
        "area_reserve_fraction": share(reserve_area),
        # Ranges / mm2 convenience values.
        "area_nominal_um2": round(block_area, 2),
        "area_low_um2": round(low_area, 2),
        "area_high_um2": round(high_area, 2),
        "area_nominal_mm2": round(block_area / 1e6, 6),
        "area_mm2": round(block_area / 1e6, 6),
        "area_envelope_mm2": round(envelope_area / 1e6, 6),
        "area_low_mm2": round(block_area * low_factor / 1e6, 6),
        "area_high_mm2": round(block_area * high_factor / 1e6, 6),
        "area_reserved_mm2": round(reserve_area / 1e6, 6),
        "area_gate": area_gate,
        # Ownership / annotation provenance.
        "role_sources": source_counts,
        "all_roles_known": all_roles_known,
        "dominant_roles": [
            {"role": role, "area_um2": round(area, 2), "share": round(area / max(active_area, 1e-9), 4)}
            for role, area in dominant
        ],
        "notes": [
            "Early planning estimate, not a signoff area.",
            "Area hierarchy: core < active < matched < block < envelope.",
            f"Estimate range is {low_factor:.2f}x to {high_factor:.2f}x the nominal block area.",
            f"{reserve_fraction * 100:.0f}% of the nominal block area is reported separately as PEX-fix reserve.",
            "Role taxonomy and rule values are owned by the analog design engineer; AI proposals need owner review.",
        ],
    }
    return summary, dict(by_role)
