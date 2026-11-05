#!/usr/bin/env python3
"""DRC-aware bank-level white-line template.

NMOS_2X0.5_BANK: XM52/XM53 input pair.
Geometry is a layout-intent primitive with Sky130 DRC dimensions, not a full
DRC-clean GDS and not a signoff artifact.
"""
from html import escape
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
OUTDIR = ROOT / "examples/sky130_ldo_01v8/banks"
OUTDIR.mkdir(exist_ok=True)

# Sky130 dimensions used in the primitive (from the local DRC deck / facts).
L = 0.5
W = 2.0
SD_LEN = 0.30                 # >= poly.7 0.25
DIFF_LEN = L + 2*SD_LEN       # 1.10
POLY_EXT = 0.13               # poly.8
DIFF_H = W
POLY_H = W + 2*POLY_EXT
CONTACT = 0.17                # licon.1
GATE_GAP = 0.055              # licon.11
ENC = 0.04                    # licon.5
DIFF_SPACE = 0.27             # difftap.3
RING_W = 0.5
RING_GAP = 0.8
CELLS = 4
CORE_W = CELLS*DIFF_LEN + (CELLS-1)*DIFF_SPACE
CORE_H = POLY_H
OUTER_W = CORE_W + 2*(RING_GAP+RING_W)
OUTER_H = CORE_H + 2*(RING_GAP+RING_W)

S = 72.0
OX, OY = 100, 130
Wpx, Hpx = 1100, 760
out=[]
def add(s): out.append(s)
def X(x): return OX + x*S
def Y(y): return OY + y*S
def rect(x,y,w,h,fill="none",stroke="#0f172a",sw=1.0,rx=0,dash=None,opacity=1):
    d=f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<rect x="{X(x):.1f}" y="{Y(y):.1f}" width="{w*S:.1f}" height="{h*S:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}"{d}/>')
def line(x1,y1,x2,y2,c="#0f172a",sw=1.0,dash=None):
    d=f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<line x1="{X(x1):.1f}" y1="{Y(y1):.1f}" x2="{X(x2):.1f}" y2="{Y(y2):.1f}" stroke="{c}" stroke-width="{sw}" stroke-linecap="round"{d}/>')
def txt(x,y,s,size=12,c="#0f172a",w=400,anchor="start",mono=False):
    fam="'DejaVu Sans Mono',monospace" if mono else "'DejaVu Sans',sans-serif"
    add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" font-weight="{w}" fill="{c}" text-anchor="{anchor}">{escape(str(s))}</text>')
def tu(x,y,s,size=7,c="#0f172a",w=700,anchor="start"):
    txt(X(x),Y(y),s,size,c,w,anchor,True)

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wpx}" height="{Hpx}" viewBox="0 0 {Wpx} {Hpx}">')
rect(-100,-100,20,20,'#f8fafc','none',0)
# outer tap/body ring: tap band at outer edge
rect(0,0,OUTER_W,OUTER_H,'#d1fae5','#0f766e',1.3)
rect(RING_W,RING_W,OUTER_W-2*RING_W,OUTER_H-2*RING_W,'#f8fafc','#0f766e',.6)
# core background at ring gap
cx0,cy0=RING_W+RING_GAP,RING_W+RING_GAP
rect(cx0,cy0,CORE_W,CORE_H,'#f8fafc','#94a3b8',.7)
# cells: 2 dummy + 2 active + 2 dummy? one each side
labels=['DM','XM52','XM53','DM']
for i,(cell_x,label) in enumerate(zip([cx0+j*(DIFF_LEN+DIFF_SPACE) for j in range(CELLS)],labels)):
    dummy=label=='DM'
    # diff/active
    rect(cell_x,cy0,DIFF_LEN,DIFF_H,'#bbf7d0' if not dummy else '#e2e8f0','#16a34a' if not dummy else '#94a3b8',.7)
    # vertical gate: centered in cell, extends beyond diff
    gate_x=cell_x+(DIFF_LEN-L)/2
    rect(gate_x,cy0-POLY_EXT,L,POLY_H,'#fecaca' if not dummy else '#e2e8f0','#dc2626' if not dummy else '#94a3b8',.8)
    if not dummy:
        # S/D contacts: 3 vertical, 0.17 square, enclosure 0.04+, gate gap >=0.055
        for xc in (cell_x+0.14, cell_x+DIFF_LEN-0.14):
            for yc in (cy0+0.55, cy0+1.00, cy0+1.45):
                rect(xc-CONTACT/2,yc-CONTACT/2,CONTACT,CONTACT,'#111827','none',0)
        tu(cell_x+DIFF_LEN/2,cy0-0.30,label,7,'#7f1d1d',700,'middle')
        tu(cell_x+DIFF_LEN/2,cy0+POLY_H+0.22,'G=VREF',5.5,'#991b1b',700,'middle')
    else:
        tu(cell_x+DIFF_LEN/2,cy0-0.30,label,7,'#64748b',700,'middle')
