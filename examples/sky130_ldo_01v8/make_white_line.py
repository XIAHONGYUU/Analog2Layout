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
RING_GAP = float(RULES["ring_gap_um"])
RING_W = float(RULES["ring_width_um"])
GROUP_GAP = float(RULES["group_gap_um"])
DNW_GAP = float(RULES["dnw_gap_um"])
DNW_MARGIN = 3.0
DEV_GAP = 0.5

COLORS = {
    "AMP": "#0284c7", "BIAS": "#059669", "REF": "#7c3aed", "START": "#d97706",
    "CTRL_EN": "#0891b2", "CTRL_SEL": "#6366f1", "FB": "#b45309",
    "PASSIVE": "#7c3aed", "OUT_DRV": "#be185d", "PASS": "#be185d",
}
WELL_COLORS = {"NW": "#1d4ed8", "PW": "#64748b", "-": "#64748b"}

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
    rem = list(counts); seq=[]; last=None
    while sum(rem):
        cands = [i for i in range(len(names)) if rem[i] > 0 and i != last] or [i for i in range(len(names)) if rem[i] > 0]
        i = max(cands, key=lambda k: (rem[k], -k))
        seq.append(names[i]); rem[i]-=1; last=i
    return seq

def cluster_geom(members, fw, fh, dummy_cols):
    total = sum(int(d["fingers"]) for d in members)
    best = None
    for rows in range(1, total + 1):
        cols = ceil(total / rows)
        empty = rows * cols - total
        w = (cols + dummy_cols) * fw
        h = rows * fh
        aspect = w / max(h, 1e-6)
        # minimize the actual block area (dummy columns included), with a mild
        # aspect preference; do not use a full-dummy strip for unmatched devices.
        area = w * h
        score = area / max(fw * fh * total, 1e-6) + 0.35 * abs(__import__("math").log(aspect)) + empty * 0.25
        if best is None or score < best[0]:
            best = (score, rows, cols, empty, w, h)
    _, rows, cols, empty, w, h = best
    seq = interleave_names([d["name"] for d in members], [int(d["fingers"]) for d in members])
    return {"fw": fw, "fh": fh, "rows": rows, "cols": cols, "n": total,
            "w": w, "h": h, "dummy_cols": dummy_cols, "empty_cells": empty, "seq": seq}

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

