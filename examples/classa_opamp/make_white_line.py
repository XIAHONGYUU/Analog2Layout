from html import escape
from math import ceil, sqrt
from pathlib import Path

# name, W (finger width, um), L (channel length, um), m (parallel units), group, color
DEV = [
    ("M1", 10, 4, 8, "IN_DP", "#0284c7"),
    ("M2", 10, 4, 8, "IN_DP", "#0284c7"),
    ("M3", 8, 1, 8, "LOAD_P", "#d97706"),
    ("M4", 8, 1, 8, "LOAD_P", "#d97706"),
    ("M15", 8, 1, 16, "LOAD_P", "#d97706"),
    ("M16", 2, 2, 81, "BIAS_N", "#059669"),
    ("M5", 2, 2, 81, "BIAS_N", "#059669"),
    ("M10", 2, 2, 97, "BIAS_N", "#059669"),
    ("M8", 9, 2, 12, "MIRROR_N", "#7c3aed"),
    ("M9", 9, 2, 12, "MIRROR_N", "#7c3aed"),
    ("M6", 12, 2, 20, "FOLD_P", "#ea580c"),
    ("M7", 12, 2, 20, "FOLD_P", "#ea580c"),
    ("M11", 8, 1, 30, "MIRROR_P", "#dc2626"),
    ("M12", 8, 1, 30, "MIRROR_P", "#dc2626"),
    ("M13", 8, 1, 80, "MIRROR_P", "#dc2626"),
    ("M14", 18, 1, 100, "OUT", "#be185d"),
]
GROUPS = ["IN_DP", "MIRROR_N", "FOLD_P", "LOAD_P", "BIAS_N", "MIRROR_P", "OUT"]

S = 5.0
OX, OY = 70.0, 120.0
RING_W = 1.0
RING_GAP = 1.5
DUMMY = 1  # one dummy finger at each W end of each array
SD_RAIL = 0.35

def array_dims(w, l, m):
    fw = l + 0.8          # horizontal pitch per finger (L + contacts)
    fh = w + 1.0          # vertical finger height (W + S/D)
    # aim for a compact, roughly 1.5:1 array
    cols = max(1, round(sqrt(max(m, 1) * fh / (fw * 1.5))))
    cols = min(cols, m)
    rows = max(1, ceil(m / cols))
    bw = cols * fw
    bh = rows * fh
    return dict(fw=fw, fh=fh, cols=cols, rows=rows, bw=bw, bh=bh)

A = {name: array_dims(w, l, m) for name, w, l, m, *_ in DEV}

def array_size(name):
    a = A[name]
    return a["bw"] + 2 * DUMMY * a["fw"], a["bh"]

def group_layout(g):
    names = [d[0] for d in DEV if d[4] == g]
    if g == "MIRROR_P":
        top = ["M11", "M12"]
        top_w = sum(array_size(n)[0] for n in top) + 2.0
        top_h = max(array_size(n)[1] for n in top)
        bot = "M13"
        bot_w, bot_h = array_size(bot)
        cw = max(top_w, bot_w)
        ch = top_h + 2.0 + bot_h
        pos = {}
        x = 0.0
        for n in top:
            bw, bh = array_size(n)
            pos[n] = (x, 0.0)
            x += bw + 2.0
        pos[bot] = (0.0, top_h + 2.0)
        return dict(names=top + [bot], cw=cw, ch=ch, pos=pos)
    # one row of arrays
    widths = [array_size(n)[0] for n in names]
    heights = [array_size(n)[1] for n in names]
    cw = sum(widths) + 2.0 * (len(names) - 1)
    ch = max(heights)
    pos = {}
    x = 0.0
    for n, w, h in zip(names, widths, heights):
        pos[n] = (x, ch - h)
        x += w + 2.0
    return dict(names=names, cw=cw, ch=ch, pos=pos)

GL = {g: group_layout(g) for g in GROUPS}

def group_outer(g):
    gl = GL[g]
    content_w = gl["cw"]
    content_h = gl["ch"]
    return content_w + 2 * (RING_GAP + RING_W), content_h + 2 * (RING_GAP + RING_W)

GO = {g: group_outer(g) for g in GROUPS}

