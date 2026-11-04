#!/usr/bin/env python3
"""Build the LDO white-line-input.json from the imported NetlistLabel overlay.

This is a deterministic importer, not an annotation tool. It preserves the
overlay's proposal status and adds only explicit geometry assumptions needed for
white-line planning.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OVERLAY = ROOT / "netlistlabel-overlay" / "ldo.annotated.sp"
OUT = ROOT / "white-line-input.json"

# Layout-only folding/dummy choices for the long xhigh resistors.
# The electrical m stays 1; these are physical segment counts.
# True folded xhigh geometry: 10 um x 0.35 um segments, 0.5 um pitch gap.
# 2 columns for the long resistors; one column for the short degeneration R.
RES_LAYOUT = {
    "XR4": {"rows": 13, "cols": 2, "cell_um": [10.0, 0.85], "active": 18, "dummy": 7,  "block_um": [20.0, 10.55]},
    "XR5": {"rows": 25, "cols": 2, "cell_um": [10.0, 0.85], "active": 36, "dummy": 13, "block_um": [20.0, 20.75]},
    "XR6": {"rows": 9,  "cols": 1, "cell_um": [10.0, 0.85], "active": 4,  "dummy": 5,  "block_um": [10.0, 7.15]},
}

PARAM_RE = re.compile(r"(?:^|\s)([A-Za-z_][A-Za-z0-9_]*)=([^\s]+)")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_params(tokens):
    text = " " + " ".join(tokens) + " "
    return {m.group(1): m.group(2) for m in PARAM_RE.finditer(text)}


def main() -> None:
    devices, passives, blackboxes = [], [], []
    groups = {}
    for lineno, raw in enumerate(OVERLAY.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("*") or line.startswith("."):
            continue
        tokens = line.split()
        name = tokens[0]
        params = parse_params(tokens)
        role = params.get("role", "unknown")
        nll_role = params.get("nll_role", role)
        group = params.get("group", "UNKNOWN")
        match = params.get("match")

        if name.startswith("XM"):
            model = next((t for t in tokens if "fet" in t), "")
            w = float(params.get("W", "0"))
            l = float(params.get("L", "0"))
            nf = int(float(params.get("nf", "1")))
            m = int(float(params.get("m", "1")))
            dev = {
                "name": name,
                "role": role,
                "nll_role": nll_role,
                "group": group,
                "W_um": w,
                "L_um": l,
                "m": m,
                "fingers": nf * m,
                "nf": nf,
                "sd_mode": "shared",
                "ring": True,
                "well": "NW" if "pfet" in model else "PW",
                "matched": bool(match),
                "match": match,
                "review_status": "sampled_reviewed",
                "dnw": "DNW2" if name == "XM61" else "DNW1",
                "source": "netlistlabel-overlay/ldo.annotated.sp",
                "source_line": lineno,
            }
            devices.append(dev)
            groups.setdefault(group, {"members": [], "matched": False})
            groups[group]["members"].append(name)
            groups[group]["matched"] = groups[group]["matched"] or bool(match)

        elif name.startswith("XR"):
            model = next((t for t in tokens if "res_" in t), "")
            length = float(params.get("L", "0"))
            m = int(float(params.get("m", "1")))
            reviewed = name in {"XR4", "XR5"}
            review_status = "user_confirmed" if name == "XR6" else ("sampled_reviewed" if reviewed else "proposed_not_reviewed")
            rl = RES_LAYOUT[name]
            nll = "degeneration" if name == "XR6" else nll_role
            passive = {
                "name": name,
                "type": "resistor",
                "value": None,
                "unit": "unknown",
                # square folded block, not a long strip; active area is 0.35 * length
                "footprint_um": rl["block_um"],
                "m": m,
                "ring": True,
                "ring_gap_um": 0.8,
                "ring_width_um": 1.0,
                "dnw": "DNW1",
                "group": group,
                "nll_role": nll,
                "match": match,
                "review_status": review_status,
                "source": "netlistlabel-overlay/ldo.annotated.sp",
                "source_line": lineno,
                "array": {
                    "style": "square_folded_dummy",
                    "folded": True,
                    "dummy_layout": "boundary",
                    "rows": rl["rows"],
                    "cols": rl["cols"],
                    "cell_um": rl["cell_um"],
                    "active_cells": rl["active"],
                    "dummy_cells": rl["dummy"],
                    "segment_length_um": 10.0,
                    "segment_width_um": 0.35,
                    "segment_gap_um": 0.5,
                    "columns": rl["cols"],
                    "rows_per_column": rl["rows"],
                },
                "notes": f"folded resistor block; core area 0.35x{length:g} um; model={model}; value not in netlist",
            }
            passives.append(passive)
            groups.setdefault(group, {"members": [], "matched": False})
            groups[group]["members"].append(name)
            groups[group]["matched"] = groups[group]["matched"] or bool(match)

        elif name.startswith("XC"):
            model = next((t for t in tokens if "cap_" in t), "")
            w = float(params.get("W", "0"))
            l = float(params.get("L", "0"))
            m = int(float(params.get("m", "1")))
            reviewed = name in {"XC1", "XC3"}
            passive = {
                "name": name,
                "type": "MIM",
                "value": None,
                "unit": "unknown",
                "footprint_um": [w, l],
                "m": m,
                "ring": True,
                "ring_gap_um": 0.8,
                "ring_width_um": 1.0,
                "dnw": "DNW1",
                "group": group,
                "nll_role": nll_role,
                "match": match,
                "review_status": "user_confirmed" if name == "XC3" else ("sampled_reviewed" if reviewed else "proposed_not_reviewed"),
                "function": "vref_input_filter" if name == "XC3" else "decap",
                "source": "netlistlabel-overlay/ldo.annotated.sp",
                "source_line": lineno,
                "array": {"style": "plain", "rows": m, "cols": 1, "dummy_cells": 0} if m > 1 else {"style": "plain", "rows": 1, "cols": 1, "dummy_cells": 0},
                "notes": f"model={model}; value not in netlist",
            }
            passives.append(passive)
            groups.setdefault(group, {"members": [], "matched": False})
            groups[group]["members"].append(name)
            groups[group]["matched"] = groups[group]["matched"] or bool(match)

        elif name.lower() in {"x1", "x2"}:
            model = next((t for t in tokens[1:] if t.startswith("sky130_")), "")
            ports = tokens[1 : tokens.index(model)] if model in tokens else tokens[1:]
            bb = {
                "name": name,
                "type": "level_shifter",
                "group": "CTRL_EN" if name == "x1" else "CTRL_SEL",
                "ports": ports,
                "footprint_um2": 25.0,
                "ring_included": True,
                "dnw": "DNW1",
                "status": "estimated",
                "review_status": "user_confirmed_placeholder",
                "notes": f"model={model}; 5x5 cell+ring placeholder from user, not LEF/GDS",
            }
            blackboxes.append(bb)
            groups.setdefault(bb["group"], {"members": [], "matched": False})
            groups[bb["group"]]["members"].append(name)

    group_objs = []
    for name in sorted(groups):
        group_objs.append({
            "name": name,
            "members": sorted(groups[name]["members"]),
            "matched": bool(groups[name]["matched"]),
            "ring": True,
            "well": "NONE",
            "preferred_rows": [2, 4, 6],
            "notes": "membership from NetlistLabel overlay; mixed NW/PW group marked NONE",
        })

    # Owner-confirmed bank map (2026-11-04).
    # active L is unchanged; dummy L=0.5 for all dummy-bearing banks.
    banks = {
        "PMOS_1X0.5_BANK": ["XM57", "XM58", "XM59", "XM63", "XM65", "XM86", "XM88", "XM90"],
        "PMOS_2.5X0.5_BANK": ["XM76", "XM84"],
        "PMOS_1X2_BANK": ["XM71", "XM72", "XM73"],
        "PMOS_1X7_BANK": ["XM46", "XM56", "XM62", "XM64", "XM60", "XM79"],
        "PMOS_1X10_BANK": ["XM68"],
        "NMOS_1X0.5_BANK": ["XM70", "XM75", "XM77", "XM78", "XM83", "XM85", "XM87", "XM89"],
        "NMOS_2X0.5_BANK": ["XM52", "XM53"],
        "NMOS_5X0.5_BANK": ["XM61"],
        "NMOS_1X7_BANK": ["XM48", "XM55"],
        "NMOS_1X9_BANK": ["XM66", "XM67", "XM69", "XM74"],
        "NMOS_3X9_BANK": ["XM54"],
        "NMOS_1X10_BANK": ["XM80", "XM81", "XM82"],
    }
    no_dummy = {"PMOS_1X0.5_BANK", "PMOS_2.5X0.5_BANK", "NMOS_1X0.5_BANK", "NMOS_5X0.5_BANK"}
    edge_switches = {"XM86", "XM88"}
    bank_of = {name: b for b, names in banks.items() for name in names}
    for d in devices:
        bank = bank_of.get(d["name"])
        if not bank:
            continue
        d["match"] = bank
        d["matched"] = True
        d["bank"] = bank
        d["array_role"] = "edge_switch" if d["name"] in edge_switches else "bank_active"
        d["dummy_sides"] = 0 if bank in no_dummy else 2
        d["dummy_l_um"] = None if bank in no_dummy else 0.5
        d["sd_connectivity"] = "separate_drains_shared_source_if_same"
        if d["name"] in edge_switches:
            d["sd_isolation"] = "separate_sd"

    data = {
        "schema_version": "1.0",
        "module": "sky130_ldo_01v8",
        "units": "um",
        "source": {
            "netlist": "examples/sky130_ldo_01v8/ldo.sp",
            "schematic": "docs/targets/sky130-ldo/schematic.png",
            "license": "Apache-2.0",
            "notes": "Overlay from AnalogNetlistLabel v0.2.0; roles remain a proposal with sampled review.",
        },
        "semantic_source": {
            "overlay": "examples/sky130_ldo_01v8/netlistlabel-overlay/ldo.annotated.sp",
            "sha256": sha256(OVERLAY),
            "status": "PROPOSAL, NOT APPROVED",
            "review": "sampled human review: 44 device + 6 net + 8 port; not global accuracy",
            "netlistlabel_commit": "8cefac8",
        },
        "devices": devices,
        "groups": group_objs,
        "passives": passives,
        "blackboxes": blackboxes,
        "rules": {
            "source": "SKY130 open PDK / sky130.lydrc",
            "source_version": "downloaded 2026-10-26",
            "gate_pitch_extra_um": 0.36,
            "ring_gap_um": 0.8,
            "ring_width_um": 0.5,
            "ring_gap_um": 0.8,
            "passive_ring_width_um": 1.0,
            "passive_ring_gap_um": 0.8,
            "pass_ring_width_um": 2.0,
            "pass_ring_gap_um": 2.0,
            "group_gap_um": 2.0,
            "dnw_gap_um": 8.0,
            "dnw_margin_um": 2.0,
            "nwell_spacing_um": 1.27,
            "nwell_pdiff_enclosure_um": 0.18,
            "ndiff_nwell_spacing_um": 0.34,
            "dnwell_spacing_um": 6.3,
        },
        "constraints": {
            "objective": "min_area",
            "aspect_max": None,
            "input_center_tolerance_um": None,
            "output_outer": True,
            "output_outer_priority": "soft",
            "output_outer_rationale": "LDO VOUT/pass current placement is a floorplan preference; not a hard legality constraint",
            "passives_inside_dnw": True,
            "local_empty": {"max_w_um": 5, "max_h_um": 5, "max_area_fraction": 0.02},
            "dummy_policy": "same_geometry",
            "fake_fill": False,
            "area_denominator": "dnw_bbox",
            "effective_area": "ring_inner_plus_ring_aa_plus_passives",
        },
        "priorities": {
            "hard": [
                "passives_inside_dnw",
                "ring_aa_counted",
                "dummy_same_geometry",
                "no_fake_fill",
                "dnw_gap",
                "local_empty",
                "no_drc_lvs_claim",
            ],
            "objective": ["min_module_bbox_area"],
            "soft": ["input_center", "aspect", "output_outer", "parasitic", "power_return"],
            "calibration": "pending_multi_structure",
        },
        "unknowns": [
            "exact DNW/well boundary polygons inside DNW1/DNW2",
            "passive values and exact physical footprints beyond the specified placeholder blocks",
            "x1/x2 actual LEF/GDS; 5x5 is a user-confirmed placeholder",
            "VOUT/pass-device physical output placement",
        ],
        "assumptions": [
            "W/L/nf/m come from the NetlistLabel overlay; R/C values are not in the netlist.",
            "S/D: separate drains; only identical source nets may share a source rail. All bank membership is owner-confirmed; PMOS 1/0.5 edge switches XM86/XM88 keep separate S/D.",
            "Passive ring gap/width use 0.8/1.0 um; all passives are in DNW1. MOS bank rings use 0.5/0.8; XM61 body rings use 2.0/2.0.",
            "XC3 is a VREF input filter (role decap); XR6 is source degeneration of XM66 (role bias).",
            "Resistor segments are folded into 2x2 um square cells; the block is square, not a 0.35 um-wide strip.",
            "output_outer is a soft preference tied to LDO current/pass-device floorplan, not a hard constraint.",
            "x1/x2 are level shifters inside DNW1; 5x5 is a cell+ring placeholder.",
            "DNW2 contains only XM61 and its guard ring; DNW1/DNW2 gap is 8 um outer-to-outer.",
            "White-line is layout intent, not DRC/LVS/PEX signoff.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT}: {len(devices)} MOS, {len(passives)} passives, {len(blackboxes)} blackboxes, {len(group_objs)} groups")


if __name__ == "__main__":
    main()
