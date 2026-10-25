"""Floorplan intent generation.

The output is a floorplan sketch: a line drawing that communicates
relative placement, symmetry, matching groups, routing channels and proposed
dummy/decap reservations.  It is deliberately not a legal layout and not a
replacement for a placement engine.

The placement policy is template-like and explainable:

* critical groups are represented as groups of individual devices;
* the input pair straddles the symmetry axis;
* a current mirror sits above it and a tail current below it;
* the output stage and compensation cap sit to the right;
* bias and switches sit to the left/bottom;
* decaps and dummies sit on the periphery.
"""

from __future__ import annotations

import math
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from .area import AreaReport, GroupArea
from .roles import get_role
from .rules import Rules


@dataclass
class FPDevice:
    name: str
    role: str
    group: str
    match: str | None
    kind: str
    nodes: list[str]
    x: float
    y: float
    w: float
    h: float
    area_um2: float
    core_area_um2: float
    proposed: bool = False
    label: str = ""
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "role": self.role,
            "group": self.group,
            "match": self.match,
            "kind": self.kind,
            "x": round(self.x, 3),
            "y": round(self.y, 3),
            "w": round(self.w, 3),
            "h": round(self.h, 3),
            "area_um2": round(self.area_um2, 2),
            "proposed": self.proposed,
            "detail": self.detail,
        }


@dataclass
class FPGroup:
    key: str
    role: str
    band: str
    x: float
    y: float
    w: float
    h: float
    devices: list[FPDevice] = field(default_factory=list)
    symmetry: str | None = None
    label: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "role": self.role,
            "band": self.band,
            "x": round(self.x, 3),
            "y": round(self.y, 3),
            "w": round(self.w, 3),
            "h": round(self.h, 3),
            "devices": [device.name for device in self.devices],
            "symmetry": self.symmetry,
            "label": self.label,
        }


@dataclass
class Port:
    name: str
    net: str
    x: float
    y: float
    side: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "net": self.net,
            "x": round(self.x, 3),
            "y": round(self.y, 3),
            "side": self.side,
        }


@dataclass
class Channel:
    orientation: str
    x1: float
    y1: float
    x2: float
    y2: float
    label: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "orientation": self.orientation,
            "x1": round(self.x1, 3),
            "y1": round(self.y1, 3),
            "x2": round(self.x2, 3),
            "y2": round(self.y2, 3),
            "label": self.label,
        }


@dataclass
class Band:
    name: str
    y0: float
    y1: float

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "y0": round(self.y0, 3), "y1": round(self.y1, 3)}


@dataclass
class Floorplan:
    design: str
    rules_name: str
    width: float
    height: float
    groups: list[FPGroup]
    devices: list[FPDevice]
    ports: list[Port]
    channels: list[Channel]
    bands: list[Band]
    symmetry_x: float
    reserve: dict[str, Any]
    stats: dict[str, Any]
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "design": self.design,
            "rules": self.rules_name,
            "units": "um",
            "canvas": {"width": round(self.width, 3), "height": round(self.height, 3)},
            "symmetry_axis_x": round(self.symmetry_x, 3),
            "groups": [group.to_dict() for group in self.groups],
            "devices": [device.to_dict() for device in self.devices],
            "ports": [port.to_dict() for port in self.ports],
            "channels": [channel.to_dict() for channel in self.channels],
            "bands": [band.to_dict() for band in self.bands],
            "reserve": self.reserve,
            "stats": self.stats,
            "notes": self.notes,
        }


_BAND_ORDER = ("top", "mid", "bottom", "periphery")


