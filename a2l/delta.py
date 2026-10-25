"""Layout-induced schematic deltas, planned before PEX.

Late PEX fixes are often "small" changes: add boundary dummies, add decap,
split a finger, add a dummy switch.  They are small electrically but expensive
process-wise because they invalidate a verified schematic/layout pair.

This module turns those predictable changes into an explicit, reviewable
manifest.  The manifest does not mutate the schematic; it is a proposal with an
owner, a reason and an area impact, so the analog and layout engineers can
accept or reject it before the layout is frozen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .area import AreaReport
from .floorplan import Floorplan
from .roles import get_role
from .rules import Rules


@dataclass
class DeltaItem:
    id: str
    kind: str
    target: str
    action: str
    reason: str
    owner: str
    status: str
    area_delta_um2: float
    confidence: str
    rule: str
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "target": self.target,
            "action": self.action,
            "reason": self.reason,
            "owner": self.owner,
            "status": self.status,
            "area_delta_um2": round(self.area_delta_um2, 2),
            "confidence": self.confidence,
            "rule": self.rule,
            "notes": self.notes,
        }


@dataclass
class LayoutDelta:
    design: str
    rules_name: str
    items: list[DeltaItem]
    pex_resim_scope: list[str]
    summary: dict[str, Any]
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "design": self.design,
            "rules": self.rules_name,
            "summary": self.summary,
            "items": [item.to_dict() for item in self.items],
            "pex_resim_scope": self.pex_resim_scope,
            "notes": self.notes,
        }


def plan_layout_delta(
    report: AreaReport,
    floorplan: Floorplan,
    rules: Rules,
) -> LayoutDelta:
    items: list[DeltaItem] = []
    counter = 1

    def add(
        kind: str,
        target: str,
        action: str,
        reason: str,
        owner: str,
        area: float,
        rule: str,
        confidence: str = "rule",
        notes: str = "",
    ) -> None:
        nonlocal counter
        items.append(
            DeltaItem(
                id=f"D{counter:03d}",
                kind=kind,
                target=target,
                action=action,
                reason=reason,
                owner=owner,
                status="proposed",
                area_delta_um2=area,
                confidence=confidence,
                rule=rule,
                notes=notes,
            )
        )
        counter += 1

    for group in report.groups:
        spec = get_role(group.role)
        target = f"{group.key} ({', '.join(device.name for device in group.devices)})"

        if group.match and group.dummy_count > 0:
            add(
                kind="dummy",
                target=target,
                action=f"Add {group.dummy_count} boundary dummy device(s); see the dashed DM blocks in the floorplan",
                reason=f"Preserve edge matching for {group.role}",
                owner="layout",
                area=group.area_dummy_um2,
                rule="matching.dummy_per_group",
                notes="Drawn in the floorplan as proposed; confirm dummy W/L with the analog designer.",
            )

        if group.role == "input_pair":
            ring_area = sum(device.area_ring_um2 for device in group.devices)
            add(
                kind="guard_ring",
                target=target,
                action="Place a guard ring and keep the pair on a common-centroid / interdigitated pattern",
                reason="Substrate noise and Vth matching dominate input-referred offset",
                owner="layout",
                area=ring_area,
                rule="matching.guard_ring_for_critical",
                notes="Do not route noisy digital or clock lines across the pair.",
            )
            add(
                kind="routing_intent",
                target=target,
                action="Keep input gate routing symmetric and shielded; reserve a clean channel to the pair",
                reason="Input parasitics and coupling directly degrade offset and noise",
                owner="both",
                area=0.0,
                rule="layout_delta.guard_ring_for_input_pair",
                confidence="heuristic",
            )

        if group.role == "current_mirror":
            add(
                kind="dummy_logic",
                target=target,
                action="Add a dummy mirror branch / dummy stack next to the mirror",
                reason="Keeps the mirror environment identical at the boundary and reduces systematic ratio error",
                owner="analog",
                area=0.0,
                rule="layout_delta.boundary_dummies_per_critical_group",
                confidence="heuristic",
                notes="May be removable if the mirror is far from the block boundary.",
            )

        if group.role == "cascode":
            add(
                kind="dummy_logic",
                target=target,
                action="Add a dummy cascode device at the top/bottom of the stack",
                reason="Balances source/drain parasitics and etch environment across the stack",
                owner="both",
                area=0.0,
                rule="layout_delta.boundary_dummies_per_critical_group",
                confidence="heuristic",
            )

        if group.role == "tail_current":
            add(
                kind="dummy_logic",
                target=target,
                action="Add a dummy tail device on the unused side of the tail current source",
                reason="Keeps the tail current mirror symmetric and preserves the input-pair common source",
                owner="analog",
                area=0.0,
                rule="layout_delta.boundary_dummies_per_critical_group",
                confidence="heuristic",
            )

        if group.role == "output_stage":
            max_w = float(rules.mos("max_w_per_finger_um", 10.0))
            oversized = [
                device.name
                for device in group.devices
                if device.kind == "mos" and device.nf > 0 and device.total_w_um / max(1, device.nf * device.m) > max_w
            ]
            if oversized:
                add(
                    kind="finger_split",
                    target=", ".join(oversized),
                    action=f"Split the output device into more fingers (W/finger <= {max_w:g} um)",
                    reason="Current density, electromigration and gate resistance",
                    owner="analog",
                    area=group.area_no_dummy_um2 * 0.03,
                    rule="mos.max_w_per_finger_um",
                    confidence="rule",
                )
            else:
                add(
                    kind="routing_intent",
                    target=target,
                    action="Reserve wide metal / multiple vias for the output devices",
                    reason="Output stage carries the largest current and is EM-limited",
                    owner="layout",
                    area=0.0,
                    rule="layout_delta.max_current_density_ma_per_um",
                    confidence="heuristic",
                )

        if group.role in ("enable_switch", "adj_switch"):
            add(
                kind="dummy_logic",
                target=target,
                action="Add a dummy switch (same W/L, gate tied off) next to the switch",
                reason="Balances charge injection and keeps the switch environment symmetric",
                owner="analog",
                area=group.area_no_dummy_um2,
                rule="layout_delta.dummy_logic_for_switches",
                confidence="heuristic",
            )

    decap_groups = [group for group in report.groups if group.role == "decap"]
    if not decap_groups:
        comp_pf = sum(device.c_pf for device in report.devices if device.role == "compensation")
        decap_pf = max(
            float(rules.block("decap_min_pf", 2.0)),
            comp_pf * float(rules.block("decap_ratio_to_comp", 0.5)),
        )
        decap_pf = min(decap_pf, float(rules.block("decap_max_pf", 20.0)))
        density = float(rules.cap("density_ff_per_um2", 1.5))
        area = decap_pf * 1000.0 / max(density, 1e-9) * (1.0 + float(rules.cap("routing_overhead", 0.10)))
        add(
            kind="decap",
            target="vdd/vss",
            action=f"Add a {decap_pf:.2f} pF decap between VDD and VSS near the block",
            reason="Supply transient / PEX-induced ringing; reserve the area now so it does not force a re-layout later",
            owner="both",
            area=area,
            rule="block.decap_min_pf / block.decap_ratio_to_comp",
            confidence="heuristic",
            notes="Value is an initial proposal; confirm with the analog designer.",
        )

    reserve_area = float(report.summary.get("area_reserved_um2", 0.0))
    add(
        kind="reserve",
        target="block",
        action=f"Keep {float(rules.block('reserve_fraction', 0.08)) * 100:.0f}% of the block area as an uncommitted PEX-fix reserve",
        reason="Absorbs predictable late fixes (extra dummies, decap, routing) without moving the block boundary",
        owner="both",
        area=reserve_area,
        rule="block.reserve_fraction",
        confidence="rule",
        notes="The reserve is drawn as the hatched strip to the right of the floorplan.",
    )

    pex_scope = _pex_resim_scope(report)
    summary = _summarize(items, report)

    notes = [
        "This is a proposal, not an automatic schematic edit.",
        "Items marked owner=analog must be reflected in the schematic before tape-out.",
        "Items marked owner=layout must be visible in the floorplan review.",
    ]
    if summary["reserve_shortfall_um2"] > 0:
        notes.append(
            f"Proposed delta area exceeds the PEX-fix reserve by "
            f"{summary['reserve_shortfall_um2']:.0f} um2; increase the reserve or reduce/relocate deltas."
        )

    return LayoutDelta(
        design=report.design,
        rules_name=report.rules_name,
        items=items,
        pex_resim_scope=pex_scope,
        summary=summary,
        notes=notes,
    )


def _pex_resim_scope(report: AreaReport) -> list[str]:
    roles = {device.role for device in report.devices}
    scope: list[str] = []
    if "input_pair" in roles:
        scope.append("DC offset / input-referred noise after input-pair and tail routing parasitics")
    if "current_mirror" in roles:
        scope.append("AC gain / phase margin after current-mirror parasitic extraction")
    if "cascode" in roles:
        scope.append("AC gain / phase margin after cascode-stack parasitic extraction")
    if "compensation" in roles:
        scope.append("Stability (loop gain / phase margin) after Cc and output-node parasitics")
    if "output_stage" in roles:
        scope.append("Large-signal swing / EM and IR-drop check after output routing")
    scope.append("Post-layout DC operating point after dummy, decap and guard-ring insertion")
    return scope


def _summarize(items: list[DeltaItem], report: AreaReport) -> dict[str, Any]:
    by_kind: dict[str, int] = {}
    for item in items:
        by_kind[item.kind] = by_kind.get(item.kind, 0) + 1

    total_area = sum(item.area_delta_um2 for item in items)
    base_area = float(report.summary.get("area_block_um2", report.summary.get("area_block_with_dummy_um2", 0.0)))
    reserve = float(report.summary.get("area_reserved_um2", 0.0))
    shortfall = max(0.0, total_area - reserve)
    return {
        "item_count": len(items),
        "by_kind": by_kind,
        "area_delta_um2": round(total_area, 2),
        "area_delta_mm2": round(total_area / 1e6, 6),
        "area_delta_fraction_of_block": round(total_area / max(base_area, 1e-9), 4),
        "proposed_count": sum(1 for item in items if item.status == "proposed"),
        "reserve_um2": round(reserve, 2),
        "reserve_shortfall_um2": round(shortfall, 2),
        "reserve_sufficient": shortfall <= 1e-9,
    }