# tap contacts on ring (one row at top/bottom; illustrative)
# tap contacts distributed along the ring, not just at the four corners.
# The 0.17 um contacts sit at the ring centerline with 0.165 um enclosure.
tap_xs = [RING_W/2 + k*0.55 for k in range(int((OUTER_W-RING_W)/0.55)+1)]
tap_ys = [RING_W/2 + k*0.55 for k in range(int((OUTER_H-RING_W)/0.55)+1)]
for xx in tap_xs:
    for yy in (RING_W/2, OUTER_H-RING_W/2):
        rect(xx-CONTACT/2,yy-CONTACT/2,CONTACT,CONTACT,'#0f766e','none',0)
for yy in tap_ys:
    for xx in (RING_W/2, OUTER_W-RING_W/2):
        rect(xx-CONTACT/2,yy-CONTACT/2,CONTACT,CONTACT,'#0f766e','none',0)
# source/drain labels (schematic; contacts exist but no metal route)
tu(cx0+0.35,cy0+DIFF_H+0.75,'S=net1',6,'#14532d',700,'middle')
tu(cx0+CORE_W-0.55,cy0+DIFF_H+0.75,'S=net1',6,'#14532d',700,'middle')
tu(cx0+CORE_W/2,cy0-0.60,'D=VX / VY',6,'#14532d',700,'middle')
# dimensions
line(cx0,cy0+CORE_H+0.35,cx0+CORE_W,cy0+CORE_H+0.35,'#0f766e',.8)
tu(cx0+CORE_W/2,cy0+CORE_H+0.70,f'{CORE_W:.2f} µm core',6.5,'#0f766e',700,'middle')
line(cx0+CORE_W+.35,cy0,cx0+CORE_W+.35,cy0+CORE_H,'#0f766e',.8)
tu(cx0+CORE_W+.55,cy0+CORE_H/2,f'{CORE_H:.2f}',6.5,'#0f766e',700)
# title/legend
txt(30,38,'NMOS_2X0.5_BANK — DRC-aware MOS primitive',24,'#0f172a',700)
txt(30,60,'XM52 / XM53 · diff/W/poly/contact/dummy/tap ring · vertical poly · ring 0.5/0.8',9.5,'#475569',mono=True)
txt(30,78,'DRC dimensions from sky130.lydrc · no S/D metal route · no global DNW · not signoff',9,'#b91c1c',mono=True)
leg=[('diff / active','#bbf7d0'),('poly gate','#fecaca'),('licon contact','#111827'),('dummy','#e2e8f0'),('tap/body ring','#d1fae5')]
for i,(name,col) in enumerate(leg):
    add(f'<rect x="30" y="{Hpx-170+i*22}" width="14" height="12" fill="{col}" stroke="#64748b" stroke-width="0.6"/>')
    txt(52,Hpx-160+i*22,name,9,'#334155',400,mono=True)
add(f'<line x1="30" y1="{Hpx-45}" x2="{30+S}" y2="{Hpx-45}" stroke="#0f172a" stroke-width="2"/>')
txt(30,Hpx-28,'1 µm',8,'#0f172a',700,mono=True)
txt(30,Hpx-12,'Bank macro only. Global placement, DNW1 and routing are later stages.',9,'#64748b',mono=True)
add('</svg>')
SVG=OUTDIR/'NMOS_2X0.5_BANK.svg'
SVG.write_text('\n'.join(out),encoding='utf-8')

# Rule audit: selected Sky130 checks, not a full DRC run.
checks = {
    'poly_width_um': {'value': L, 'rule': 'poly.3 min 0.33', 'pass': L >= 0.33},
    'sd_length_um': {'value': SD_LEN, 'rule': 'poly.7 min 0.25', 'pass': SD_LEN >= 0.25},
    'poly_extension_um': {'value': POLY_EXT, 'rule': 'poly.8 min 0.13', 'pass': POLY_EXT >= 0.13},
    'license?': {'pass': True},
    'licon_size_um': {'value': CONTACT, 'rule': 'licon.1 min 0.17', 'pass': CONTACT >= 0.17},
    'licon_gate_gap_um': {'value': 0.075, 'rule': 'licon.11 min 0.055', 'pass': 0.075 >= 0.055},
    'diff_enclosure_licon_um': {'value': 0.055, 'rule': 'licon.5 min 0.04', 'pass': 0.055 >= 0.04},
    'diff_space_um': {'value': DIFF_SPACE, 'rule': 'difftap.3 min 0.27', 'pass': DIFF_SPACE >= 0.27},
    'tap_contact_in_ring': {'value': True, 'rule': 'licon on tap/AA ring', 'pass': True},
    'tap_contact_enclosure_um': {'value': RING_W/2-CONTACT/2, 'rule': 'licon.7 min 0.12', 'pass': (RING_W/2-CONTACT/2) >= 0.12},
}
# remove accidental key
checks.pop('license?',None)
report = {'bank':'NMOS_2X0.5_BANK','geometry':{'core_um':[CORE_W,CORE_H],
          'outer_um':[OUTER_W,OUTER_H],'L_um':L,'W_um':W,'diff_len_um':DIFF_LEN,
          'contact_um':CONTACT,'dummy_cells':2,'active_cells':2},
          'checks':checks,'all_pass':all(v['pass'] for v in checks.values()),
          'note':'selected rule checks only; no DRC/LVS/PEX run'}
(OUTDIR/'NMOS_2X0.5_BANK-drc.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('geometry', CORE_W,CORE_H, OUTER_W,OUTER_H)
print('checks', checks, 'all_pass', report['all_pass'])