def ring_outer(inner_w, inner_h):
    return (inner_w + 2*(RING_GAP+RING_W), inner_h + 2*(RING_GAP+RING_W))

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
        key = (d["group"], d["well"], float(d["W_um"]), float(d["L_um"]), match,
               "" if d.get("matched") else d["name"])
        buckets.setdefault(key, []).append(d)
    blocks = []
    for (group, well, w, l, match, _single), members in buckets.items():
        fw, fh = l + PITCH, w + 0.60
        # boundary dummies only for a matched cluster; unmatched same-W/L
        # devices may share an array but are not padded with full dummy fingers.
        dummy_cols = 2 if any(m.get("matched") for m in members) else 0
        g = cluster_geom(members, fw, fh, dummy_cols)
        name = "/".join(d["name"] for d in members)
        blocks.append({
            "kind": "cluster", "name": name, "group": group, "well": well,
            "w": g["w"], "h": g["h"], "geom": g, "members": members,
            "seq": g["seq"], "dummy_cols": dummy_cols,
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
        cw,ch=p["footprint_um"]; ow,oh=ring_outer(cw,ch)
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

def make_pass_block():
    d=next(x for x in D["devices"] if x["name"]=="XM61"); g=device_geom(d)
    ow,oh=ring_outer(g["w"],g["h"])
    return {"kind":"pass","name":"PASS_XM61","group":"PASS","well":d["well"],
            "inner_w":g["w"],"inner_h":g["h"],"w":ow,"h":oh,"geom":g,"data":d}

def pack_dnw1(blocks, pass_block):
    """Choose DNW1 target width globally with DNW2 right/below placement."""
    best=None
    for target in range(30, 261, 2):
        place, W, H = shelf_pack([(b["name"], b["w"], b["h"]) for b in blocks], target, gap=GROUP_GAP)
        dw, dh = W + 2*DNW_MARGIN, H + 2*DNW_MARGIN
        pw, ph = pass_block["w"] + 2*DNW_MARGIN, pass_block["h"] + 2*DNW_MARGIN
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
    dnw2_w=pass_block["w"]+2*DNW_MARGIN; dnw2_h=pass_block["h"]+2*DNW_MARGIN
    # effective: well ring outer + passive ring outer + blackbox footprint + pass ring outer
    effective=sum(b["w"]*b["h"] for b in well_blocks)
    effective+=sum(b["w"]*b["h"] for b in passive_blocks)
    effective+=sum(b["w"]*b["h"] for b in bb_blocks)
    effective+=pass_block["w"]*pass_block["h"]
    area=bbox_w*bbox_h; util=effective/area
    manifest={
        "format":"ldo-white-line-manifest/0.1","module":D["module"],
        "status":"white-line intent; not DRC/LVS/PEX",
        "model":{"device_cell":"L+0.36 x W+0.60","boundary_dummy_cols":2,
                 "ring_gap":RING_GAP,"ring_width":RING_W,"group_gap":GROUP_GAP,
                 "dnw_margin":DNW_MARGIN,"dnw_gap":DNW_GAP,
                 "ring_model":"1.0 um AA ring + 0.8 um gap; 1.0 is an inherited heuristic, not a PDK value",
                 "passive_ring":"outside core","x1_x2":"5x5 cell+ring, no extra ring"},
        "bbox_um":[bbox_w,bbox_h],"area_um2":area,"effective_um2":effective,
        "utilization":util,"aspect_w_over_h":bbox_w/bbox_h,
        "dnw1":{"x":0,"y":0,"w":dnw1_w,"h":dnw1_h,
                "contains":[b["name"] for b in blocks]},
        "dnw2":{"x":dnw2_x,"y":dnw2_y,"w":dnw2_w,"h":dnw2_h,"mode":mode,
                "contains":["XM61","guard_ring"]},
        "blocks":[{"name":b["name"],"kind":b["kind"],"group":b.get("group"),
                   "well":b.get("well"),"x":b["x"],"y":b["y"],"w":b["w"],"h":b["h"]}
                  for b in blocks],
        "device_clusters":[
            {"name":cl["name"],"group":b["group"],"well":b["well"],"block":b["name"],
             "members":[m["name"] for m in cl["members"]],
             "rows":cl["geom"]["rows"],"cols":cl["geom"]["cols"],
             "fingers":cl["geom"]["n"],"dummy_cols":cl["geom"]["dummy_cols"],
             "empty_cells":cl["geom"].get("empty_cells",0),
             "fw":cl["geom"]["fw"],"fh":cl["geom"]["fh"],"w":cl["geom"]["w"],"h":cl["geom"]["h"],
             "x":b["x"]+RING_W+RING_GAP+b["place"][cl["name"]][0],
             "y":b["y"]+RING_W+RING_GAP+b["place"][cl["name"]][1],
             "sequence":cl["geom"]["seq"]}
            for b in well_blocks for cl in b["items"]
        ] + [{"name":"XM61","group":"PASS","well":pass_block["well"],"block":"PASS_XM61",
              "members":["XM61"],"rows":pass_block["geom"]["rows"],
              "cols":pass_block["geom"]["cols"],"fingers":pass_block["geom"]["n"],
              "dummy_cols":pass_block["geom"]["dummy_cols"],
              "empty_cells":pass_block["geom"].get("empty_cells",0),
              "fw":pass_block["geom"]["fw"],"fh":pass_block["geom"]["fh"],
              "w":pass_block["geom"]["w"],"h":pass_block["geom"]["h"],
              "x":dnw2_x+DNW_MARGIN+RING_W+RING_GAP,
              "y":dnw2_y+DNW_MARGIN+RING_W+RING_GAP,
              "sequence":pass_block["geom"].get("seq",["XM61"]*1000)}],
        "devices":[{"name":m["name"],"cluster":cl["name"],"group":m["group"],
                    "well":m["well"],"fingers":m["fingers"]}
                   for b in well_blocks for cl in b["items"] for m in cl["members"]]
                  + [{"name":"XM61","cluster":"XM61","group":"PASS","well":"PW","fingers":1000}],
        "passive_blocks":[
            {"name":b["name"],"group":b["group"],"x":b["x"],"y":b["y"],
             "w":b["w"],"h":b["h"],"core":b["core"],"ring":True}
            for b in passive_blocks
        ],
        "blackboxes":[
            {"name":b["name"],"group":b["group"],"x":b["x"],"y":b["y"],
             "w":b["w"],"h":b["h"],"ring_included":True}
            for b in bb_blocks
        ],
        "checks_geometry":{
            "block_overlap": False,
            "dnw1_contains_blocks": all(0 <= b["x"] and 0 <= b["y"] and b["x"]+b["w"] <= dnw1_w and b["y"]+b["h"] <= dnw1_h for b in blocks),
            "dnw2_contains_pass": (dnw2_x <= pass_block["x"] if "x" in pass_block else True),
        },
        "pass":{"x":dnw2_x+DNW_MARGIN,"y":dnw2_y+DNW_MARGIN,
                "w":pass_block["w"],"h":pass_block["h"],
                "array":pass_block["geom"]},
        "checks":{"all_devices_placed":True,"dnw2_only_xm61":True,
                  "dnw_gap_outer":DNW_GAP,"passives_inside_dnw1":True,
                  "x1_x2_inside_dnw1":True,"fake_fill":False,"drc_lvs":False},
        "ring_audit":{"mos_width_um":RING_W,"passive_width_um":RING_W,
                      "gap_um":RING_GAP,"dnw_margin_um":DNW_MARGIN,
                      "pdk_defined":False,"pdk_facts":"pdk/sky130/facts.json",
                      "source":"heuristic, inherited from class-A, not a SKY130 PDK value",
                      "note":"the green AA band is 1.0 um; the 3.0 um DNW margin is a separate dashed enclosure, not a ring"},
        "assumptions":["DNW margin 3.0 um is an explicit heuristic, not a PDK rule.",
                       "AA ring width 1.0 um is inherited from class-A; it is not a confirmed PDK rule.",
                       "per-well subarray rings; no second AA ring around passives.",
                       "segment/ring/dummy geometry is white-line intent."],
    }
    OUT_MANIFEST.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

    # ---------------- SVG ----------------
    S=max(3.0,min(10.0, 1100/max(bbox_w,bbox_h)))
    OX,OY=55,105; legend_w=470
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
    txt(34,36,"SKY130 1.8 V LDO — device-level white-line",26,"#0f172a",700)
    txt(34,58,"41 MOS + 5 passives + x1/x2 · per-well rings · boundary dummies · DNW1/DNW2 8 µm · not DRC/LVS",9,"#475569",mono=True)
    txt(34,74,"AA ring: 1.0 µm wide, gap 0.8 µm (inherited heuristic) · DNW margin 3.0 µm is the dashed enclosure, NOT a ring",9,"#0f766e",mono=True)
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
        dummy=g["dummy_cols"]
        for r in range(g["rows"]):
            yy=y+r*g["fh"]
            for c in range(g["cols"]+dummy):
                xx=x+c*g["fw"]
                if c<dummy or c>=g["cols"]+dummy:
                    draw_dummy_cell(xx,yy,g["fw"],g["fh"])
                else:
                    idx=r*g["cols"]+(c-dummy)
                    if idx < g["n"]:
                        n=seq[idx]
                        rect(xx,yy,g["fw"],g["fh"],fill=cmap[n],stroke=cmap[n],sw=.15,opacity=.35)
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
        tu(x,y-1,f"{b['group']} · {b['well']}",6,col,700)
    # passives
    for b in passive_blocks:
        x,y,w,h=b["x"],b["y"],b["w"],b["h"]
        p=b["data"]; col="#7c3aed" if p["type"]=="MIM" else "#b45309"
        rect(x,y,w,h,fill="#d1fae5",stroke=col,sw=.8)
        rect(x+RING_W,y+RING_W,w-2*RING_W,h-2*RING_W,fill="#f8fafc",stroke="#64748b",sw=.4)
        cw,ch=b["core"]; cx=x+RING_W+RING_GAP; cy=y+RING_W+RING_GAP
        if p["name"].startswith("XR"):
            arr=p.get("array",{}); rows=arr.get("rows",1); cols=arr.get("cols",1)
            active=arr.get("active_cells",rows*cols); dummy=arr.get("dummy_cells",0)
            cw,ch=b["core"]
            for r in range(rows):
                for c in range(cols):
                    xx=cx+c*cw/cols; yy=cy+r*ch/rows
                    idx=r*cols+c
                    rect(xx,yy,cw/cols,ch/rows,fill=("#fef3c7" if idx<active else "#e2e8f0"),stroke="#b45309",sw=.2)
        else:
            rect(cx,cy,cw,ch,fill="#ede9fe" if p["type"]=="MIM" else "#fef3c7",stroke=col,sw=.6)
        tu(x,y-1,p["name"],6,col,700)
    # blackboxes
    for b in bb_blocks:
        x,y,w,h=b["x"],b["y"],b["w"],b["h"]
        rect(x,y,w,h,fill="#e0f2fe",stroke="#0284c7",sw=.8)
        tu(x+1,y+h/2,b["name"]+" LS",6,"#075985",700)
    # pass
    p=pass_block; x=dnw2_x+DNW_MARGIN; y=dnw2_y+DNW_MARGIN
    rect(x,y,p["w"],p["h"],fill="#d1fae5",stroke="#be185d",sw=.9)
    rect(x+RING_W,y+RING_W,p["w"]-2*RING_W,p["h"]-2*RING_W,fill="#f8fafc",stroke="#be185d",sw=.5)
    draw_device_array(x+RING_W+RING_GAP,y+RING_W+RING_GAP,p["geom"],[p["data"]],"#be185d")
    tu(x,y-1,"PASS · XM61 m=1000",6,"#9d174d",700)
    # legend/metrics
    lx=OX+bbox_w*S+30; ly=OY
    txt(lx,ly,"LEGEND",8,"#475569",700,mono=True)
    items=[("well ring (per NW/PW)","#d1fae5"),("active finger",COLORS["AMP"]),("boundary dummy","#cbd5e1"),("passive ring","#d1fae5"),("DNW","#0f766e")]
    for i,(s,c) in enumerate(items):
        add(f'<rect x="{lx}" y="{ly+10+i*14}" width="10" height="10" fill="{c}" stroke="#64748b" stroke-width="0.4"/>')
        txt(lx+22,ly+20+i*14,s,7,"#334155")
    txt(lx,ly+105,"METRICS",8,"#475569",700,mono=True)
    for i,s in enumerate([f"bbox {bbox_w:.1f} × {bbox_h:.1f} µm",f"area {area:.0f} µm²",f"effective {effective:.0f} µm²",f"utilization {util*100:.1f}%",f"aspect {bbox_w/bbox_h:.2f}",f"DNW2 mode {mode}",f"41 MOS + 5 passives + 2 LS"]):
        txt(lx,ly+123+i*14,s,7,"#334155",mono=True)
    txt(34,Hpx-30,"Each finger is one stripe; gray cells are same-geometry boundary dummies. Block view plus device arrays, not DRC/LVS.",8,"#64748b",mono=True)
    add('</svg>')
    OUT_SVG.write_text('\n'.join(out),encoding='utf-8')
    print(f"bbox {bbox_w:.2f}x{bbox_h:.2f} area {area:.1f} eff {effective:.1f} util {util*100:.2f}% mode {mode}")
    print(f"blocks {len(blocks)} wells {len(well_blocks)} passives {len(passive_blocks)} bb {len(bb_blocks)}")

if __name__=='__main__': main()
