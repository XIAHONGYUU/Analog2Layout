#!/usr/bin/env python3
"""Resistor group with long-edge dummies and explicit AA/field separation."""
from html import escape
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
D=json.loads((ROOT/'examples/sky130_ldo_01v8/white-line-input.json').read_text())
R={p['name']:p for p in D['passives'] if p['type']=='resistor'}
RING=1.0; GAP=.8; DM_GAP=.5; DM_W=.35
# side-by-side active blocks; common well; dummies above/below long edges
blocks={
 'XR5':{'x':0,'y':2.0,'w':20,'h':15.30},
 'XR4':{'x':21,'y':2.0,'w':20,'h':7.65},
 'XR6':{'x':42,'y':2.0,'w':10,'h':3.40},
}
GW=52.0; GH=17.30
def txt(x,y,s,size=12,c='#0f172a',w=400,anchor='start',mono=False):
 fam="'DejaVu Sans Mono',monospace" if mono else "'DejaVu Sans',sans-serif"
 return f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" font-weight="{w}" fill="{c}" text-anchor="{anchor}">{escape(str(s))}</text>'
def rect(x,y,w,h,fill='none',stroke='#0f172a',sw=1,rx=0,dash=None):
 d=f' stroke-dasharray="{dash}"' if dash else ''
 return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'
W,H=1500,780;S=min(1200/GW,540/GH);ox=(W-GW*S)/2;oy=150
def X(x): return ox+x*S
def Y(y): return oy+y*S
out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',rect(0,0,W,H,'#f8fafc','none',0)]
out.append(txt(28,36,'XR4/XR5/XR6 — long-edge dummies, one common well',22,'#0f172a',700))
out.append(txt(28,58,'dummy strips run along the 10 µm long edge, same orientation; no AA under resistor body',9,'#475569',mono=True))
out.append(txt(28,76,'AA/tap only at perimeter · structure only · no DRC/LVS',8,'#b91c1c',mono=True))
# common well/ring
out.append(rect(X(0),Y(0),(GW+2*(GAP+RING))*S,(GH+2*(GAP+RING))*S,'#fef3c7','#b45309',1.2,2))
out.append(rect(X(RING),Y(RING),(GW+2*GAP)*S,(GH+2*GAP)*S,'#fff7ed','#b45309',.5,1))
# field core
out.append(rect(X(RING+GAP),Y(RING+GAP),GW*S,GH*S,'#fff7ed','#d97706',.4,0))
# explicit AA/tap ring at perimeter only (no AA under R)
aa=0.4
out.append(rect(X(RING+GAP-aa),Y(RING+GAP-aa),(GW+2*aa)*S,(GH+2*aa)*S,'none','#16a34a',3.0,0))
# resistors
for name,b in blocks.items():
 p=R[name];arr=p['array'];cols=arr['cols'];active=arr['active_cells'];rows=(active+cols-1)//cols
 x0,y0=b['x'],b['y'];bw,bh=b['w'],b['h']
 out.append(txt(X(x0+1),Y(y0-0.45),name,7,'#92400e',700,mono=True))
 # dummy long-edge strips: full block width above and below, same horizontal orientation
 for dy in (-DM_GAP-DM_W, bh+DM_GAP):
  out.append(rect(X(x0),Y(y0+dy),bw*S,max(DM_W*S,3),'#e2e8f0','#94a3b8',.6,1))
 out.append(rect(X(x0),Y(y0),bw*S,bh*S,'none','#d97706',.3,0,dash='3 2'))
 cellw=bw/cols;rowh=bh/rows
 for r in range(rows):
  for c in range(cols):
   if r*cols+c>=active: continue
   x=x0+c*cellw;y=y0+r*rowh
   sw=min(arr['segment_length_um'],cellw*.92);sh=arr['segment_width_um']
   out.append(rect(X(x+(cellw-sw)/2),Y(y+(rowh-sh)/2),sw*S,max(sh*S,2),'#fef08a','#b45309',.4,1))
out.append(txt(28,H-40,'field/well background; AA/tap ring only at perimeter; dummy strips above/below long edges; no metal.',8,'#64748b',mono=True))
out.append('</svg>')
(ROOT/'examples/sky130_ldo_01v8/passive-banks/XR_GROUP_LONG.svg').write_text('\n'.join(out),encoding='utf-8')
json.dump({'name':'XR_GROUP_LONG','group_um':[GW,GH],'blocks':blocks,'dummy':'one long-edge strip above and below each resistor',
           'aa':'perimeter ring only; no AA under resistor'},open(ROOT/'examples/sky130_ldo_01v8/passive-banks/XR_GROUP_LONG.json','w'),indent=2)
print('wrote')