def build_floorplan(
    design: str,
    report: AreaReport,
    rules: Rules,
) -> Floorplan:
    device_areas = report.device_map()
    group_areas = {group.key: group for group in report.groups}

    fp_groups: list[FPGroup] = []
    used_names: set[str] = set(device_areas)

    for key, area_group in group_areas.items():
        fp_group = _arrange_group(key, area_group, device_areas, rules, used_names)
        fp_groups.append(fp_group)

    _place_bands(fp_groups, rules)
    _shift_to_canvas(fp_groups, rules)
    width, height, reserve, _ = _canvas_geometry(fp_groups, rules)
    _center_content(fp_groups, reserve)
    symmetry_x = _symmetry_axis(fp_groups)

    devices = [device for group in fp_groups for device in group.devices]
    ports = _make_ports(fp_groups, width, height, symmetry_x)
    channels, bands = _make_channels_and_bands(fp_groups, width)

    total_device_area = sum(device.w * device.h for device in devices)
    core_area = sum(device.core_area_um2 for device in devices)
    content_right = max((group.x + group.w for group in fp_groups), default=16.0)
    content_bottom = max((group.y + group.h for group in fp_groups), default=34.0)
    block_width = max(1e-9, content_right - 16.0)
    block_height = max(1e-9, content_bottom - 34.0)
    content_area = block_width * block_height
    aspect_ratio = block_width / block_height
    squareness = min(block_width, block_height) / max(block_width, block_height)
    if aspect_ratio > 1.15:
        orientation = "landscape"
    elif aspect_ratio < 0.87:
        orientation = "portrait"
    else:
        orientation = "square-ish"
    groups_by_band = {
        band: sum(1 for group in fp_groups if group.band == band)
        for band in _BAND_ORDER
        if any(group.band == band for group in fp_groups)
    }
    rows = len(bands)
    arrangement = (
        f"{rows} rows ({'/'.join(band.name for band in bands)}); "
        f"groups/band: {', '.join(f'{band}={count}' for band, count in groups_by_band.items())}; "
        f"symmetry axis at x={symmetry_x:.1f} um"
    )
    stats = {
        "group_count": len(fp_groups),
        "device_count": sum(1 for device in devices if not device.proposed),
        "proposed_dummy_count": sum(1 for device in devices if device.proposed),
        "device_area_um2": round(total_device_area, 2),
        "core_area_um2": round(core_area, 2),
        "floorplan_area_um2": round(content_area, 2),
        "utilization": round(total_device_area / content_area, 4),
        "core_utilization": round(core_area / content_area, 4),
        "whitespace_fraction": round(max(0.0, 1.0 - total_device_area / content_area), 4),
        "block_width_um": round(block_width, 2),
        "block_height_um": round(block_height, 2),
        "aspect_ratio": round(aspect_ratio, 3),
        "squareness": round(squareness, 3),
        "orientation": orientation,
        "rows": rows,
        "groups_by_band": groups_by_band,
        "arrangement": arrangement,
    }

    notes = [
        "Floorplan sketch intent; not a DRC/LVS-clean layout.",
        "Proposed dummies/decaps are negotiation items, not silently inserted devices.",
        "Coordinates are in um with the origin at the top-left of the canvas.",
        "The symmetry axis is the vertical dashed line through the input pair.",
    ]
    if squareness < 0.5:
        notes.append(
            f"Block is elongated: aspect {aspect_ratio:.2f}, squareness {squareness:.2f}. "
            "Confirm this shape is compatible with the parent block."
        )

    return Floorplan(
        design=design,
        rules_name=rules.name,
        width=width,
        height=height,
        groups=fp_groups,
        devices=devices,
        ports=ports,
        channels=channels,
        bands=bands,
        symmetry_x=symmetry_x,
        reserve=reserve,
        stats=stats,
        notes=notes,
    )


def _group_label_text(key: str, short: str) -> str:
    return key if key.lower() == short.lower() else f"{key} · {short}"


