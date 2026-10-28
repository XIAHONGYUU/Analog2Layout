from html import escape
from math import ceil, sqrt, log
from pathlib import Path

# group, [(name, W, L, m, color)], placement row
GROUPS = {
    "IN_DP": [("M1", 10, 4, 8, "#0284c7"), ("M2", 10, 4, 8, "#38bdf8")],
    "LOAD_P": [("M15", 8, 1, 16, "#d97706"), ("M3", 8, 1, 8, "#f59e0b"), ("M4", 8, 1, 8, "#fbbf24")],
    "MIRROR_N": [("M8", 9, 2, 12, "#7c3aed"), ("M9", 9, 2, 12, "#a78bfa")],
    "FOLD_P": [("M6", 12, 2, 20, "#ea580c"), ("M7", 12, 2, 20, "#fb923c")],
    "BIAS_N": [("M16", 2, 2, 81, "#059669"), ("M5", 2, 2, 81, "#34d399"), ("M10", 2, 2, 97, "#6ee7b7")],
    "MIRROR_P": [("M11", 8, 1, 30, "#dc2626"), ("M12", 8, 1, 30, "#f87171"), ("M13", 8, 1, 80, "#fca5a5")],
    "OUT": [("M14", 18, 1, 100, "#be185d")],
}
ORDER = ["LOAD_P", "FOLD_P", "MIRROR_N", "IN_DP", "OUT", "MIRROR_P", "BIAS_N"]

S = 9.0
OX, OY = 60.0, 110.0
RING_W = 1.0
RING_GAP = 0.8
GAP = 2.0

def interleave(devs):
    # weighted round-robin, no same device twice in a row when avoidable
    rem=[d[3] for d in devs]; seq=[]; last=-1
    for _ in range(sum(rem)):
        cand=[i for i,c in enumerate(rem) if c>0 and i!=last] or [i for i,c in enumerate(rem) if c>0]
        i=max(cand,key=lambda k:(rem[k],-k))
        seq.append((devs[i][0],devs[i][1],devs[i][2],devs[i][4]))
        rem[i]-=1; last=i
    return seq

def array_dims(devs, target_h):
    w, l = devs[0][1], devs[0][2]
    total = sum(d[3] for d in devs)
    fw = l + 0.36
    fh = w + 0.60
    best = None
    for rows in range(1, total + 1):
        cols = ceil(total / rows)
        empty = rows * cols - total
        h = rows * fh
        score = abs(h - target_h) + empty * 0.02
        if rows in (2, 4, 6):
            score -= 0.8
        aw = cols * fw
        aspect = aw / max(h, 0.1)
        score += abs(log(aspect / 1.0)) * 0.35
        if best is None or score < best[0]:
            best = (score, cols, rows, aw, h, empty)
    return dict(fw=fw, fh=fh, cols=best[1], rows=best[2], aw=best[3], ah=best[4], empty=best[5])

A = {
    "LOAD_P":   dict(fw=1.36, fh=8.60,  cols=11, rows=3,  aw=14.96, ah=25.80),
    "IN_DP":    dict(fw=4.36, fh=10.60, cols=8,  rows=2,  aw=34.88, ah=21.20),
    "MIRROR_P": dict(fw=1.36, fh=8.60,  cols=47, rows=3,  aw=63.92, ah=25.80),
    "FOLD_P":   dict(fw=2.36, fh=12.60, cols=20, rows=2,  aw=47.20, ah=25.20),
    "MIRROR_N": dict(fw=2.36, fh=9.60,  cols=8,  rows=3,  aw=18.88, ah=28.80),
    "BIAS_N":   dict(fw=2.36, fh=2.60,  cols=24, rows=11, aw=56.64, ah=28.60),
    "OUT":      dict(fw=1.36, fh=18.60, cols=34, rows=3,  aw=46.24, ah=55.80),
}
SEQ = {g: interleave(ds) for g, ds in GROUPS.items()}

def group_dims(g):
    a = A[g]
    # one shared dummy column on each side
    w = a["aw"] + 2 * a["fw"]
    h = a["ah"]
    return (w + 2*(RING_GAP + RING_W), h + 2*(RING_GAP + RING_W))

GD = {g: group_dims(g) for g in GROUPS}

