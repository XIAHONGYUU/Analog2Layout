from html import escape
from math import ceil, sqrt
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

S = 6.0
OX, OY = 60.0, 110.0
RING_W = 1.0
RING_GAP = 1.5
GAP = 5.0

def interleave(devs):
    # weighted Bresenham: distribute each device's fingers uniformly
    total = sum(m for _, _, _, m, _ in devs)
    events = []
    for name, w, l, m, color in devs:
        for j in range(m):
            events.append(((j + 0.5) / m, name, w, l, color))
    events.sort(key=lambda e: e[0])
    return [(e[1], e[2], e[3], e[4]) for e in events]

def array_dims(devs):
    w, l = devs[0][1], devs[0][2]
    total = sum(d[3] for d in devs)
    fw = l + 0.8
    fh = w + 1.0
    # Prefer a factor pair (no empty fingers inside the ring); among exact
    # pairs choose the aspect closest to square.  If the count is prime, allow
    # the minimum number of empty cells.
    best = None
    for c in range(1, total + 1):
        r = ceil(total / c)
        waste = c * r - total
        aspect = (c * fw) / (r * fh)
        score = abs(__import__("math").log(aspect)) + waste * 0.5
        if best is None or score < best[0]:
            best = (score, c, r)
    cols, rows = best[1], best[2]
    return dict(fw=fw, fh=fh, cols=cols, rows=rows,
                aw=cols*fw, ah=rows*fh, total=total)

A = {g: array_dims(ds) for g, ds in GROUPS.items()}
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
POS = {}
POS["LOAD_P"] = (0, 0)
POS["FOLD_P"] = (0, GD["LOAD_P"][1] + GAP)
POS["MIRROR_N"] = (0, GD["LOAD_P"][1] + GD["FOLD_P"][1] + 2*GAP)
left_w = max(GD[g][0] for g in ("LOAD_P", "FOLD_P", "MIRROR_N"))
CX = left_w + GAP
POS["IN_DP"] = (CX, 0)
POS["MIRROR_P"] = (CX, GD["IN_DP"][1] + GAP)
POS["BIAS_N"] = (CX, GD["IN_DP"][1] + GD["MIRROR_P"][1] + 2*GAP)
right_w = max(GD[g][0] for g in ("IN_DP", "MIRROR_P", "BIAS_N"))
main_w = CX + right_w
main_h = max(
    POS["MIRROR_N"][1] + GD["MIRROR_N"][1],
    POS["BIAS_N"][1] + GD["BIAS_N"][1],
)

# M14: separate DNW, 8 um gap between DNW outlines.
OUT_X = main_w + 14  # main DNW right = main_w+3, OUT DNW left = OUT_X-3
OUT_Y = 16
POS["OUT"] = (OUT_X, OUT_Y)
C1 = (OUT_X + 2, OUT_Y + GD["OUT"][1] + 8)
R1 = (OUT_X + 2, C1[1] + 16)
dnw2_h = GD["OUT"][1] + 6  # M14 only; C1/R1 stay outside this DNW
layout_w = OUT_X + GD["OUT"][0] + 4
layout_h = max(main_h + 3, R1[1] + 6)

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
txt(34,38,"Class-A CMOS OP — compact white-line layout plan",27,"#0f172a",700)
txt(34,64,"interdigitated matched arrays · shared S/D · shared DM columns · two DNWs (M14 separate, 8 µm gap)",11,"#475569")
txt(34,82,"PMOS upper · NMOS lower · input/output center · W=finger height, L=finger width, m=fingers",9,"#64748b",family="'DejaVu Sans Mono',monospace")