def _sanitize(text: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", text).strip("_")
    return cleaned or "GRP"


def _arrange_group(
    key: str,
    area_group: GroupArea,
    device_areas: dict[str, Any],
    rules: Rules,
    used_names: set[str],
) -> FPGroup:
    spec = get_role(area_group.role)
    gap = max(0.8, float(rules.matching("group_spacing_um", 3.0)) * 0.35)
    devices: list[FPDevice] = []

    for name in [device.name for device in area_group.devices]:
        area = device_areas[name]
        w = max(area.w_layout_um, 1.6)
        h = max(area.h_layout_um, 2.2)
        if area.kind == "cap":
            detail = f"{area.c_pf:g} pF"
        elif area.kind == "mos":
            detail = f"{area.total_w_um:g}/{area.l_um:g} nf={area.nf}"
        else:
            detail = ""
        devices.append(
            FPDevice(
                name=area.name,
                role=area.role,
                group=area_group.key,
                match=area.match,
                kind=area.kind,
                nodes=list(area.nodes),
                x=0.0,
                y=0.0,
                w=w,
                h=h,
                area_um2=area.area_total_um2,
                core_area_um2=area.area_core_um2,
                label=area.name,
                detail=detail,
            )
        )

    if not devices:
        return FPGroup(
            key=key,
            role=area_group.role,
            band=spec.band,
            x=0.0,
            y=0.0,
            w=1.0,
            h=1.0,
            label=_group_label_text(key, spec.short),
        )

    if area_group.role == "input_pair" and len(devices) == 2:
        left, right = devices
        left.x = -(gap / 2.0 + left.w)
        left.y = 0.0
        right.x = gap / 2.0
        right.y = 0.0
        group_w = left.w + gap + right.w
        group_h = max(left.h, right.h)
    elif area_group.role == "cascode":
        y = 0.0
        group_w = 0.0
        for device in devices:
            device.x = 0.0
            device.y = y
            y += device.h + gap
            group_w = max(group_w, device.w)
        group_h = max(0.0, y - gap)
    else:
        x = 0.0
        group_h = 0.0
        for device in devices:
            device.x = x
            device.y = 0.0
            x += device.w + gap
            group_h = max(group_h, device.h)
        group_w = max(0.0, x - gap)

    # Normalize local coordinates first.
    min_x = min(device.x for device in devices)
    min_y = min(device.y for device in devices)
    for device in devices:
        device.x -= min_x
        device.y -= min_y

    # Proposed boundary dummies, sized from the group average.  They are drawn
    # outside the active devices so the layout engineer can see the matching
    # overhead rather than discovering it later.
    dummy_count = min(2, max(0, area_group.dummy_count))
    if dummy_count:
        avg_w = sum(device.w for device in devices) / len(devices)
        avg_h = sum(device.h for device in devices) / len(devices)
        dummy_w = max(1.0, avg_w * 0.85)
        dummy_h = max(1.0, avg_h * 0.85)
        dummy_specs: list[tuple[str, float, float]] = []
        if area_group.role == "cascode":
            dummy_specs.append(("BOT", 0.0, group_h + gap))
            if dummy_count > 1:
                dummy_specs.append(("TOP", 0.0, -dummy_h - gap))
        else:
            dummy_specs.append(("L", -dummy_w - gap, 0.0))
            if dummy_count > 1:
                dummy_specs.append(("R", group_w + gap, 0.0))

        for suffix, x, y in dummy_specs:
            name = f"DM_{_sanitize(key)}_{suffix}"
            index = 2
            while name in used_names:
                name = f"DM_{_sanitize(key)}_{suffix}{index}"
                index += 1
            used_names.add(name)
            devices.append(
                FPDevice(
                    name=name,
                    role="dummy",
                    group=area_group.key,
                    match=area_group.match,
                    kind="dummy",
                    nodes=[],
                    x=x,
                    y=y,
                    w=dummy_w,
                    h=dummy_h,
                    area_um2=0.0,
                    core_area_um2=0.0,
                    proposed=True,
                    label="DM",
                )
            )

    min_x = min(device.x for device in devices)
    min_y = min(device.y for device in devices)
    max_x = max(device.x + device.w for device in devices)
    max_y = max(device.y + device.h for device in devices)
    for device in devices:
        device.x -= min_x
        device.y -= min_y

    return FPGroup(
        key=key,
        role=area_group.role,
        band=spec.band,
        x=0.0,
        y=0.0,
        w=max_x - min_x,
        h=max_y - min_y,
        devices=devices,
        symmetry="vertical" if area_group.role == "input_pair" else None,
        label=_group_label_text(key, spec.short),
    )


def _place_bands(groups: list[FPGroup], rules: Rules) -> None:
    band_gap = max(2.0, float(rules.matching("band_spacing_um", 5.0)))
    by_band: dict[str, list[FPGroup]] = defaultdict(list)
    for group in groups:
        by_band[group.band].append(group)

    for band in by_band:
        by_band[band].sort(key=lambda group: (get_role(group.role).priority, group.key))

    y_cursor = 0.0
    for band in _BAND_ORDER:
        band_groups = by_band.get(band, [])
        if not band_groups:
            continue

        center = _choose_center(band, band_groups)
        if center is None:
            total = sum(group.w for group in band_groups) + band_gap * (len(band_groups) - 1)
            x_cursor = -total / 2.0
            for group in band_groups:
                group.x = x_cursor
                x_cursor += group.w + band_gap
        else:
            center.x = -center.w / 2.0

            left = [group for group in band_groups if group is not center and _side(group) == "left"]
            right = [group for group in band_groups if group is not center and _side(group) != "left"]

            cursor = center.x - band_gap
            for group in sorted(left, key=lambda item: (-get_role(item.role).priority, item.key)):
                group.x = cursor - group.w
                cursor = group.x - band_gap

            cursor = center.x + center.w + band_gap
            for group in sorted(right, key=lambda item: (get_role(item.role).priority, item.key)):
                group.x = cursor
                cursor += group.w + band_gap

        row_height = max(group.h for group in band_groups)
        for group in band_groups:
            group.y = y_cursor + (row_height - group.h) / 2.0
        y_cursor += row_height + band_gap

    # Devices are arranged in group-local coordinates; promote them to canvas
    # coordinates now that every group has a final position.
    for group in groups:
        for device in group.devices:
            device.x += group.x
            device.y += group.y


def _choose_center(band: str, groups: list[FPGroup]) -> FPGroup | None:
    preferred = {
        "top": ("current_mirror",),
        "mid": ("input_pair",),
        "bottom": ("tail_current",),
        "periphery": (),
    }.get(band, ())

    for role in preferred:
        for group in groups:
            if group.role == role:
                return group
    for group in groups:
        if _side(group) == "center":
            return group
    return None


def _side(group: FPGroup) -> str:
    return get_role(group.role).side


def _shift_to_canvas(groups: list[FPGroup], rules: Rules) -> None:
    if not groups:
        return
    min_x = min(group.x for group in groups)
    min_y = min(group.y for group in groups)
    dx = 16.0 - min_x
    dy = 34.0 - min_y
    for group in groups:
        group.x += dx
        group.y += dy
        for device in group.devices:
            device.x += dx
            device.y += dy


def _canvas_geometry(
    groups: list[FPGroup],
    rules: Rules,
) -> tuple[float, float, dict[str, Any], float]:
    if not groups:
        return 80.0, 60.0, {}, 40.0

    max_x = max(group.x + group.w for group in groups)
    max_y = max(group.y + group.h for group in groups)
    content_w = max_x - 16.0
    content_h = max_y - 34.0

    reserve_fraction = float(rules.block("reserve_fraction", 0.08))
    reserve_w = max(10.0, content_w * reserve_fraction)
    right_margin = 16.0 + reserve_w + 8.0
    width = 16.0 + content_w + right_margin
    # Small blocks still need room for the title, legend and footer.  Without
    # this floor the text is clipped on the right for a compact design.
    width = max(width, 150.0)
    height = 34.0 + content_h + 30.0

    reserve = {
        "x": width - 16.0 - reserve_w - 4.0,
        "y": 34.0,
        "w": reserve_w,
        "h": content_h,
        "fraction": reserve_fraction,
        "label": "PEX-fix reserve",
    }

    input_groups = [group for group in groups if group.role == "input_pair"]
    if input_groups:
        symmetry_x = input_groups[0].x + input_groups[0].w / 2.0
    else:
        symmetry_x = 16.0 + content_w / 2.0

    return width, height, reserve, symmetry_x


def _center_content(groups: list[FPGroup], reserve: dict[str, Any]) -> None:
    """Center the block between the left margin and the reserve strip.

    Small designs otherwise leave a large empty gap between the block and the
    reserve, which reads as if the reserve were a separate block.
    """

    if not groups:
        return
    content_right = max(group.x + group.w for group in groups)
    reserve_x = float(reserve.get("x", content_right + 8.0))
    spare = reserve_x - 8.0 - content_right
    if spare <= 0:
        return
    dx = spare / 2.0
    for group in groups:
        group.x += dx
        for device in group.devices:
            device.x += dx


def _symmetry_axis(groups: list[FPGroup]) -> float:
    input_group = next((group for group in groups if group.role == "input_pair"), None)
    if input_group:
        return input_group.x + input_group.w / 2.0
    left = min((group.x for group in groups), default=16.0)
    right = max((group.x + group.w for group in groups), default=116.0)
    return (left + right) / 2.0


def _make_ports(
    groups: list[FPGroup],
    width: float,
    height: float,
    symmetry_x: float,
) -> list[Port]:
    ports: list[Port] = []
    content_bottom = max((group.y + group.h for group in groups), default=height - 30.0)
    ports.append(Port("VDD", "vdd", symmetry_x, 27.0, "top"))
    ports.append(Port("VSS", "vss", symmetry_x, content_bottom + 4.0, "bottom"))

    input_group = next((group for group in groups if group.role == "input_pair"), None)
    if input_group:
        active = [device for device in input_group.devices if not device.proposed]
        if len(active) >= 2:
            left_input = min(active, key=lambda device: device.x)
            right_input = max(active, key=lambda device: device.x)
            ports.append(
                Port(
                    "INP",
                    "vinp",
                    left_input.x + left_input.w / 2.0,
                    left_input.y - 1.0,
                    "pin-top",
                )
            )
            ports.append(
                Port(
                    "INN",
                    "vinn",
                    right_input.x + right_input.w / 2.0,
                    right_input.y - 1.0,
                    "pin-top",
                )
            )

    output_group = next((group for group in groups if group.role == "output_stage"), None)
    if output_group:
        ports.append(
            Port(
                "VOUT",
                "vout",
                output_group.x + output_group.w + 0.9,
                output_group.y + output_group.h / 2.0,
                "pin-right",
            )
        )
    else:
        candidates = [
            device
            for group in groups
            for device in group.devices
            if not device.proposed
            and any(node.lower() in ("vout", "out", "outp", "outn") for node in device.nodes)
        ]
        if candidates:
            device = max(candidates, key=lambda item: item.x + item.w)
            ports.append(
                Port(
                    "VOUT",
                    "vout",
                    device.x + device.w + 0.9,
                    device.y + device.h / 2.0,
                    "pin-right",
                )
            )

    for role, label in (("enable_switch", "EN"), ("adj_switch", "ADJ")):
        group = next((group for group in groups if group.role == role), None)
        if group:
            ports.append(
                Port(
                    label,
                    label.lower(),
                    group.x + group.w / 2.0,
                    group.y + group.h + 2.5,
                    "bottom",
                )
            )

    return ports


def _make_channels_and_bands(
    groups: list[FPGroup],
    width: float,
) -> tuple[list[Channel], list[Band]]:
    by_band: dict[str, list[FPGroup]] = defaultdict(list)
    for group in groups:
        by_band[group.band].append(group)

    bands: list[Band] = []
    for name in _BAND_ORDER:
        band_groups = by_band.get(name, [])
        if not band_groups:
            continue
        y0 = min(group.y for group in band_groups)
        y1 = max(group.y + group.h for group in band_groups)
        bands.append(Band(name=name, y0=y0, y1=y1))

    content_right = max((group.x + group.w for group in groups), default=max(16.0, width - 20.0))
    channels: list[Channel] = []
    for upper, lower in zip(bands, bands[1:]):
        y = (upper.y1 + lower.y0) / 2.0
        channels.append(
            Channel(
                orientation="horizontal",
                x1=16.0,
                y1=y,
                x2=content_right,
                y2=y,
                label="routing channel",
            )
        )
    return channels, bands