# Main DNW: left column (PMOS upper / NMOS lower) and center column
# (input / PMOS mirror / NMOS bias).  M14 is in its own DNW, 8 um away.
POS={}
# Row 1: PMOS mirror + centered input + PMOS load
POS["MIRROR_P"]=(0,0)
POS["IN_DP"]=(GD["MIRROR_P"][0]+2,0)
POS["LOAD_P"]=(POS["IN_DP"][0]+GD["IN_DP"][0]+2,0)
row1_h=max(GD[g][1] for g in ("MIRROR_P","IN_DP","LOAD_P"))
# Row 2: PMOS fold + NMOS mirror + NMOS bias
POS["FOLD_P"]=(0,row1_h+2)
POS["MIRROR_N"]=(GD["FOLD_P"][0]+2,row1_h+2)
POS["BIAS_N"]=(POS["MIRROR_N"][0]+GD["MIRROR_N"][0]+2,row1_h+2)
row2_h=max(GD[g][1] for g in ("FOLD_P","MIRROR_N","BIAS_N"))
base_main_w=max(POS[g][0]+GD[g][0] for g in ("MIRROR_P","IN_DP","LOAD_P","FOLD_P","MIRROR_N","BIAS_N"))
main_h=row1_h+2+row2_h
# Guarded passive bay inside DNW1: C1 over R1, both with AA rings.
P_GAP=0.8; P_RING=1.0
C1_W,C1_H=5.0,10.0
R1_W,R1_H=4.5,6.5
C1_OUT_W,C1_OUT_H=C1_W+2*(P_GAP+P_RING), C1_H+2*(P_GAP+P_RING)
R1_OUT_W,R1_OUT_H=R1_W+2*(P_GAP+P_RING), R1_H+2*(P_GAP+P_RING)
PB_X=max(POS[g][0]+GD[g][0] for g in ("MIRROR_P","IN_DP","LOAD_P"))+2.0
PB_Y=4.0
C1_OUT=(PB_X,PB_Y,C1_OUT_W,C1_OUT_H)
R1_OUT=(PB_X,PB_Y+C1_OUT_H+2.0,R1_OUT_W,R1_OUT_H)
C1=(PB_X+P_GAP+P_RING, PB_Y+P_GAP+P_RING)
R1=(PB_X+P_GAP+P_RING, R1_OUT[1]+P_GAP+P_RING)
main_w=max(base_main_w, PB_X+C1_OUT_W)
OUT_X=main_w+14
OUT_Y=max(0,(main_h-GD["OUT"][1])/2)
POS["OUT"]=(OUT_X,OUT_Y)
dnw2_h=GD["OUT"][1]+6
layout_w=OUT_X+GD["OUT"][0]+4
layout_h=main_h+3

W = int(OX + layout_w * S + 520)
H = int(OY + layout_h * S + 160)
out = []
def add(s): out.append(s)
def X(x): return OX + x * S
def Y(y): return OY + y * S
def rect(x,y,w,h,fill="none",stroke="#0f172a",sw=1.0,rx=0,dash=None,opacity=1):
    d=f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<rect x="{X(x):.1f}" y="{Y(y):.1f}" width="{w*S:.1f}" height="{h*S:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}"{d}/>')
def line(x1,y1,x2,y2,stroke="#0f172a",sw=0.9,dash=None):
    d=f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<line x1="{X(x1):.1f}" y1="{Y(y1):.1f}" x2="{X(x2):.1f}" y2="{Y(y2):.1f}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round"{d}/>')
def txt(x,y,s,size=12,fill="#0f172a",weight=400,anchor="start",family="'DejaVu Sans',sans-serif"):
    add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escape(s)}</text>')
def txt_um(x,y,s,size=9,fill="#0f172a",weight=400,anchor="start",family="'DejaVu Sans Mono',monospace"):
    txt(X(x), Y(y), s, size, fill, weight, anchor, family)

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="class-A op-amp white-line layout plan">')
rect(-1000,-1000,5000,5000,fill="#f8fafc",stroke="none")
txt(34,38,"Class-A CMOS OP — area-min white-line candidate",27,"#0f172a",700)
txt(34,64,"area-first candidate · per-group row shapes · R/C guarded inside DNW1 · M14 outer DNW2 (8 µm gap)",11,"#475569")
txt(34,82,"220 × 64 µm class · PMOS upper · NMOS lower · M14 outer · W=finger height, L=finger width, m=fingers",9,"#64748b",family="'DejaVu Sans Mono',monospace")

