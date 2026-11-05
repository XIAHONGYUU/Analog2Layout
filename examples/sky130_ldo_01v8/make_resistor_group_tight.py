#!/usr/bin/env python3
"""Tight stepped common resistor well: no rectangular padding between XR blocks."""
from html import escape
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
D=json.loads((ROOT/'examples/sky130_ldo_01v8/white-line-input.json').read_text())
R={p['name']:p for p in D['passives'] if p['type']=='resistor'}
# tight H: XR5 left; XR4 right top; XR6 directly below XR4, no block gap
blocks={'XR5':(0,0,20,15.30),'XR4':(20,0,20,7.65),'XR6':(20,7.65,10,3.40)}
GW,GH=40,15.30
# union outline of the three resistor blocks
union=[(0,0),(40,0),(40,7.65),(30,7.65),(30,11.05),(20,11.05),(20,15.30),(0,15.30)]
def txt(x,y,s,size=12,c='#0f172a',w=400,anchor='start',mono=False):
 fam="'DejaVu Sans Mono',monospace" if mono else "'DejaVu Sans',sans-serif"
 return f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" font-weight="{w}" fill="{c}" text-anchor="{anchor}">{escape(str(s))}</text>'
def rect(x,y,w,h,fill='none',stroke='#0f172a',sw=1,rx=0,dash=None):
 d=f' stroke-dasharray="{dash}"' if dash else ''
 return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'
W,H=1300,760;S=min(1000/GW,520/GH);ox=(W-GW*S)/2;oy=150
def X(x): return ox+x*S
def Y(y): return oy+y*S
out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',rect(0,0,W,H,'#f8fafc','none',0)]
out.append(txt(28,36,'XR4/XR5/XR6 — tight stepped common well',22,'#0f172a',700))
out.append(txt(28,58,'blocks touch; stepped well outline removes rectangular padding; dummy only at two outer ends',9,'#475569',mono=True))
out.append(txt(28,76,'structure only · no DRC/LVS · no resistor end metal',8,'#b91c1c',mono=True))
# thick ring/well outline: draw union fill then a thick stroke approximates gap+ring
pts=' '.join(f'{X(x):.1f},{Y(y):.1f}' for x,y in union)
out.append(f'<polygon points="{pts}" fill="#fff7ed" stroke="#b45309" stroke-width="{3.6*S/40:.1f}" stroke-linejoin="round"/>')
out.append(f'<polygon points="{pts}" fill="none" stroke="#b45309" stroke-width="1.0" stroke-linejoin="round"/>')
# resistor cells tight, no individual rings
for name,(x0,y0,bw,bh) in blocks.items():
 p=R[name];arr=p['array'];cols=arr['cols'];active=arr['active_cells'];rows=(active+cols-1)//cols
 out.append(rect(X(x0),Y(y0),bw*S,bh*S,'none','#d97706',.35,0,dash='3 2'))
 out.append(txt(X(x0+1),Y(y0+4),name,7,'#92400e',700,mono=True))
 cellw=bw/cols;rowh=bh/rows;pos=set([(r,c) for r in range(rows) for c in range(cols)][:active])
 for r in range(rows):
  for c in range(cols):
   if (r,c) not in pos: continue
   x=x0+c*cellw;y=y0+r*rowh
   sw=min(arr['segment_length_um'],cellw*.92);sh=arr['segment_width_um']
   out.append(rect(X(x+(cellw-sw)/2),Y(y+(rowh-sh)/2),sw*S,max(sh*S,2),'#fef08a','#b45309',.4,1))
# two outer end dummies
for xx in (-1.6,GW+.6):
 out.append(rect(X(xx),Y(GH/2-.35),.35*S,.70*S,'#e2e8f0','#94a3b8',.6,1))
 out.append(txt(X(xx+.17),Y(GH/2-.55),'DM',5,'#64748b',700,'middle',True))
out.append(txt(28,H-40,'No internal rectangular padding; no individual XR rings; no metal.',8,'#64748b',mono=True))
out.append('</svg>')
(ROOT/'examples/sky130_ldo_01v8/passive-banks/XR_GROUP_TIGHT.svg').write_text('\n'.join(out),encoding='utf-8')
json.dump({'name':'XR_GROUP_TIGHT','blocks':blocks,'bbox_um':[GW,GH],'union_outline':union,
           'dummy':'one at each outer end'},open(ROOT/'examples/sky130_ldo_01v8/passive-banks/XR_GROUP_TIGHT.json','w'),indent=2)
print('wrote')