POS = {}
POS["IN_DP"] = (0, 0)
POS["MIRROR_N"] = (0, GO["IN_DP"][1] + 6)
POS["FOLD_P"] = (0, GO["IN_DP"][1] + GO["MIRROR_N"][1] + 12)
POS["LOAD_P"] = (0, GO["IN_DP"][1] + GO["MIRROR_N"][1] + GO["FOLD_P"][1] + 18)
left_w = max(GO[g][0] for g in ["IN_DP", "MIRROR_N", "FOLD_P", "LOAD_P"])
RX = left_w + 18
POS["BIAS_N"] = (RX, 0)
POS["MIRROR_P"] = (RX, GO["BIAS_N"][1] + 6)
POS["OUT"] = (RX, GO["BIAS_N"][1] + GO["MIRROR_P"][1] + 12)

C1 = (RX + 2, POS["OUT"][1] + GO["OUT"][1] + 8)
R1 = (RX + 8, POS["OUT"][1] + GO["OUT"][1] + 24)
layout_w = max(left_w, RX + GO["BIAS_N"][0], RX + GO["MIRROR_P"][0],
               RX + GO["OUT"][0], C1[0] + 5, R1[0] + 10)
layout_h = max(POS["LOAD_P"][1] + GO["LOAD_P"][1], R1[1] + 4)

W = int(OX + layout_w * S + 470)
H = int(OY + layout_h * S + 150)
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
txt(36,38,"Class-A CMOS OP — white-line layout plan",27,"#0f172a",700)
txt(36,64,"vertical-finger MOS arrays · shared S/D · dummies at both W ends · one ring per matched group",11,"#475569")
txt(36,82,"PMOS bulk=VDD · NMOS bulk=VSS · one DNW · one NW/PW well · W=finger height, L=finger width, m=fingers",9,"#64748b",family="'DejaVu Sans Mono',monospace")

# DNW
rect(-4,-4,layout_w+8,layout_h+8,fill="none",stroke="#0f766e",sw=1.2,rx=2,dash="7 4")
txt_um(-3,layout_h+2,"DNW (one) · NW/PW one well · not a DRC rule",7.5,"#0f766e",600)

def draw_array(name, x, y, color):
    a = A[name]
    fw, fh = a["fw"], a["fh"]
    cols, rows = a["cols"], a["rows"]
    m = next(d[3] for d in DEV if d[0] == name)
    # dummies at both ends: one per row
    for side in (-1, 1):
        for r in range(rows):
            dx = x + (side * fw) if side < 0 else x + a["bw"]
            rect(dx, y + r*fh, fw, fh, fill="#e2e8f0", stroke="#94a3b8", sw=0.45, dash="2 1")
            if r == 0:
                txt_um(dx + fw/2, y + r*fh + fh/2 + 0.4, "d", 6, "#64748b", 700, "middle")
    # active fingers
    for r in range(rows):
        for c in range(cols):
            idx = r * cols + c
            if idx >= m:
                break
            cx = x + c * fw
            cy = y + r * fh
            # cell / active area
            rect(cx, cy, fw, fh, fill="#ffffff", stroke=color, sw=0.45, opacity=0.55)
            # gate poly: vertical stripe of width L, height W
            gx = cx + (fw - a["fw"] * 0 + (fw - (a["fw"] - 0.8)) / 2)  # not used; keep centered
            # finger poly width = L (fw - 0.8), height = W (fh - 1.0)
            pw = fw - 0.8
            ph = fh - 1.0
            rect(cx + 0.4, cy + 0.5, pw, ph, fill=color, stroke="none", opacity=0.28)
            # source/drain rails
            line(cx + 0.1, cy + 0.2, cx + fw - 0.1, cy + 0.2, stroke=color, sw=0.45)
            line(cx + 0.1, cy + fh - 0.2, cx + fw - 0.1, cy + fh - 0.2, stroke=color, sw=0.45)
    # array border
    rect(x, y, a["bw"], a["bh"], fill="none", stroke=color, sw=0.9)
    # W/L dimension on first finger
    d0x, d0y = x + 0.4, y + 0.5
    pw, ph = a["fw"] - 0.8, a["fh"] - 1.0
    # W (vertical)
    line(d0x + pw + 0.25, d0y, d0x + pw + 0.25, d0y + ph, stroke="#0f172a", sw=0.5)
    line(d0x + pw + 0.15, d0y, d0x + pw + 0.35, d0y, stroke="#0f172a", sw=0.5)
    line(d0x + pw + 0.15, d0y + ph, d0x + pw + 0.35, d0y + ph, stroke="#0f172a", sw=0.5)
    txt_um(d0x + pw + 0.45, d0y + ph/2, f"W{int(ph)}", 5.5, "#0f172a", 600)
    # L (horizontal)
    line(d0x, d0y + ph + 0.25, d0x + pw, d0y + ph + 0.25, stroke="#0f172a", sw=0.5)
    line(d0x, d0y + ph + 0.15, d0x, d0y + ph + 0.35, stroke="#0f172a", sw=0.5)
    line(d0x + pw, d0y + ph + 0.15, d0x + pw, d0y + ph + 0.35, stroke="#0f172a", sw=0.5)
    txt_um(d0x + pw/2, d0y + ph + 0.75, f"L{int(pw)}", 5.5, "#0f172a", 600, "middle")