# Two DNWs: DNW1 is a stepped outline around the two group rows; DNW2 is M14 only.
row1_right=max(POS[g][0]+GD[g][0] for g in ("MIRROR_P","IN_DP","LOAD_P"))
row1_right=max(row1_right, PB_X+C1_OUT_W)
row2_right=max(POS[g][0]+GD[g][0] for g in ("FOLD_P","MIRROR_N","BIAS_N"))
step_y=row1_h+1.0
pts=[(-3,-3),(row1_right+3,-3),(row1_right+3,step_y),(row2_right+3,step_y),
     (row2_right+3,main_h+3),(-3,main_h+3),(-3,-3)]
path=' '.join(f'{"M" if i==0 else "L"}{X(x):.1f},{Y(y):.1f}' for i,(x,y) in enumerate(pts))
add(f'<path d="{path}" fill="none" stroke="#0f766e" stroke-width="1.3" stroke-dasharray="7 4"/>')
rect(OUT_X-3,OUT_Y-3,GD["OUT"][0]+6,dnw2_h,fill="none",stroke="#0f766e",sw=1.3,rx=2,dash="7 4")
txt_um(-2,main_h+2,"DNW1 · stepped around groups · one NW/PW well",7.5,"#0f766e",600)
txt_um(OUT_X-3,OUT_Y-4,"DNW2 · M14 output",7.5,"#0f766e",600)
line(main_w+3,-7,OUT_X-3,-7,stroke="#0f766e",sw=0.8)
line(main_w+3,-9,main_w+3,-5,stroke="#0f766e",sw=0.8)
line(OUT_X-3,-9,OUT_X-3,-5,stroke="#0f766e",sw=0.8)
txt_um((main_w+3+OUT_X-3)/2,-8,"8 µm",6,"#0f766e",600,"middle")

