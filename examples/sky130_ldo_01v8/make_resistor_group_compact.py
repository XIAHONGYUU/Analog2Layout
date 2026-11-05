#!/usr/bin/env python3
"""Compact common resistor well: horizontal-fill vs vertical-stack."""
from html import escape
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
D=json.loads((ROOT/'examples/sky130_ldo_01v8/white-line-input.json').read_text())
R={p['name']:p for p in D['passives'] if p['type']=='resistor'}
RING=1.0; GAP=.8
# no internal 2 um gap; right column abuts XR5 / XR6
layouts=[
 ('compact-H',{'XR5':(0,0,20,20.75),'XR4':(20,0,20,10.55),'XR6':(20,10.55,10,7.15)},40,20.75),
 ('compact-V',{'XR5':(0,0,20,20.75),'XR4':(0,20.75,20,10.55),'XR6':(0,31.30,10,7.15)},20,38.45),
]
def txt(x,y,s,size=12,c='#0f172a',w=400,anchor='start',mono=False):
 fam="'DejaVu Sans Mono',monospace" if mono else "'DejaVu Sans',sans-serif"
 return f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" font-weight="{w}" fill="{c}" text-anchor="{anchor}">{escape(str(s))}</text>'
def rect(x,y,w,h,fill='none',stroke='#0f172a',sw=1,rx=0,dash=None):
 d=f' stroke-dasharray="{dash}"' if dash else ''
 return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'
W,H=1800,800;out=[]
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
out.append(rect(0,0,W,H,'#f8fafc','none',0))
out.append(txt(30,38,'Common resistor well — compact options',24,'#0f172a',700))
out.append(txt(30,62,'No individual XR rings · dummy only at the two outer ends · structure only',9,'#b91c1c',mono=True))
for pi,(name,blocks,gw,gh) in enumerate(layouts):
 ow,oh=gw+2*(GAP+RING),gh+2*(GAP+RING)
 px=40+pi*860;py=110;pw=800;ph=620
 out.append(rect(px,py,pw,ph,'#fff','#cbd5e1',1))
 out.append(txt(px+12,py+24,name,15,'#0f172a',700))
 out.append(txt(px+12,py+44,f'group {gw:.2f}×{gh:.2f} · outer {ow:.2f}×{oh:.2f} · area {ow*oh:.0f} µm²',8,'#334155',mono=True))
 S=min(700/ow,500/oh);ox=px+(pw-ow*S)/2;oy=py+75
 def X(x): return ox+x*S
 def Y(y): return oy+y*S
 out.append(rect(X(0),Y(0),ow*S,oh*S,'#fef3c7','#b45309',1.2,2))
 out.append(rect(X(RING),Y(RING),(ow-2*RING)*S,(oh-2*RING)*S,'#fff7ed','#b45309',.5,1))
 cx,cy=RING+GAP,RING+GAP
 out.append(rect(X(cx),Y(cy),gw*S,gh*S,'#fff7ed','#d97706',.5,0))
 for n,(x0,y0,bw,bh) in blocks.items():
  p=R[n];arr=p['array'];rows,cols=arr['rows'],arr['cols'];active=arr['active_cells']
  out.append(rect(X(cx+x0),Y(cy+y0),bw*S,bh*S,'none','#d97706',.4,0,dash='3 2'))
  out.append(txt(X(cx+x0+1),Y(cy+y0+4),n,7,'#92400e',700,mono=True))
  cellw=bw/cols;rowh=bh/rows;pos=set([(r,c) for r in range(rows) for c in range(cols)][:active])
  for r in range(rows):
   for c in range(cols):
    x=cx+x0+c*cellw;y=cy+y0+r*rowh
    if (r,c) in pos:
     sw=min(arr['segment_length_um'],cellw*.92);sh=arr['segment_width_um']
     out.append(rect(X(x+(cellw-sw)/2),Y(y+(rowh-sh)/2),sw*S,max(sh*S,2),'#fef08a','#b45309',.4,1))
 # group-level end dummies
 for xx in (cx-.55,cx+gw+.20):
  out.append(rect(X(xx),Y(cy+gh/2-.35),.35*S,.70*S,'#e2e8f0','#94a3b8',.6,1))
  out.append(txt(X(xx+.17),Y(cy+gh/2-.55),'DM',5,'#64748b',700,'middle',True))
 out.append(txt(px+12,py+ph-24,'one common well/ring; no individual XR rings; no metal',7,'#64748b',mono=True))
out.append('</svg>')
(ROOT/'examples/sky130_ldo_01v8/passive-banks/XR_GROUP_COMPACT.svg').write_text('\n'.join(out),encoding='utf-8')
json.dump([{'name':n,'group_um':[gw,gh],'outer_um':[gw+2*(GAP+RING),gh+2*(GAP+RING)]} for n,b,gw,gh in layouts],
          open(ROOT/'examples/sky130_ldo_01v8/passive-banks/XR_GROUP_COMPACT.json','w'),indent=2)
print('wrote')
