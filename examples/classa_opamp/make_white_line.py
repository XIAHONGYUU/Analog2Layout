from html import escape
from math import ceil
from pathlib import Path

# name, W unit, L, m, group, role, color
DEV = [
    ("M1", 10, 4, 8, "IN_DP", "input pair", "#0ea5e9"),
    ("M2", 10, 4, 8, "IN_DP", "input pair", "#0ea5e9"),
    ("M3", 8, 1, 8, "LOAD_P", "PMOS load", "#f59e0b"),
    ("M4", 8, 1, 8, "LOAD_P", "PMOS load", "#f59e0b"),
    ("M15", 8, 1, 16, "LOAD_P", "PMOS ref", "#f59e0b"),
    ("M16", 2, 2, 81, "BIAS_N", "NMOS ref", "#10b981"),
    ("M5", 2, 2, 81, "BIAS_N", "tail", "#10b981"),
    ("M10", 2, 2, 97, "BIAS_N", "bias", "#10b981"),
    ("M8", 9, 2, 12, "MIRROR_N", "NMOS mirror", "#8b5cf6"),
    ("M9", 9, 2, 12, "MIRROR_N", "NMOS mirror", "#8b5cf6"),
    ("M6", 12, 2, 20, "FOLD_P", "common-gate", "#f97316"),
    ("M7", 12, 2, 20, "FOLD_P", "common-gate", "#f97316"),
    ("M11", 8, 1, 30, "MIRROR_P", "PMOS bias", "#ef4444"),
    ("M12", 8, 1, 30, "MIRROR_P", "PMOS bias", "#ef4444"),
    ("M13", 8, 1, 80, "MIRROR_P", "PMOS current source", "#ef4444"),
    ("M14", 18, 1, 100, "OUT", "NMOS output", "#db2777"),
]
GROUPS = ["IN_DP", "MIRROR_N", "FOLD_P", "LOAD_P", "BIAS_N", "MIRROR_P", "OUT"]

MAX_ROW = 100.0
ROW_GAP = 1.0
SDO = 1.0  # source/drain/contact allowance per cell
RING_W = 1.0
RING_GAP = 1.5
SCALE = 3.0
OX, OY = 80.0, 160.0