def draw_group(g):
    gx, gy = POS[g]
    ow, oh = GD[g]
    ds = GROUPS[g]
    color = ds[0][4]
    a = A[g]
    # ring: AA band + inner boundary
    rect(gx, gy, ow, oh, fill="#d1fae5", stroke=color, sw=1.2, rx=1)
    rect(gx+RING_W, gy+RING_W, ow-2*RING_W, oh-2*RING_W, fill="#f8fafc", stroke=color, sw=0.7, rx=1)
    # simplified well boundary (NW for PMOS, PW for NMOS); not a DRC drawing
    if g in ("MIRROR_P", "LOAD_P", "FOLD_P"):
        rect(gx-0.2, gy-0.2, ow+0.4, oh+0.4, fill="none", stroke="#1d4ed8", sw=0.5, dash="3 2")
        txt_um(gx+ow-3.0, gy-0.4, "NW", 7, "#1d4ed8", 700)
    else:
        rect(gx-0.2, gy-0.2, ow+0.4, oh+0.4, fill="none", stroke="#64748b", sw=0.5, dash="3 2")
        txt_um(gx+ow-3.0, gy-0.4, "PW", 7, "#475569", 700)
    cx = gx + RING_W + RING_GAP
    cy = gy + RING_W + RING_GAP
    # shared dummy columns
    for side in (-1, 1):
        dx = cx if side < 0 else cx + a["fw"] + a["aw"]
        for r in range(a["rows"]):
            # dummy is the same finger geometry as active; only the label differs
            rect(dx, cy + r*a["fh"], a["fw"], a["fh"], fill="#ffffff", stroke="#64748b", sw=0.35, opacity=0.45)
            pw = a["fw"] - 0.36
            ph = a["fh"] - 0.60
            rect(dx + 0.18, cy + r*a["fh"] + 0.30, pw, ph, fill="#cbd5e1", stroke="none", opacity=0.45)
            line(dx + 0.05, cy + r*a["fh"] + 0.12, dx + a["fw"] - 0.05, cy + r*a["fh"] + 0.12, stroke="#64748b", sw=0.3)
            line(dx + 0.05, cy + r*a["fh"] + a["fh"] - 0.12, dx + a["fw"] - 0.05, cy + r*a["fh"] + a["fh"] - 0.12, stroke="#64748b", sw=0.3)
            if r == 0:
                txt_um(dx + a["fw"]/2, cy + r*a["fh"] - 0.3, "DM", 5.5, "#475569", 700, "middle")
    # fingers, interleaved
    for idx, (name, w, l, col) in enumerate(SEQ[g]):
        r, c = divmod(idx, a["cols"])
        if r >= a["rows"]:
            continue
        fx = cx + a["fw"] + c*a["fw"]
        fy = cy + r*a["fh"]
        rect(fx, fy, a["fw"], a["fh"], fill="#ffffff", stroke=col, sw=0.35, opacity=0.5)
        pw = a["fw"] - 0.36
        ph = a["fh"] - 0.60
        rect(fx + 0.4, fy + 0.5, pw, ph, fill=col, stroke="none", opacity=0.42)
        line(fx + 0.1, fy + 0.2, fx + a["fw"] - 0.1, fy + 0.2, stroke=col, sw=0.35)
        line(fx + 0.1, fy + a["fh"] - 0.2, fx + a["fw"] - 0.1, fy + a["fh"] - 0.2, stroke=col, sw=0.35)
    # fill unused cells with a real dummy finger (e.g. BIAS_N 259 in 260)
    used = len(SEQ[g])
    total = a["cols"] * a["rows"]
    for idx in range(used, total):
        r, c = divmod(idx, a["cols"])
        fx = cx + a["fw"] + c*a["fw"]
        fy = cy + r*a["fh"]
        rect(fx, fy, a["fw"], a["fh"], fill="#ffffff", stroke="#64748b", sw=0.35, opacity=0.45)
        pw = a["fw"] - 0.36; ph = a["fh"] - 0.60
        rect(fx + 0.18, fy + 0.30, pw, ph, fill="#cbd5e1", stroke="none", opacity=0.45)
        line(fx + 0.05, fy + 0.12, fx + a["fw"] - 0.05, fy + 0.12, stroke="#64748b", sw=0.3)
        line(fx + 0.05, fy + a["fh"] - 0.12, fx + a["fw"] - 0.05, fy + a["fh"] - 0.12, stroke="#64748b", sw=0.3)
    # array border
    rect(cx + a["fw"], cy, a["aw"], a["ah"], fill="none", stroke=color, sw=0.8)
    # W/L on first finger
    fx, fy = cx + a["fw"], cy
    pw, ph = a["fw"] - 0.36, a["fh"] - 0.60
    line(fx + pw + 0.25, fy + 0.5, fx + pw + 0.25, fy + 0.5 + ph, stroke="#0f172a", sw=0.45)
    line(fx + pw + 0.15, fy + 0.5, fx + pw + 0.35, fy + 0.5, stroke="#0f172a", sw=0.45)
    line(fx + pw + 0.15, fy + 0.5 + ph, fx + pw + 0.35, fy + 0.5 + ph, stroke="#0f172a", sw=0.45)
    txt_um(fx + pw + 0.45, fy + 0.5 + ph/2, f"W{round(ph)}", 5.5, "#0f172a", 600)
    line(fx + 0.4, fy + 0.5 + ph + 0.2, fx + 0.4 + pw, fy + 0.5 + ph + 0.2, stroke="#0f172a", sw=0.45)
    txt_um(fx + 0.4 + pw/2, fy + 0.5 + ph + 0.7, f"L{round(pw)}", 5.5, "#0f172a", 600, "middle")
    # group label above
    label = "/".join(d[0] for d in ds)
    txt_um(gx, gy - 1.0, label, 7, color, 700)
    dims = "/".join(str(d[3]) for d in ds)
    txt_um(gx, gy - 0.2, f"W{ds[0][1]}/L{ds[0][2]}  m={dims}  DM shared", 5.5, "#475569", 600)

for g in ORDER:
    draw_group(g)

