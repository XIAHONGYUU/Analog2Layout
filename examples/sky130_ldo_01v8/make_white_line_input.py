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
                "sd_mode": "unknown",
                "ring": True,
                "well": "NW" if "pfet" in model else "PW",
                "matched": bool(match),
                "match": match,
                "review_status": "sampled_reviewed",
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
            passive = {
                "name": name,
                "type": "resistor",
                "value": None,
                "unit": "unknown",
                "footprint_um": [0.35, length],
                "m": m,
                "ring": True,
                "ring_gap_um": 0.8,
                "ring_width_um": 1.0,
                "dnw": "DNW1",
                "group": group,
                "nll_role": nll_role,
                "match": match,
                "review_status": "sampled_reviewed" if reviewed else "proposed_not_reviewed",
                "source": "netlistlabel-overlay/ldo.annotated.sp",
                "source_line": lineno,
                "notes": f"approx. width=0.35 um; model={model}; value not in netlist",
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
            reviewed = name == "XC1"
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
                "review_status": "sampled_reviewed" if reviewed else "proposed_not_reviewed",
                "source": "netlistlabel-overlay/ldo.annotated.sp",
                "source_line": lineno,
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
                "footprint_um2": None,
                "status": "unknown",
                "review_status": "proposed_not_reviewed",
                "notes": f"model={model}; footprint must be supplied before area signoff",
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
            "ring_width_um": 1.0,
            "group_gap_um": 2.0,
            "dnw_gap_um": 8.0,
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
            "sd_mode for all MOS",
            "DNW/well boundaries and which groups share a DNW",
            "passive values and exact footprints",
            "x1/x2 level-shifter footprints",
            "VOUT/pass-device physical output placement",
            "whether output_outer is a hard constraint for this LDO",
        ],
        "assumptions": [
            "W/L/nf/m come from the NetlistLabel overlay; R/C values are not in the netlist.",
            "Passive ring gap/width use 0.8/1.0 um; all passives are tentatively in DNW1.",
            "Group membership is proposal-grade; XC3/XR6 remain unreviewed.",
            "White-line is layout intent, not DRC/LVS/PEX signoff.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT}: {len(devices)} MOS, {len(passives)} passives, {len(blackboxes)} blackboxes, {len(group_objs)} groups")


if __name__ == "__main__":
    main()
