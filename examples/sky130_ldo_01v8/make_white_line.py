#!/usr/bin/env python3
"""Deterministic LDO device-level white-line compiler.

Reads examples/sky130_ldo_01v8/white-line-input.json and emits a device-level
white-line intent plus a manifest. Not DRC/LVS/PEX.
"""
from html import escape
from math import ceil, sqrt
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
INP = ROOT / "examples/sky130_ldo_01v8/white-line-input.json"
OUT_SVG = ROOT / "examples/sky130_ldo_01v8/white-line.svg"
OUT_MANIFEST = ROOT / "examples/sky130_ldo_01v8/white-line-manifest.json"
D = json.loads(INP.read_text())
RULES = D["rules"]
PITCH = float(RULES["gate_pitch_extra_um"])
RING_GAP = 0.8
RING_W = 0.5
PASSIVE_RING_W = 1.0
PASSIVE_RING_GAP = 0.8
PASS_RING_W = 2.0
PASS_RING_GAP = 2.0
PASS_W_MIN = 5.0
PASS_W_MAX = 25.0
PASS_SUB_COUNT = 6
PASS_FINGERS_PER_SUB = 34
PASS_ARRAY_ROWS = 1
PASS_ARRAY_COLS = 34
PASS_SUB_ROWS = 3
PASS_SUB_COLS = 2
PASS_TOTAL_W = 5000.0
GROUP_GAP = float(RULES["group_gap_um"])
DNW_GAP = float(RULES["dnw_gap_um"])
DNW_MARGIN = 2.0
DEV_GAP = 0.5

COLORS = {
    "AMP": "#0284c7", "BIAS": "#059669", "REF": "#7c3aed", "START": "#d97706",
    "CTRL_EN": "#0891b2", "CTRL_SEL": "#6366f1", "FB": "#b45309",
    "PASSIVE": "#7c3aed", "OUT_DRV": "#be185d", "PASS": "#be185d",
}
WELL_COLORS = {"NW": "#1d4ed8", "PW": "#64748b", "-": "#64748b"}
PASSIVE_TERMINALS = {
    "XR4": {"a": "VM", "b": "VOUT", "body": "AVSS"},
    "XR5": {"a": "AVSS", "b": "VM", "body": "AVSS"},
    "XR6": {"a": "AVSS", "b": "net5", "body": "AVSS"},
    "XC1": {"a": "VERR", "b": "AVSS"},
    "XC3": {"a": "VREF", "b": "AVSS"},
}

def cell(d):
    return d["L_um"] + PITCH, d["W_um"] + 0.60

def device_geom(d, dummy_cols=2):
    fw, fh = cell(d)
    n = int(d["fingers"])
    rows = max(1, round(sqrt(n * fw / fh))) if n > 1 else 1
    rows = min(rows, n)
    cols = ceil(n / rows)
    w = (cols + dummy_cols) * fw
    h = rows * fh
    return {"fw": fw, "fh": fh, "rows": rows, "cols": cols, "n": n,
            "w": w, "h": h, "dummy_cols": dummy_cols}

