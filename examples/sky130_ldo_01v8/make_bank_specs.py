#!/usr/bin/env python3
"""Freeze bank geometry (no global placement) from the current LDO artifacts.

This is a bank-first planning artifact. It deliberately omits x/y placement and
port-side assignments; those belong to the later assembly/routing stages.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "examples/sky130_ldo_01v8/white-line-input.json"
MANIFEST = ROOT / "examples/sky130_ldo_01v8/white-line-manifest.json"
OUT_JSON = ROOT / "examples/sky130_ldo_01v8/bank-specs.json"
OUT_MD = ROOT / "examples/sky130_ldo_01v8/bank-plan.md"

D = json.loads(INPUT.read_text())
M = json.loads(MANIFEST.read_text())
devices = {d["name"]: d for d in D["devices"]}
blocks = {b["group"]: b for b in M["blocks"] if b.get("kind") == "well"}


def bank_record(cluster):
    group = cluster["group"]
    block = blocks.get(group)
    if block is None:
        raise KeyError(group)
    members = [devices[n] for n in cluster["members"]]
    return {
        "kind": "mos_bank",
        "type": "PMOS" if members[0]["well"] == "NW" else "NMOS",
        "members": cluster["members"],
        "active_l_um": cluster["active_l_um"],
        "m_values": cluster["m_values"],
        "nf_total": cluster["nf_total"],
        "array": {"rows": cluster["rows"], "cols": cluster["cols"],
                  "fingers": cluster["fingers"]},
        "dummy": {"sides": cluster.get("dummy_sides", 0),
                  "L_um": cluster.get("dummy_l_um"),
                  "W_um": cluster.get("dummy_w"),
                  "extra_cells": cluster.get("empty_cells", 0)},
        "poly_orientation": "vertical",
        "ring": {"type": "body_tap_intent", "width_um": 0.5, "gap_um": 0.8},
        "core_um": [cluster["w"], cluster["h"]],
        "outer_um": [block["w"], block["h"]],
        "ports": {"status": "pending", "sides": None, "nets": None},
        "status": "draft_frozen_geometry",
    }

banks = {}
for c in M["device_clusters"]:
    banks[c["group"]] = bank_record(c)

# XM61 output bank: six shared-ring sub-banks; DNW2-specific macro.
p = M["pass"]
banks["PASS_XM61"] = {
    "kind": "output_bank", "type": "NMOS", "members": ["XM61"],
    "active_l_um": p["array"]["fw"] - 0.36,
    "m_values": [1000], "nf_total": 1,
    "array": {"rows": p["array"]["rows"], "cols": p["array"]["cols"],
              "fingers": p["array"]["n"]},
    "sub_banks": {"count": len(p["subs"]), "fingers_each": p["subs"][0]["fingers"],
                  "arrangement": p["arrangement"], "finger_w_um": p["finger_w_um"]},
    "dummy": {"sides": 0, "L_um": None, "W_um": 0.0, "extra_cells": 0},
    "poly_orientation": "vertical",
    "ring": {"type": "body_tap_intent", "width_um": 2.0, "gap_um": 2.0,
             "shared_walls": True, "outer_dnw_guard": True},
    "dnw": {"width_um": p["dnw_w"], "height_um": p["dnw_h"]},
    "outer_um": [p["w"], p["h"]],
    "ports": {"status": "pending", "sides": None, "nets": None},
    "status": "draft_frozen_geometry",
}

passives = []
for b in M["passive_blocks"]:
    pdata = next(x for x in D["passives"] if x["name"] == b["name"])
    passives.append({
        "kind": "passive", "name": b["name"], "group": b["group"],
        "array": pdata.get("array"),
        "core_um": b["core"], "outer_um": [b["w"], b["h"]],
        "ring": {"type": "passive_ring_intent", "width_um": 1.0, "gap_um": 0.8},
        "terminals": {},
        "ports": {"status": "pending", "sides": None},
        "status": "draft_frozen_geometry",
    })

blackboxes = []
for b in M["blackboxes"]:
    blackboxes.append({"kind": "blackbox", "name": b["name"], "group": b["group"],
                       "outer_um": [b["w"], b["h"]], "ring_included": True,
                       "ports": {"status": "pending", "sides": None},
                       "status": "placeholder"})

spec = {
    "schema_version": "0.1",
    "module": D["module"],
    "status": "draft bank geometry; no global placement/routing",
    "constraints": {"dnw1_poly_orientation": "vertical",
                    "no_bank_rotation_inside_dnw1": True,
                    "no_connection_geometry": True},
    "banks": banks,
    "passives": passives,
    "blackboxes": blackboxes,
}
OUT_JSON.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

lines = ["# LDO bank plan — bank-first freeze", "",
         "Status: **draft geometry freeze**; no global placement/routing yet.", "",
         "Global rule: DNW1 poly orientation is **vertical**; no individual bank",
         "rotation is allowed. Ports and S/D connections remain pending.", "",
         "## MOS banks", "",
         "| bank | type | members | m | array | L | dummy | core µm | outer µm | status |",
         "| --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- |"]
for name, b in banks.items():
    if b["kind"] != "mos_bank":
        continue
    lines.append(f"| `{name}` | {b['type']} | {', '.join(b['members'])} | {','.join(map(str,b['m_values']))} | {b['array']['rows']}×{b['array']['cols']} | {b['active_l_um']:g} | "
                 f"{b['dummy']['sides']} side(s), L={b['dummy']['L_um']} | {b['core_um'][0]:.2f}×{b['core_um'][1]:.2f} | "
                 f"{b['outer_um'][0]:.2f}×{b['outer_um'][1]:.2f} | {b['status']} |")
b = banks["PASS_XM61"]
lines += ["", "## Output bank", "",
          f"- `PASS_XM61`: {b['sub_banks']['count']} sub-banks × {b['sub_banks']['fingers_each']} fingers; "
          f"W={b['sub_banks']['finger_w_um']:.2f} µm; arrangement {b['sub_banks']['arrangement']}; "
          f"body ring 2.0/2.0 shared; DNW2 {b['dnw']['width_um']:.2f}×{b['dnw']['height_um']:.2f}; no edge dummy.",
          "", "## Passive / blackbox macros", "",
          "| macro | kind | core/outer µm | status |", "| --- | --- | --- | --- |"]
for p in passives:
    lines.append(f"| `{p['name']}` | passive | {p['core_um'][0]:g}×{p['core_um'][1]:g} / {p['outer_um'][0]:.2f}×{p['outer_um'][1]:.2f} | {p['status']} |")
for b in blackboxes:
    lines.append(f"| `{b['name']}` | blackbox | — / {b['outer_um'][0]:.2f}×{b['outer_um'][1]:.2f} | {b['status']} |")
lines += ["", "## Freeze checklist", "",
          "- [x] members / m / nf", "- [x] bank array rows×cols", "- [x] dummy policy and L",
          "- [x] ring dimensions", "- [x] core / outer footprint", "- [x] poly orientation vertical",
          "- [ ] port-side assignment", "- [ ] S/D topology", "- [ ] global placement (later)", "",
          "This file is a geometry contract for the next assembly stage, not a release.",
          "`bank-specs.json` is the machine-readable source."]
OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", OUT_JSON, OUT_MD)