# Two DNWs: main block and separate output device
rect(-3,-3,main_w+6,main_h+6,fill="none",stroke="#0f766e",sw=1.3,rx=2,dash="7 4")
rect(OUT_X-3,OUT_Y-3,GD["OUT"][0]+6,dnw2_h,fill="none",stroke="#0f766e",sw=1.3,rx=2,dash="7 4")
txt_um(-2,main_h+2,"DNW1 · main · one NW/PW well · PMOS bulk=VDD · NMOS bulk=VSS",7.5,"#0f766e",600)
txt_um(OUT_X-3,OUT_Y-4,"DNW2 · M14 output",7.5,"#0f766e",600)
# 8 um gap dimension
line(main_w+3, -7, OUT_X-3, -7, stroke="#0f766e", sw=0.8)
line(main_w+3, -9, main_w+3, -5, stroke="#0f766e", sw=0.8)
line(OUT_X-3, -9, OUT_X-3, -5, stroke="#0f766e", sw=0.8)
txt_um((main_w+3+OUT_X-3)/2, -8, "8 µm",6,"#0f766e",600,"middle")

def draw_group(g):
    gx, gy = POS[g]
    ow, oh = GD[g]
    ds = GROUPS[g]
    color = ds[0][4]
    a = A[g]
    # ring
    rect(gx, gy, ow, oh, fill="none", stroke=color, sw=1.2, rx=1)
    rect(gx+RING_W, gy+RING_W, ow-2*RING_W, oh-2*RING_W, fill="none", stroke=color, sw=0.7, rx=1)
    cx = gx + RING_W + RING_GAP
    cy = gy + RING_W + RING_GAP
    # shared dummy columns
    for side in (-1, 1):
        dx = cx if side < 0 else cx + a["aw"]
        for r in range(a["rows"]):
            rect(dx, cy + r*a["fh"], a["fw"], a["fh"], fill="#e2e8f0", stroke="#94a3b8", sw=0.45, dash="2 1")
            if r == 0:
                txt_um(dx + a["fw"]/2, cy + r*a["fh"] + 1.1, "DM", 6.2, "#475569", 700, "middle")
    # fingers, interleaved
    for idx, (name, w, l, col) in enumerate(SEQ[g]):
        r, c = divmod(idx, a["cols"])
        if r >= a["rows"]:
            continue
        fx = cx + a["fw"] + c*a["fw"]
        fy = cy + r*a["fh"]
        rect(fx, fy, a["fw"], a["fh"], fill="#ffffff", stroke=col, sw=0.35, opacity=0.5)
        pw = a["fw"] - 0.8
        ph = a["fh"] - 1.0
        rect(fx + 0.4, fy + 0.5, pw, ph, fill=col, stroke="none", opacity=0.42)
        line(fx + 0.1, fy + 0.2, fx + a["fw"] - 0.1, fy + 0.2, stroke=col, sw=0.35)
        line(fx + 0.1, fy + a["fh"] - 0.2, fx + a["fw"] - 0.1, fy + a["fh"] - 0.2, stroke=col, sw=0.35)
    # array border
    rect(cx + a["fw"], cy, a["aw"], a["ah"], fill="none", stroke=color, sw=0.8)
    # W/L on first finger
    fx, fy = cx + a["fw"], cy
    pw, ph = a["fw"] - 0.8, a["fh"] - 1.0
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

# C1 / R1
c1x, c1y = C1
rect(c1x, c1y, 5, 10, fill="#ede9fe", stroke="#7c3aed", sw=1.0)
txt_um(c1x, c1y - 1.0, "C1_CC 5pF MOM 5×10", 6, "#5b21b6", 600)
r1x, r1y = R1
for i in range(4):
    rect(r1x + i*2.5, r1y, 2, 3, fill="#fef3c7", stroke="#b45309", sw=0.6)
txt_um(r1x, r1y - 1.0, "R1 4×(2×3) 3.33k", 6, "#92400e", 600)

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

add('</svg>')
Path('examples/classa_opamp/white-line.svg').write_text('\n'.join(out), encoding='utf-8')
print('layout', layout_w, layout_h, 'canvas', W, H)
for g in ORDER:
    print(g, GD[g], A[g]['cols'], A[g]['rows'], A[g]['total'])