# C1 / R1 inside DNW1, each with an AA guard ring
for (ox,oy,ow,oh), inner, label, col in (
    (C1_OUT,(C1_W,C1_H),"C1_CC 5pF MOM 5×10","#5b21b6"),
    (R1_OUT,(R1_W,R1_H),"R1 4×(2×3) 3.33k","#92400e"),
):
    rect(ox, oy, ow, oh, fill="#d1fae5", stroke="#0f766e", sw=0.8)
    rect(ox+P_RING, oy+P_RING, ow-2*P_RING, oh-2*P_RING, fill="#f8fafc", stroke="#64748b", sw=0.5, dash="2 1")
    txt_um(ox, oy-0.7, label, 5.8, col, 600)
c1x,c1y=C1; rect(c1x,c1y,C1_W,C1_H,fill="#ede9fe",stroke="#7c3aed",sw=1.0)
r1x,r1y=R1
for i in range(4):
    rect(r1x + (i % 2)*2.5, r1y + (i // 2)*3.5, 2, 3, fill="#fef3c7", stroke="#b45309", sw=0.6)

# scale
line(0, layout_h + 8, 50, layout_h + 8, stroke="#0f172a", sw=2)
line(0, layout_h + 6, 0, layout_h + 10, stroke="#0f172a", sw=2)
line(50, layout_h + 6, 50, layout_h + 10, stroke="#0f172a", sw=2)
txt(X(25), Y(layout_h+8)+16, "50 µm", 8, "#0f172a", 600, "middle", "'DejaVu Sans Mono',monospace")
txt(X(0), Y(layout_h+8)+32, "scale bar · each stripe is one finger; adjacent fingers share S/D", 7.5, "#64748b", family="'DejaVu Sans Mono',monospace")

# legend
lx = OX + layout_w*S + 26
ly = OY
txt(lx, ly, "LEGEND", 8.5, "#475569", 700, family="'DejaVu Sans Mono',monospace")
ry = ly + 18
for g in ORDER:
    ds = GROUPS[g]
    txt(lx, ry, g, 7.5, ds[0][4], 700, family="'DejaVu Sans Mono',monospace")
    ry += 11
    for name, w, l, m, color in ds:
        rect(lx+1, ry-6, 2, 2, fill=color, stroke="none")
        txt(lx+7, ry, f"{name:4s} {w}/{l} m={m}", 6.8, "#334155", family="'DejaVu Sans Mono',monospace")
        ry += 10
    ry += 2
txt(lx, ry+6, "DM = shared dummy column (both ends)", 6.5, "#64748b", family="'DejaVu Sans Mono',monospace")
txt(lx, ry+20, "ring 1.0 µm / gap 1.5 µm (edu)", 7, "#64748b", family="'DejaVu Sans Mono',monospace")
txt(lx, ry+34, "M13 PMOS current source · M14 output", 7, "#64748b", family="'DejaVu Sans Mono',monospace")

# Effective area: inside outer ring = inner + ring AA; R/C including its ring.
# Denominator: rectangular bbox enclosing all DNW outer boundaries.
mos_outer = sum(GD[g][0]*GD[g][1] for g in GROUPS)
passive_outer = C1_OUT_W*C1_OUT_H + R1_OUT_W*R1_OUT_H
eff = mos_outer + passive_outer
bbox_w = (OUT_X+GD["OUT"][0]+3) - (-3)
bbox_h = (max(main_h, GD["OUT"][1])+3) - (-3)
bbox_area = bbox_w*bbox_h
util = eff / bbox_area
txt(lx,ry+60,f"effective = MOS ring outer + R/C ring = {eff:.0f} um2",6.0,"#475569",family="'DejaVu Sans Mono',monospace")
txt(lx,ry+72,f"module bbox = {bbox_w:.1f} x {bbox_h:.1f} = {bbox_area:.0f} um2",6.0,"#475569",family="'DejaVu Sans Mono',monospace")
txt(lx,ry+84,f"utilization = {util*100:.1f}% (ring AA included)",6.0,"#475569",family="'DejaVu Sans Mono',monospace")

add('</svg>')
Path('examples/classa_opamp/area-min.svg').write_text('\n'.join(out), encoding='utf-8')
print('layout', layout_w, layout_h, 'canvas', W, H)
for g in ORDER:
    print(g, GD[g], A[g]['cols'], A[g]['rows'], sum(d[3] for d in GROUPS[g]))
