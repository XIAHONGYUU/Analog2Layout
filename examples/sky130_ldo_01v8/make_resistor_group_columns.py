#!/usr/bin/env python3
"""Common resistor well with per-column dummies (owner-selected scope).

One dummy segment per active column, same orientation and immediately adjacent
to that column. XR4/XR5 have 2 columns; XR6 has 1. Structure only.
"""
from html import escape
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
D=json.loads((ROOT/'examples/sky130_ldo_01v8/white-line-input.json').read_text())
R={p['name']:p for p in D['passives'] if p['type']=='resistor'}
RING=1.0; GAP=.8
# vertical stack; active width 20 (XR4/5) or 10 (XR6); dummies outside columns
# group x: dummy-left 0..10, active 10..30, dummy-right 30..40
blocks={
 'XR5':{'x':10,'y':0,'w':20,'h':15.30,'dummy_cols':[('L',0,10),('R',30,10)]},
 'XR4':{'x':10,'y':15.30,'w':20,'h':7.65,'dummy_cols':[('L',0,10),('R',30,10)]},
 'XR6':{'x':10,'y':22.95,'w':10,'h':3.40,'dummy_cols':[('L',0,10)]},
}
GW,GH=40,26.35
def txt(x,y,s,size=12,c='#0f172a',w=400,anchor='start',mono=False):
 fam="'DejaVu Sans Mono',monospace" if mono else "'DejaVu Sans',sans-serif"
 return f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" font-weight="{w}" fill="{c}" text-anchor="{anchor}">{escape(str(s))}</text>'
def rect(x,y,w,h,fill='none',stroke='#0f172a',sw=1,rx=0,dash=None):
 d=f' stroke-dasharray="{dash}"' if dash else ''
 return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'
W,H=1300,900;S=min(1000/GW,600/GH);ox=(W-GW*S)/2;oy=150
def X(x): return ox+x*S
def Y(y): return oy+y*S
out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',rect(0,0,W,H,'#f8fafc','none',0)]
out.append(txt(28,36,'XR4/XR5/XR6 — per-column dummies in one common well',22,'#0f172a',700))
out.append(txt(28,58,'one dummy segment per active column · same horizontal orientation · adjacent to column · structure only',9,'#475569',mono=True))
out.append(txt(28,76,f'group {GW:.2f}×{GH:.2f} · outer {GW+2*(GAP+RING):.2f}×{GH+2*(GAP+RING):.2f} · full dummy columns: 2+2+1 · no DRC',8,'#b91c1c',mono=True))
# common well/ring
out.append(rect(X(0),Y(0),(GW+2*(GAP+RING))*S,(GH+2*(GAP+RING))*S,'#fef3c7','#b45309',1.2,2))
out.append(rect(X(RING),Y(RING),(GW+2*GAP)*S,(GH+2*GAP)*S,'#fff7ed','#b45309',.5,1))
out.append(rect(X(RING+GAP),Y(RING+GAP),GW*S,GH*S,'#fff7ed','#d97706',.5,0))
for name,b in blocks.items():
 p=R[name];arr=p['array'];cols=arr['cols'];active=arr['active_cells'];rows=(active+cols-1)//cols
 out.append(rect(X(b['x']),Y(b['y']),b['w']*S,b['h']*S,'none','#d97706',.35,0,dash='3 2'))
 out.append(txt(X(b['x']+1),Y(b['y']+4),name,7,'#92400e',700,mono=True))
 cellw=b['w']/cols;rowh=b['h']/rows
 for r in range(rows):
  for c in range(cols):
   if r*cols+c>=active: continue
   x=b['x']+c*cellw;y=b['y']+r*rowh
   sw=min(arr['segment_length_um'],cellw*.92);sh=arr['segment_width_um']
   out.append(rect(X(x+(cellw-sw)/2),Y(y+(rowh-sh)/2),sw*S,max(sh*S,2),'#fef08a','#b45309',.4,1))
 # full per-column dummy columns: same row count/orientation as active column
 for side,dx,dw in b['dummy_cols']:
  for rr in range(rows):
   yy=b['y']+rr*rowh+(rowh-arr['segment_width_um'])/2
   out.append(rect(X(dx),Y(yy),dw*S,max(arr['segment_width_um']*S,2),'#e2e8f0','#94a3b8',.5,1))
  out.append(txt(X(dx+dw/2),Y(b['y']-0.15),f'DM-{side}',5,'#64748b',700,'middle',True))
out.append(txt(28,H-40,'Dummy is same 10×0.35 horizontal segment as active column; no individual XR rings; no metal.',8,'#64748b',mono=True))
out.append('</svg>')
(ROOT/'examples/sky130_ldo_01v8/passive-banks/XR_GROUP_COLUMNS.svg').write_text('\n'.join(out),encoding='utf-8')
json.dump({'name':'XR_GROUP_COLUMNS','group_um':[GW,GH],'dummy_count':'full columns: XR5 2, XR4 2, XR6 1', 'dummy_scope':'one full dummy column per active column',
           'blocks':blocks},open(ROOT/'examples/sky130_ldo_01v8/passive-banks/XR_GROUP_COLUMNS.json','w'),indent=2)
print('wrote')