for g in GROUPS:
    gx, gy = POS[g]
    ow, oh = GO[g]
    color = next(d[5] for d in DEV if d[4] == g)
    rect(gx, gy, ow, oh, fill="none", stroke=color, sw=1.2, rx=1)
    rect(gx+RING_W, gy+RING_W, ow-2*RING_W, oh-2*RING_W, fill="none", stroke=color, sw=0.7, rx=1)
    cx = gx + RING_W + RING_GAP
    cy = gy + RING_W + RING_GAP
    for n in GL[g]["names"]:
        px, py = GL[g]["pos"][n]
        draw_array(n, cx + px, cy + py, next(d[5] for d in DEV if d[0] == n))
    txt_um(gx, gy - 1.0, {"IN_DP":"IN_DP","MIRROR_N":"MIRROR_N","FOLD_P":"FOLD_P",
                          "LOAD_P":"LOAD_P","BIAS_N":"BIAS_N","MIRROR_P":"MIRROR_P","OUT":"OUT"}[g], 7, color, 700)

# C1 / R1
c1x, c1y = C1
rect(c1x, c1y, 5, 10, fill="#ede9fe", stroke="#7c3aed", sw=1.0)
txt_um(c1x, c1y - 1.0, "C1_CC 5 pF MOM 5×10 µm", 6.5, "#5b21b6", 600)
r1x, r1y = R1
for i in range(4):
    rect(r1x + i*2.5, r1y, 2, 3, fill="#fef3c7", stroke="#b45309", sw=0.6)
txt_um(r1x, r1y - 1.0, "R1 4×(2×3) 3.33k", 6.5, "#92400e", 600)

# scale
line(0, layout_h + 10, 50, layout_h + 10, stroke="#0f172a", sw=2)
line(0, layout_h + 8, 0, layout_h + 12, stroke="#0f172a", sw=2)
line(50, layout_h + 8, 50, layout_h + 12, stroke="#0f172a", sw=2)
txt(X(25), Y(layout_h+10)+18, "50 µm", 8, "#0f172a", 600, "middle", "'DejaVu Sans Mono',monospace")
txt(X(0), Y(layout_h+10)+34, "scale bar · each finger is a vertical MOS stripe; S/D shared between adjacent fingers", 7.5, "#64748b", family="'DejaVu Sans Mono',monospace")

# legend right
lx = OX + layout_w*S + 24
ly = OY
txt(lx, ly, "LEGEND", 8.5, "#475569", 700, family="'DejaVu Sans Mono',monospace")
txt(lx, ly+16, "group   device  W/L  m", 7.5, "#64748b", family="'DejaVu Sans Mono',monospace")
ry = ly + 32
for g in GROUPS:
    color = next(d[5] for d in DEV if d[4] == g)
    txt(lx, ry, g, 7.5, color, 700, family="'DejaVu Sans Mono',monospace")
    ry += 12
    for n in GL[g]["names"]:
        w, l, m = next((d[1], d[2], d[3]) for d in DEV if d[0] == n)
        txt(lx+8, ry, f"{n:4s} {w}/{l}  m={m}", 7, "#334155", family="'DejaVu Sans Mono',monospace")
        ry += 10.5
    ry += 2
txt(lx, ry+8, "d = dummy finger (same W/L, S/D shared)", 7, "#64748b", family="'DejaVu Sans Mono',monospace")
txt(lx, ry+22, "ring 1.0 µm / gap 1.5 µm (edu)", 7, "#64748b", family="'DejaVu Sans Mono',monospace")
txt(lx, ry+36, "M13: PMOS current source; M14: output", 7, "#64748b", family="'DejaVu Sans Mono',monospace")

add('</svg>')
Path('examples/classa_opamp/white-line.svg').write_text('\n'.join(out), encoding='utf-8')
print('layout', layout_w, layout_h, 'canvas', W, H)
for n in ["M1","M3","M5","M6","M8","M11","M13","M14","M15","M16"]:
    print(n, A[n])