def fold(w, l, m):
    cols = max(1, int(MAX_ROW // w))
    rows = max(1, ceil(m / cols))
    used_cols = min(cols, m)
    bw = used_cols * w
    bh = rows * (l + SDO) + (rows - 1) * ROW_GAP
    return bw, bh, cols, rows

BLOCKS = {}
for name, w, l, m, group, role, color in DEV:
    bw, bh, cols, rows = fold(w, l, m)
    BLOCKS[name] = dict(w=w, l=l, m=m, group=group, role=role, color=color,
                        bw=bw, bh=bh, cols=cols, rows=rows)

def group_layout(g):
    ds = [d for d in DEV if d[4] == g]
    if g == "MIRROR_P":
        # M11/M12 side by side, M13 below
        top = ["M11", "M12"]
        top_w = sum(BLOCKS[n]["bw"] for n in top) + 2.0 * (len(top) - 1)
        top_h = max(BLOCKS[n]["bh"] for n in top)
        bottom = "M13"
        cw = max(top_w, BLOCKS[bottom]["bw"])
        ch = top_h + 2.0 + BLOCKS[bottom]["bh"]
        return dict(devs=top + [bottom], cw=cw, ch=ch,
                    pos={"M11": (0, 0), "M12": (BLOCKS["M11"]["bw"] + 2.0, 0),
                         "M13": (0, top_h + 2.0)})
    if g == "OUT":
        n = "M14"
        return dict(devs=[n], cw=BLOCKS[n]["bw"], ch=BLOCKS[n]["bh"],
                    pos={n: (0, 0)})
    # row layout
    cw = sum(BLOCKS[d[0]]["bw"] for d in ds) + 2.0 * (len(ds) - 1)
    ch = max(BLOCKS[d[0]]["bh"] for d in ds)
    pos = {}
    x = 0.0
    for d in ds:
        n = d[0]
        pos[n] = (x, ch - BLOCKS[n]["bh"])  # bottom aligned
        x += BLOCKS[n]["bw"] + 2.0
    return dict(devs=[d[0] for d in ds], cw=cw, ch=ch, pos=pos)

GL = {g: group_layout(g) for g in GROUPS}

def group_dims(g):
    gl = GL[g]
    ds = [BLOCKS[n] for n in gl["devs"]]
    # dummies use the first device's unit W/L
    dw, dl = ds[0]["w"], ds[0]["l"]
    content_w = gl["cw"] + 2 * dw
    content_h = max(gl["ch"], dl + SDO)
    outer_w = content_w + 2 * (RING_GAP + RING_W)
    outer_h = content_h + 2 * (RING_GAP + RING_W)
    return dict(dw=dw, dl=dl, content_w=content_w, content_h=content_h,
                outer_w=outer_w, outer_h=outer_h)

GD = {g: group_dims(g) for g in GROUPS}

# layout positions (group bbox origin)
POS = {
    "IN_DP": (0, 0),
    "MIRROR_N": (0, GD["IN_DP"]["outer_h"] + 6),
    "FOLD_P": (0, GD["IN_DP"]["outer_h"] + GD["MIRROR_N"]["outer_h"] + 12),
    "LOAD_P": (0, GD["IN_DP"]["outer_h"] + GD["MIRROR_N"]["outer_h"] + GD["FOLD_P"]["outer_h"] + 18),
}
left_w = max(GD[g]["outer_w"] for g in ["IN_DP", "MIRROR_N", "FOLD_P", "LOAD_P"])
RX = left_w + 18
POS["BIAS_N"] = (RX, 0)
POS["MIRROR_P"] = (RX, GD["BIAS_N"]["outer_h"] + 6)
POS["OUT"] = (RX, GD["BIAS_N"]["outer_h"] + GD["MIRROR_P"]["outer_h"] + 12)

# C1 and R1 below OUT
C1 = (RX + 2, POS["OUT"][1] + GD["OUT"]["outer_h"] + 10)
R1 = (RX + 2, C1[1] + 16)

layout_w = max(left_w, RX + GD["BIAS_N"]["outer_w"],
               RX + GD["MIRROR_P"]["outer_w"],
               RX + GD["OUT"]["outer_w"],
               C1[0] + 5, R1[0] + 9.5)
layout_h = max(POS["LOAD_P"][1] + GD["LOAD_P"]["outer_h"],
               R1[1] + 6)

W = int(OX + layout_w * SCALE + 500)
H = int(OY + layout_h * SCALE + 170)
out = []
def add(s): out.append(s)
def X(x): return OX + x * SCALE
def Y(y): return OY + y * SCALE
def rect(x,y,w,h,fill="none",stroke="#0f172a",sw=1.2,rx=0,dash=None,opacity=1):
    d=f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<rect x="{X(x):.1f}" y="{Y(y):.1f}" width="{w*SCALE:.1f}" height="{h*SCALE:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}"{d}/>')
def line(x1,y1,x2,y2,stroke="#0f172a",sw=1.0,dash=None):
    d=f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<line x1="{X(x1):.1f}" y1="{Y(y1):.1f}" x2="{X(x2):.1f}" y2="{Y(y2):.1f}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round"{d}/>')
def txt(x,y,s,size=12,fill="#0f172a",weight=400,anchor="start",family="'DejaVu Sans',sans-serif"):
    add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escape(s)}</text>')
def txt_um(x,y,s,size=9,fill="#0f172a",weight=400,anchor="start",family="'DejaVu Sans Mono',monospace"):
    txt(X(x), Y(y), s, size, fill, weight, anchor, family)

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="class-A op-amp white-line layout plan">')
rect(-1000,-1000,5000,5000,fill="#f8fafc",stroke="none")
txt(40,40,"Class-A CMOS OP — white-line layout plan (strict scale)",26,"#0f172a",700)
txt(40,66,"W/L in µm · m = parallel units · dummies at group W ends · one ring per matched group · one DNW",11,"#475569")
txt(40,84,"intent only; not DRC/LVS/PEX · M13 is PMOS current-source load; M14 is the only signal output",9,"#64748b",family="'DejaVu Sans Mono',monospace")

# DNW outline around all layout
rect(-4,-4,layout_w+8,layout_h+8,fill="none",stroke="#0f766e",sw=1.4,rx=3,dash="8 4")
txt_um(-3,layout_h+1,"DNW (one) · NW/PW one well · not a DRC rule",8,"#0f766e",600)

for g in GROUPS:
    gx, gy = POS[g]
    gd = GD[g]
    color = BLOCKS[GL[g]["devs"][0]]["color"]
    # outer/inner ring
    rect(gx,gy,gd["outer_w"],gd["outer_h"],fill="none",stroke=color,sw=1.4,rx=1)
    rect(gx+RING_W,gy+RING_W,gd["outer_w"]-2*RING_W,gd["outer_h"]-2*RING_W,fill="none",stroke=color,sw=1.0,rx=1)
    # content origin inside ring gap
    cx = gx + RING_W + RING_GAP
    cy = gy + RING_W + RING_GAP
    # dummies
    dw, dl = gd["dw"], gd["dl"]
    rect(cx,cy+gd["content_h"]-dl-SDO,dw,dl+SDO,fill="#e2e8f0",stroke="#64748b",sw=0.8,dash="3 2")
    rect(cx+gd["content_w"]-dw,cy+gd["content_h"]-dl-SDO,dw,dl+SDO,fill="#e2e8f0",stroke="#64748b",sw=0.8,dash="3 2")
    txt_um(cx+dw/2,cy+gd["content_h"]-0.4,"d",7,"#475569",700,"middle")
    txt_um(cx+gd["content_w"]-dw/2,cy+gd["content_h"]-0.4,"d",7,"#475569",700,"middle")
    # devices (shift content by left dummy width)
    gl = GL[g]
    for n in gl["devs"]:
        b = BLOCKS[n]
        px, py = gl["pos"][n]
        x = cx + dw + px
        y = cy + (gl["ch"] - b["bh"]) + py  # careful: py already includes bottom align
        # draw block
        rect(x,y,b["bw"],b["bh"],fill="none",stroke=b["color"],sw=1.2,rx=0.8)
        # row separators
        cell_h = b["l"] + SDO
        for r in range(1,b["rows"]):
            line(x,y+r*cell_h+(r-1)*ROW_GAP,x+b["bw"],y+r*cell_h+(r-1)*ROW_GAP,stroke=b["color"],sw=0.5,dash="2 2")
        # label inside/above
        label=f"{n} m={b['m']}"
        sub=f"W={b['w']} L={b['l']}"
        txt_um(x+b["bw"]/2,y+b["bh"]/2-0.5,label,7.5,b["color"],700,"middle")
        txt_um(x+b["bw"]/2,y+b["bh"]/2+1.2,sub,6.5,"#475569",400,"middle")
    # group label
    txt_um(gx,gy-1.2,g.replace("_"," "),8,color,700)

# C1 / R1
c1x,c1y=C1
rect(c1x,c1y,5,10,fill="#ede9fe",stroke="#7c3aed",sw=1.2)
txt_um(c1x,c1y-1.0,"C1_CC 5 pF MOM 5×10 µm",7,"#5b21b6",600)
r1x,r1y=R1
# 4 parallel resistor units 2 x 3, pitch 2.5
for i in range(4):
    rect(r1x+i*2.5,r1y,2,3,fill="#fef3c7",stroke="#b45309",sw=0.8)
txt_um(r1x,r1y-1.0,"R1 4× (2×3) 3.33k",7,"#92400e",600)

# scale bar and dims
sx=OX; sy=Y(layout_h)+55
line(0,layout_h+12,50,layout_h+12,stroke="#0f172a",sw=2)
line(0,layout_h+10,0,layout_h+14,stroke="#0f172a",sw=2)
line(50,layout_h+10,50,layout_h+14,stroke="#0f172a",sw=2)
txt(sx+50*SCALE/2,sy+18,"50 µm",9,"#0f172a",600,"middle","'DejaVu Sans Mono',monospace")
txt(sx,sy+34,"scale bar · device blocks are folded arrays of m parallel units",8,"#64748b",family="'DejaVu Sans Mono',monospace")

# legend right
lx=OX+layout_w*SCALE+30; ly=OY
txt(lx,ly,"LEGEND",9,"#475569",700,family="'DejaVu Sans Mono',monospace")
txt(lx,ly+18,"group   device  W/L  m",8,"#64748b",family="'DejaVu Sans Mono',monospace")
ry=ly+36
for g in GROUPS:
    txt(lx,ry,g,8,BLOCKS[GL[g]["devs"][0]]["color"],700,family="'DejaVu Sans Mono',monospace")
    ry+=14
    for n in GL[g]["devs"]:
        b=BLOCKS[n]
        txt(lx+10,ry,f"{n:4s} {b['w']}/{b['l']}  m={b['m']}",7.5,"#334155",family="'DejaVu Sans Mono',monospace")
        ry+=12
    ry+=2
txt(lx,ry+8,"C1_CC 5pF MOM 5×10 µm",7.5,"#5b21b6",600,family="'DejaVu Sans Mono',monospace")
txt(lx,ry+22,"R1 3.33k w=2 L=3 m=4",7.5,"#92400e",600,family="'DejaVu Sans Mono',monospace")
txt(lx,ry+40,"d = dummy (same W/L, S/D shared)",7.5,"#64748b",family="'DejaVu Sans Mono',monospace")
txt(lx,ry+54,"ring 1.0 µm / gap 1.5 µm (edu)",7.5,"#64748b",family="'DejaVu Sans Mono',monospace")

add('</svg>')
Path('examples/classa_opamp/white-line.svg').write_text('\n'.join(out),encoding='utf-8')
print('layout_w,h',layout_w,layout_h,'canvas',W,H)