def interleave_names(names, counts):
    """Weighted round-robin: repeat one cycle of all active devices, with
    extra slots distributed round-robin by m. No sequential tail."""
    rem = list(counts)
    seq = []
    while sum(rem):
        active = [i for i, c in enumerate(rem) if c > 0]
        cycles = max(1, min(rem[i] for i in active))
        shares = {i: rem[i] // cycles for i in active}
        # build this cycle with max-remaining / no-immediate-repeat; the
        # per-cycle quota prevents a sequential tail at the end of the bank.
        crem = dict(shares)
        last = -1
        while sum(crem.values()):
            cands = [i for i in active if crem[i] > 0 and i != last]
            if not cands:
                cands = [i for i in active if crem[i] > 0]
            i = max(cands, key=lambda k: (crem[k], -k))
            seq.append(names[i])
            crem[i] -= 1
            last = i
        for i in active:
            rem[i] -= shares[i]
        # safety: if floor division left one leftover, place it next cycle
        if all(rem[i] == 0 for i in active):
            continue
    return seq

def cluster_geom(members, fw, fh, dummy_sides=0, dummy_l=0.5):
    total = sum(int(d["fingers"]) for d in members)
    dummy_w = (dummy_l + PITCH) if dummy_sides else 0.0
    best = None
    for rows in range(1, total + 1):
        cols = ceil(total / rows)
        empty = rows * cols - total
        active_w = cols * fw
        w = active_w + dummy_sides * dummy_w
        h = rows * fh
        aspect = w / max(h, 1e-6)
        area = w * h
        score = area / max(fw * fh * total, 1e-6) + 0.35 * abs(__import__("math").log(aspect)) + empty * 0.25
        if best is None or score < best[0]:
            best = (score, rows, cols, empty, w, h)
    _, rows, cols, empty, w, h = best
    seq = interleave_names([d["name"] for d in members], [int(d["fingers"]) for d in members])
    return {"fw": fw, "fh": fh, "rows": rows, "cols": cols, "n": total,
            "w": w, "h": h, "dummy_sides": dummy_sides,
            "dummy_cols": (2 if dummy_sides == 2 else 0),
            "dummy_w": dummy_w, "dummy_l_um": (dummy_l if dummy_sides else None),
            "empty_cells": empty, "seq": seq}

def shelf_pack(items, target_w, gap=DEV_GAP):
    """items: name,w,h; return placements, W,H."""
    shelves = []
    for it in sorted(items, key=lambda x: (-x[2], -x[1])):
        placed = False
        for sh in shelves:
            if sh["w"] + gap + it[1] <= target_w + 1e-9:
                sh["items"].append(it); sh["w"] += gap + it[1]; sh["h"] = max(sh["h"], it[2]); placed = True; break
        if not placed:
            shelves.append({"items": [it], "w": it[1], "h": it[2]})
    W = max(sh["w"] for sh in shelves); H = sum(sh["h"] for sh in shelves)
    place = {}; y = 0
    for sh in shelves:
        x = 0
        for it in sh["items"]:
            place[it[0]] = (x, y); x += it[1] + gap
        y += sh["h"]
    return place, W, H

def ring_outer(inner_w, inner_h, width=RING_W, gap=RING_GAP):
    return (inner_w + 2*(gap+width), inner_h + 2*(gap+width))

def make_well_blocks():
    """Cluster same-W/L devices in a group/well; interleave their fingers.

    This is the key fix for huge per-device dummy columns and for matching:
    one array + shared end dummies per cluster, not one 3-column array per device.
    """
    buckets = {}
    for d in D["devices"]:
        if d["name"] == "XM61":
            continue
        # Only declared/match groups share a cluster. An unmatched device
        # must not silently share an array with a same-W/L neighbour.
        match = d.get("match") or ""
        if match:
            # Owner-confirmed banks cross logical groups.
            key = ("BANK", match, d["well"], float(d["W_um"]), float(d["L_um"]), "")
        else:
            key = (d["group"], d["well"], float(d["W_um"]), float(d["L_um"]), "",
                   d["name"])
        buckets.setdefault(key, []).append(d)
    blocks = []
    for (_bank, match, well, w, l, _single), members in buckets.items():
        fw, fh = l + PITCH, w + 0.60
        # One 0.5-um-L dummy finger on each side, except no-dummy banks.
        dummy_sides = int(members[0].get("dummy_sides", 0))
        dummy_l = float(members[0].get("dummy_l_um") or 0.5)
        g = cluster_geom(members, fw, fh, dummy_sides, dummy_l)
        boundary = [m for m in members if m.get("array_role") == "edge_switch"]
        if boundary:
            # The edge switches are real devices, but they occupy the two outer
            # cells; no additional dummy columns are added.
            boundary = sorted(boundary, key=lambda m: m["name"])
            core = [m for m in members if m not in boundary]
            seq = [boundary[0]["name"]] + [m["name"] for m in core] + [boundary[-1]["name"]]
            g["dummy_sides"] = 0
            g["dummy_cols"] = 0
            g["dummy_w"] = 0.0
            g["boundary_devices"] = [m["name"] for m in boundary]
            g["rows"] = 1
            g["cols"] = len(seq)
            g["w"] = len(seq) * fw
            g["h"] = fh
            g["empty_cells"] = 0
            g["seq"] = seq
        name = "/".join(d["name"] for d in members)
        blocks.append({
            "kind": "cluster", "name": name, "group": match or "UNMATCHED", "well": well,
            "w": g["w"], "h": g["h"], "geom": g, "members": members,
            "seq": g["seq"], "dummy_cols": g["dummy_cols"],
        })
    # pack clusters inside each group/well with a ring
    grouped = {}
    for b in blocks:
        grouped.setdefault((b["group"], b["well"]), []).append(b)
    out = []
    for (group, well), items in grouped.items():
        best = None
        for target in range(6, 120, 2):
            place, W, H = shelf_pack([(b["name"], b["w"], b["h"]) for b in items], target, gap=DEV_GAP)
            ow, oh = ring_outer(W, H)
            score = ow * oh
            if best is None or score < best[0]:
                best = (score, target, place, W, H, ow, oh)
        _, target, place, W, H, ow, oh = best
        for b in items:
            b["x"], b["y"] = place[b["name"]]
        out.append({"kind": "well", "name": f"{group}_{well}", "group": group, "well": well,
                    "inner_w": W, "inner_h": H, "w": ow, "h": oh, "target_w": target,
                    "items": items, "place": place})
    return out

def make_passive_blocks():
    out=[]
    for p in D["passives"]:
        cw,ch=p["footprint_um"]; ow,oh=ring_outer(cw,ch,PASSIVE_RING_W,PASSIVE_RING_GAP)
        out.append({"kind":"passive","name":p["name"],"group":p.get("group","PASSIVE"),
                    "w":ow,"h":oh,"core":[cw,ch],"data":p})
    return out

def make_blackbox_blocks():
    out=[]
    for b in D["blackboxes"]:
        s=sqrt(b["footprint_um2"]) if b.get("footprint_um2") else 5.0
        # footprint_um2 includes ring; no extra ring
        out.append({"kind":"blackbox","name":b["name"],"group":b.get("group","CTRL"),
                    "w":s,"h":s,"data":b})
    return out

def _array_shape_n(n, fw, fh):
    best = None
    for rows in range(1, n + 1):
        cols = ceil(n / rows)
        empty = rows * cols - n
        w, h = cols * fw, rows * fh
        aspect = w / max(h, 1e-6)
        score = w * h / max(fw * fh * n, 1e-6) + 0.35 * abs(__import__("math").log(aspect)) + empty * 0.25
        if best is None or score < best[0]:
            best = (score, rows, cols, w, h, empty)
    return best[1:]

def make_pass_block():
    d = next(x for x in D["devices"] if x["name"] == "XM61")
    fw = float(d["L_um"]) + PITCH
    nf = PASS_FINGERS_PER_SUB
    w = PASS_TOTAL_W / (PASS_SUB_COUNT * nf)
    fh = w + 0.60
    aw, ah = PASS_ARRAY_COLS * fw, PASS_ARRAY_ROWS * fh
    br, bc = PASS_SUB_ROWS, PASS_SUB_COLS
    # shared ring wall: outer gap+ring at edges, gap+one ring+gap between
    gw = bc * aw + 2*(PASS_RING_GAP + PASS_RING_W) + (bc - 1)*(2*PASS_RING_GAP + PASS_RING_W)
    gh = br * ah + 2*(PASS_RING_GAP + PASS_RING_W) + (br - 1)*(2*PASS_RING_GAP + PASS_RING_W)
    dnw_w, dnw_h = gw + 2*DNW_MARGIN, gh + 2*DNW_MARGIN
    env_w, env_h = dnw_w + 2*(PASS_RING_W + PASS_RING_GAP), dnw_h + 2*(PASS_RING_W + PASS_RING_GAP)
    subs = []
    core_x0 = PASS_RING_GAP + PASS_RING_W
    core_y0 = PASS_RING_GAP + PASS_RING_W
    for k in range(PASS_SUB_COUNT):
        rr, cc = divmod(k, bc)
        subs.append({"index": k, "x": core_x0 + cc*(aw + 2*PASS_RING_GAP + PASS_RING_W),
                     "y": core_y0 + rr*(ah + 2*PASS_RING_GAP + PASS_RING_W),
                     "w": aw, "h": ah, "core_w": aw, "core_h": ah,
                     "rows": PASS_ARRAY_ROWS, "cols": PASS_ARRAY_COLS, "fingers": nf})
    geom = {"fw": fw, "fh": fh, "rows": PASS_ARRAY_ROWS, "cols": PASS_ARRAY_COLS,
            "n": nf, "w": aw, "h": ah, "dummy_sides": 0, "dummy_w": 0.0,
            "dummy_cols": 0, "empty_cells": 0, "seq": ["XM61"] * nf}
    return {"kind": "pass", "name": "PASS_XM61", "group": "PASS", "well": d["well"],
            "inner_w": gw, "inner_h": gh, "w": env_w, "h": env_h,
            "dnw_w": dnw_w, "dnw_h": dnw_h, "group_w": gw, "group_h": gh,
            "arrangement": [br, bc], "subs": subs, "geom": geom,
            "finger_w_um": w, "fingers_per_sub": nf,
            "total_w_um": w * nf * PASS_SUB_COUNT, "data": d}

def pack_dnw1(blocks, pass_block):
    """Choose DNW1 target width globally with DNW2 right/below placement."""
    best=None
    for target in range(30, 261, 2):
        place, W, H = shelf_pack([(b["name"], b["w"], b["h"]) for b in blocks], target, gap=GROUP_GAP)
        dw, dh = W + 2*DNW_MARGIN, H + 2*DNW_MARGIN
        pw, ph = pass_block["w"], pass_block["h"]
        for mode in ("right", "below"):
            if mode == "right":
                bw, bh = dw + DNW_GAP + pw, max(dh, ph)
                ox, oy = dw + DNW_GAP, (bh - ph) / 2
            else:
                bw, bh = max(dw, pw), dh + DNW_GAP + ph
                ox, oy = (bw - pw) / 2, dh + DNW_GAP
            area = bw * bh
            if best is None or area < best[0]:
                best = (area, target, W, H, dw, dh, bw, bh, ox, oy, mode, dict(place))
    area, target, W, H, dw, dh, bw, bh, ox, oy, mode, place = best
    for b in blocks:
        x, y = place[b["name"]]
        b["x"], b["y"] = x + DNW_MARGIN, y + DNW_MARGIN
    return target, W, H, dw, dh, bw, bh, ox, oy, mode

def main():
    well_blocks=make_well_blocks()
    passive_blocks=make_passive_blocks()
    bb_blocks=make_blackbox_blocks()
    pass_block=make_pass_block()
    blocks=well_blocks+passive_blocks+bb_blocks
    target,W,H,dnw1_w,dnw1_h,bbox_w,bbox_h,dnw2_x,dnw2_y,mode=pack_dnw1(blocks,pass_block)
    guard = PASS_RING_W + PASS_RING_GAP
    # pack_dnw1 reserves the outer envelope; put the DNW2 edge (not the guard
    # envelope) at the required 8 um gap, and let the guard occupy the gap.
    if mode == "right":
        pass_x = dnw2_x - guard
        pass_y = dnw2_y
        bbox_w -= guard
    else:
        pass_x = dnw2_x
        pass_y = dnw2_y - guard
        bbox_h -= guard
    dnw2_w=pass_block["dnw_w"]; dnw2_h=pass_block["dnw_h"]
    dnw2_inner_x=pass_x+guard; dnw2_inner_y=pass_y+guard
    # effective: well ring outer + passive ring outer + blackbox footprint + pass ring outer
    effective=sum(b["w"]*b["h"] for b in well_blocks)
    effective+=sum(b["w"]*b["h"] for b in passive_blocks)
    effective+=sum(b["w"]*b["h"] for b in bb_blocks)
    effective+=pass_block["w"]*pass_block["h"]
    area=bbox_w*bbox_h; util=effective/area
    manifest={
        "format":"ldo-white-line-manifest/0.1","module":D["module"],
        "bank_count": 12, "bank_clusters": len(well_blocks), "pass_bank": "XM61",
        "status":"white-line intent; not DRC/LVS/PEX",
        "model":{"device_cell":"L+0.36 x W+0.60","boundary_dummy_cols":2,
                 "ring_gap":RING_GAP,"ring_width":RING_W,"group_gap":GROUP_GAP,
                 "dnw_margin":DNW_MARGIN,"dnw_gap":DNW_GAP,
                 "ring_model":"MOS bank 0.5/0.8; XM61 body 2.0/2.0; passive 1.0/0.8; heuristics, not PDK values",
                 "passive_ring":"outside core","x1_x2":"5x5 cell+ring, no extra ring"},
        "bbox_um":[bbox_w,bbox_h],"area_um2":area,"effective_um2":effective,
        "utilization":util,"aspect_w_over_h":bbox_w/bbox_h,
        "dnw1":{"x":0,"y":0,"w":dnw1_w,"h":dnw1_h,
                "contains":[b["name"] for b in blocks]},
        "dnw2":{"x":dnw2_inner_x,"y":dnw2_inner_y,"w":dnw2_w,"h":dnw2_h,"mode":mode,
                "contains":["XM61","body_rings"],"outer_guard":True},
        "blocks":[{"name":b["name"],"kind":b["kind"],"group":b.get("group"),
                   "well":b.get("well"),"x":b["x"],"y":b["y"],"w":b["w"],"h":b["h"]}
                  for b in blocks],
        "device_clusters":[
            {"name":cl["name"],"group":b["group"],"well":b["well"],"block":b["name"],
             "members":[m["name"] for m in cl["members"]],
             "active_l_um":float(cl["members"][0]["L_um"]),
             "m_values":sorted({int(m["m"]) for m in cl["members"]}),
             "nf_total":sum(int(m["nf"]) for m in cl["members"]),
             "rows":cl["geom"]["rows"],"cols":cl["geom"]["cols"],
             "fingers":cl["geom"]["n"],"dummy_cols":cl["geom"]["dummy_cols"],
             "dummy_sides":cl["geom"].get("dummy_sides",0),
             "dummy_w":cl["geom"].get("dummy_w",0.0),
             "dummy_l_um":cl["geom"].get("dummy_l_um"),
             "empty_cells":cl["geom"].get("empty_cells",0),
             "fw":cl["geom"]["fw"],"fh":cl["geom"]["fh"],"w":cl["geom"]["w"],"h":cl["geom"]["h"],
             "x":b["x"]+RING_W+RING_GAP+b["place"][cl["name"]][0],
             "y":b["y"]+RING_W+RING_GAP+b["place"][cl["name"]][1],
             "boundary_devices":cl["geom"].get("boundary_devices",[]),
             "sequence":cl["geom"]["seq"]}
            for b in well_blocks for cl in b["items"]
        ],
        "devices":[{"name":m["name"],"cluster":cl["name"],"group":m["group"],
                    "well":m["well"],"active_l_um":float(m["L_um"]),
                    "m":int(m["m"]),"nf":int(m["nf"]),"fingers":m["fingers"],
                    "array_role":m.get("array_role","normal"),
                    "sd_isolation":m.get("sd_isolation")}
                   for b in well_blocks for cl in b["items"] for m in cl["members"]]
                  + [{"name":"XM61","cluster":"XM61","group":"PASS","well":"PW",
                      "active_l_um":0.5,"m":1000,"nf":1,"fingers":1000}],
        "passive_blocks":[
            {"name":b["name"],"group":b["group"],"x":b["x"],"y":b["y"],
             "w":b["w"],"h":b["h"],"core":b["core"],"ring":True,
             "terminals":PASSIVE_TERMINALS.get(b["name"],{})}
            for b in passive_blocks
        ],
        "blackboxes":[
            {"name":b["name"],"group":b["group"],"x":b["x"],"y":b["y"],
             "w":b["w"],"h":b["h"],"ring_included":True}
            for b in bb_blocks
        ],
        "checks_geometry":{
            "block_overlap": any(
                not (a["x"]+a["w"] <= b["x"]+1e-6 or b["x"]+b["w"] <= a["x"]+1e-6 or
                     a["y"]+a["h"] <= b["y"]+1e-6 or b["y"]+b["h"] <= a["y"]+1e-6)
                for i, a in enumerate(blocks) for b in blocks[i+1:]
            ),
            "dnw1_contains_blocks": all(0 <= b["x"] and 0 <= b["y"] and
                                        b["x"]+b["w"] <= dnw1_w and b["y"]+b["h"] <= dnw1_h
                                        for b in blocks),
            "dnw2_contains_pass": (dnw2_w >= pass_block["group_w"] and dnw2_h >= pass_block["group_h"]),
        },
        "pass":{"x":pass_x,"y":pass_y,"w":pass_block["w"],"h":pass_block["h"],
                "finger_w_um":pass_block["finger_w_um"],
                "fingers_per_sub":pass_block["fingers_per_sub"],
                "total_w_um":pass_block["total_w_um"],
                "dnw_w":pass_block["dnw_w"],"dnw_h":pass_block["dnw_h"],
                "arrangement":pass_block["arrangement"],
                "subs":pass_block["subs"],"array":pass_block["geom"]},
        "checks":{"all_devices_placed": sum(len(cl["members"]) for b in well_blocks for cl in b["items"]) + 1 == 41,
                  "dnw2_only_xm61": pass_block["data"]["name"] == "XM61",
                  "dnw_gap_outer": (dnw2_inner_x - dnw1_w) if mode == "right" else (dnw2_inner_y - dnw1_h),
                  "dnw_gap_reference": "DNW2 polygon edge, not the outer guard envelope",
                  "dnw2_inner_gap": (dnw2_inner_x - dnw1_w) if mode == "right" else (dnw2_inner_y - dnw1_h),
                  "dnw2_outer_guard_gap": (pass_x - dnw1_w) if mode == "right" else (pass_y - dnw1_h),
                  "passives_inside_dnw1": all(0 <= b["x"] and 0 <= b["y"] and b["x"]+b["w"] <= dnw1_w and b["y"]+b["h"] <= dnw1_h for b in passive_blocks),
                  "x1_x2_inside_dnw1": all(0 <= b["x"] and 0 <= b["y"] and b["x"]+b["w"] <= dnw1_w and b["y"]+b["h"] <= dnw1_h for b in bb_blocks),
                  "fake_fill":False,"drc_lvs":False},
        "ring_audit":{"mos_width_um":RING_W,"mos_gap_um":RING_GAP,
                      "passive_width_um":PASSIVE_RING_W,"passive_gap_um":PASSIVE_RING_GAP,
                      "pass_width_um":PASS_RING_W,"pass_gap_um":PASS_RING_GAP,
                      "dnw_margin_um":DNW_MARGIN,
                      "pdk_defined":False,"pdk_facts":"pdk/sky130/facts.json",
                      "source":"layout heuristic; not a SKY130 PDK value",
                      "note":"MOS bank ring 0.5/0.8; XM61 body ring 2.0/2.0; passive 1.0/0.8; DNW margin 2.0"},
        "assumptions":["DNW margin 2.0 um is an explicit heuristic, not a PDK rule.",
                       "MOS bank ring 0.5/0.8, XM61 body ring 2.0/2.0, passive 1.0/0.8 are layout heuristics; none is a PDK rule.",
                       "per-well subarray rings; no second AA ring around passives.",
                       "segment/ring/dummy geometry is white-line intent."],
    }
    OUT_MANIFEST.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

    # ---------------- SVG ----------------
    S=max(3.0,min(10.0, 1100/max(bbox_w,bbox_h)))
    OX,OY=55,125; legend_w=470
    Wpx=int(OX+bbox_w*S+legend_w); Hpx=int(OY+bbox_h*S+180)
    out=[]
    def add(s): out.append(s)
    def X(x): return OX+x*S
    def Y(y): return OY+y*S
    def rect(x,y,w,h,fill="none",stroke="#0f172a",sw=.7,rx=0,dash=None,opacity=1):
        d=f' stroke-dasharray="{dash}"' if dash else ""
        add(f'<rect x="{X(x):.1f}" y="{Y(y):.1f}" width="{w*S:.1f}" height="{h*S:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}"{d}/>')
    def line(x1,y1,x2,y2,stroke="#0f172a",sw=.6,dash=None):
        d=f' stroke-dasharray="{dash}"' if dash else ""
        add(f'<line x1="{X(x1):.1f}" y1="{Y(y1):.1f}" x2="{X(x2):.1f}" y2="{Y(y2):.1f}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round"{d}/>')
    def txt(x,y,s,size=10,fill="#0f172a",weight=400,anchor="start",mono=False):
        fam="'DejaVu Sans Mono',monospace" if mono else "'DejaVu Sans',sans-serif"
        add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escape(str(s))}</text>')
    def tu(x,y,s,size=6,fill="#0f172a",weight=400,anchor="start"):
        txt(X(x),Y(y),s,size,fill,weight,anchor,True)

    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wpx}" height="{Hpx}" viewBox="0 0 {Wpx} {Hpx}">')
    rect(-1000,-1000,6000,6000,fill="#f8fafc",stroke="none")
    txt(34,36,"SKY130 1.8 V LDO — ILLUSTRATIVE white-line intent",26,"#0f172a",700)
    txt(34,58,"41 MOS + 5 passives + x1/x2 · per-bank rings · one dummy strip per side · DNW1/DNW2 8 µm",9,"#475569",mono=True)
    txt(34,76,"NOT a GDS/DRC/LVS layout: no S/D metal, no contacts, no dummy connections, no implant layers",9,"#b91c1c",mono=True)
    txt(34,94,"MOS bank ring: 0.5 / gap 0.8 · XM61 body ring: 2.0 / 2.0 · passive: 1.0 / 0.8 · DNW margin 2.0 (heuristic)",8.5,"#0f766e",mono=True)
    # DNWs
    rect(0,0,dnw1_w,dnw1_h,fill="none",stroke="#0f766e",sw=1.2,rx=1,dash="6 3")
    rect(dnw2_x,dnw2_y,dnw2_w,dnw2_h,fill="none",stroke="#0f766e",sw=1.2,rx=1,dash="6 3")
    tu(1,dnw1_h-2,"DNW1",7,"#0f766e",700); tu(dnw2_x+1,dnw2_y+7,"DNW2 · XM61",7,"#0f766e",700)
    line(dnw1_w+2,dnw2_y+dnw2_h/2,dnw2_x-2,dnw2_y+dnw2_h/2,stroke="#0f766e",sw=.8)
    tu((dnw1_w+dnw2_x)/2,dnw2_y+dnw2_h/2-1,"8 µm",6,"#0f766e",700,"middle")

    def draw_dummy_cell(x,y,fw,fh,dark=False):
        rect(x,y,fw,fh,fill="#ffffff",stroke="#64748b",sw=.25,opacity=.5)
        rect(x+.15,y+.15,max(.1,fw-.3),max(.1,fh-.3),fill="#cbd5e1",stroke="none",opacity=.5)

    def draw_device_array(x,y,g,members,color):
        rect(x,y,g["w"],g["h"],fill="#ffffff",stroke=color,sw=.5)
        palette=["#0284c7","#38bdf8","#7c3aed","#a78bfa","#059669","#34d399","#d97706","#fbbf24","#be185d","#f472b6"]
        cmap={m["name"]:palette[i%len(palette)] for i,m in enumerate(members)}
        seq=g.get("seq",[members[0]["name"]]*g["n"])
        dw=g.get("dummy_w",0.0)
        sides=int(g.get("dummy_sides",0))
        active_x=x+(dw if sides else 0.0)
        if sides:
            # one dummy device/strip per side, spanning the full array height
            draw_dummy_cell(x,y,dw,g["h"])
            if sides == 2:
                draw_dummy_cell(active_x+g["cols"]*g["fw"],y,dw,g["h"])
        for r in range(g["rows"]):
            yy=y+r*g["fh"]
            for c in range(g["cols"]):
                xx=active_x+c*g["fw"]
                idx=r*g["cols"]+c
                if idx < g["n"]:
                    n=seq[idx]
                    edge = n in g.get("boundary_devices", [])
                    rect(xx,yy,g["fw"],g["fh"],fill=("#fca5a5" if edge else cmap[n]),stroke=("#b91c1c" if edge else cmap[n]),sw=(.7 if edge else .15),opacity=(.45 if edge else .35))
                    if edge:
                        add(f'<line x1="{xx*S+OX:.1f}" y1="{yy*S+OY:.1f}" x2="{(xx+g["fw"])*S+OX:.1f}" y2="{(yy+g["fh"])*S+OY:.1f}" stroke="#7f1d1d" stroke-width="0.3"/>')
                else:
                    draw_dummy_cell(xx,yy,g["fw"],g["fh"])
        label="/".join(m["name"] for m in members[:3]) + ("/…" if len(members)>3 else "")
        tu(x+1,y-0.5,label,5,color,700)

    # well blocks
    for b in well_blocks:
        x,y,w,h=b["x"],b["y"],b["w"],b["h"]
        col=COLORS.get(b["group"],"#475569")
        rect(x,y,w,h,fill="#d1fae5",stroke=col,sw=.8)
        rect(x+RING_W,y+RING_W,w-2*RING_W,h-2*RING_W,fill="#f8fafc",stroke=col,sw=.5)
        ix=x+RING_W+RING_GAP; iy=y+RING_W+RING_GAP
        for cl in b["items"]:
            dx,dy=b["place"][cl["name"]]
            draw_device_array(ix+dx,iy+dy,cl["geom"],cl["members"],col)
        short = b["group"].replace("PMOS_", "P").replace("NMOS_", "N").replace("_BANK", "")
        tu(x,y-0.7,f"{short}·{b['well']}",4.5,col,700)
    # passives
    for b in passive_blocks:
        x,y,w,h=b["x"],b["y"],b["w"],b["h"]
        p=b["data"]; col="#7c3aed" if p["type"]=="MIM" else "#b45309"
        rect(x,y,w,h,fill="#d1fae5",stroke=col,sw=.8)
        rect(x+PASSIVE_RING_W,y+PASSIVE_RING_W,w-2*PASSIVE_RING_W,h-2*PASSIVE_RING_W,fill="#f8fafc",stroke="#64748b",sw=.4)
        cw,ch=b["core"]; cx=x+PASSIVE_RING_W+PASSIVE_RING_GAP; cy=y+PASSIVE_RING_W+PASSIVE_RING_GAP
        term=PASSIVE_TERMINALS.get(p["name"],{})
        if p["name"].startswith("XR"):
            arr=p.get("array",{}); rows=arr.get("rows",1); cols=arr.get("cols",1)
            active=arr.get("active_cells",rows*cols); dummy=arr.get("dummy_cells",0)
            cw,ch=b["core"]
            # folded xhigh resistor intent: one serpentine body, not a grid of
            # independent square tiles.
            cells=[]
            for r in range(rows):
                cs=list(range(cols)) if r%2==0 else list(reversed(range(cols)))
                for c in cs: cells.append((r,c))
            for idx,(r,c) in enumerate(cells):
                xx=cx+c*cw/cols; yy=cy+r*ch/rows
                if idx < active:
                    rect(xx,yy,cw/cols,ch/rows,fill="#fef3c7",stroke="#fcd34d",sw=.15,opacity=.55)
                else:
                    rect(xx,yy,cw/cols,ch/rows,fill="#e2e8f0",stroke="#94a3b8",sw=.15,opacity=.55)
            pts=[]
            for idx,(r,c) in enumerate(cells):
                px=cx+(c+0.5)*cw/cols; py=cy+(r+0.5)*ch/rows
                pts.append((px,py))
            for i in range(len(pts)-1):
                x1,y1=pts[i]; x2,y2=pts[i+1]
                line(x1,y1,x2,y2,stroke=("#b45309" if i<active-1 else "#94a3b8"),sw=.9,dash=(None if i<active-1 else "2 1"))
            for i,label in ((0,term.get("a","A")),(len(pts)-1,term.get("b","B"))):
                px,py=pts[i]; rect(px-.45,py-.35,.9,.7,fill="#fff7ed",stroke="#b45309",sw=.5)
                tu(px-0.5,py-.7,label,4.5,"#92400e",700)
            tu(cx,cy-0.8,f"{active} seg + {dummy} DM",4.3,"#92400e",700)
        else:
            arr=p.get("array",{}); rows=arr.get("rows",1); cols=arr.get("cols",1)
            cw,ch=b["core"]
            for r in range(rows):
                for c in range(cols):
                    xx=cx+c*cw/cols; yy=cy+r*ch/rows
                    rect(xx,yy,cw/cols,ch/rows,fill="#ede9fe" if p["type"]=="MIM" else "#fef3c7",stroke=col,sw=.45)
            # MIM has m units; draw the unit count, not one merged block
            tu(cx,cy-0.8,f"{p.get('m',1)} unit",4.3,col,700)
        tlabel=f"{p['name']} {term.get('a','')}–{term.get('b','')}" if term else p["name"]
        tu(x,y-1,tlabel,5.5,col,700)
    # blackboxes
    for b in bb_blocks:
        x,y,w,h=b["x"],b["y"],b["w"],b["h"]
        rect(x,y,w,h,fill="#e0f2fe",stroke="#0284c7",sw=.8)
        tu(x+1,y+h/2,b["name"]+" LS",6,"#075985",700)
    # pass: 5 body-ringed sub-banks with shared ring walls + outer DNW guard
    p=pass_block; px=pass_x; py=pass_y
    # outer envelope / DNW guard ring
    rect(px,py,p["w"],p["h"],fill="#fce7f3",stroke="#be185d",sw=.7)
    rect(px+PASS_RING_W,py+PASS_RING_W,p["w"]-2*PASS_RING_W,p["h"]-2*PASS_RING_W,fill="#f8fafc",stroke="#be185d",sw=.5)
    # DNW2 inner polygon
    rect(px+(PASS_RING_W+PASS_RING_GAP),py+(PASS_RING_W+PASS_RING_GAP),p["dnw_w"],p["dnw_h"],fill="none",stroke="#0f766e",sw=.8,dash="4 2")
    # group body ring origin
    gx=px+(PASS_RING_W+PASS_RING_GAP)+DNW_MARGIN
    gy=py+(PASS_RING_W+PASS_RING_GAP)+DNW_MARGIN
    rect(gx-PASS_RING_GAP-PASS_RING_W,gy-PASS_RING_GAP-PASS_RING_W,p["group_w"],p["group_h"],fill="#d1fae5",stroke="#be185d",sw=.65)
    rect(gx,gy,p["group_w"]-2*(PASS_RING_GAP+PASS_RING_W),p["group_h"]-2*(PASS_RING_GAP+PASS_RING_W),fill="#f8fafc",stroke="#be185d",sw=.35)
    # shared ring walls between sub-banks (not two tangent rings)
    br,bc=p["arrangement"]; aw=p["subs"][0]["w"]; ah=p["subs"][0]["h"]
    for c in range(1,bc):
        wall_x=gx-PASS_RING_GAP-PASS_RING_W + c*(aw+2*PASS_RING_GAP+PASS_RING_W)-PASS_RING_W-PASS_RING_GAP
        rect(wall_x,gy-PASS_RING_GAP-PASS_RING_W,PASS_RING_W,p["group_h"]-2*(PASS_RING_GAP+PASS_RING_W)+2*PASS_RING_GAP,fill="#d1fae5",stroke="#be185d",sw=.3)
    for r in range(1,br):
        wall_y=gy-PASS_RING_GAP-PASS_RING_W + r*(ah+2*PASS_RING_GAP+PASS_RING_W)-PASS_RING_W-PASS_RING_GAP
        rect(gx-PASS_RING_GAP-PASS_RING_W,wall_y,p["group_w"]-2*(PASS_RING_GAP+PASS_RING_W)+2*PASS_RING_GAP,PASS_RING_W,fill="#d1fae5",stroke="#be185d",sw=.3)
    for sb in p["subs"]:
        sx=gx+sb["x"]; sy=gy+sb["y"]
        draw_device_array(sx,sy,p["geom"], [p["data"]], "#be185d")
        tu(sx,sy-1,f"{sb['fingers']} fingers #{sb['index']+1}",4.5,"#9d174d",700)
    tu(px,py-1,f"PASS · XM61 · W={p['finger_w_um']:.2f} µm/finger · {p['fingers_per_sub']}/sub",6,"#9d174d",700)

    # legend/metrics
    lx=OX+bbox_w*S+30; ly=OY
    txt(lx,ly,"LEGEND",8,"#475569",700,mono=True)
    items=[("bank ring (per bank)","#d1fae5"),("edge switch XM86/88","#fca5a5"),
           ("body ring / shared wall","#d1fae5"),("dummy L=0.5","#cbd5e1"),
           ("passive ring","#d1fae5"),("DNW2 outer guard","#fce7f3"),
           ("DNW boundary","#0f766e")]
    for i,(s,c) in enumerate(items):
        add(f'<rect x="{lx}" y="{ly+10+i*14}" width="10" height="10" fill="{c}" stroke="#64748b" stroke-width="0.4"/>')
        txt(lx+22,ly+20+i*14,s,7,"#334155")
    txt(lx,ly+105,"METRICS",8,"#475569",700,mono=True)
    for i,s in enumerate([f"bbox {bbox_w:.1f} × {bbox_h:.1f} µm",f"area {area:.0f} µm²",f"effective {effective:.0f} µm²",f"utilization {util*100:.1f}%",f"aspect {bbox_w/bbox_h:.2f}",f"DNW2 mode {mode}",f"41 MOS + 5 passives + 2 LS"]):
        txt(lx,ly+123+i*14,s,7,"#334155",mono=True)
    txt(34,Hpx-30,"Gray stripe = dummy L=0.5; gray cell inside an array = empty slot. No S/D metal, contacts or dummy connections are drawn. Not DRC/LVS.",8,"#64748b",mono=True)
    add('</svg>')
    OUT_SVG.write_text('\n'.join(out),encoding='utf-8')
    print(f"bbox {bbox_w:.2f}x{bbox_h:.2f} area {area:.1f} eff {effective:.1f} util {util*100:.2f}% mode {mode}")
    print(f"blocks {len(blocks)} wells {len(well_blocks)} passives {len(passive_blocks)} bb {len(bb_blocks)}")

if __name__=='__main__': main()
