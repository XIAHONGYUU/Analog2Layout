#!/usr/bin/env python3
"""One common resistor well for XR4/XR5/XR6.

The three xhigh resistors share one well/ring. Dummy is only at the two outer
ends of the combined group. Structure-level intent, not GDS/DRC.
"""
from html import escape
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
D=json.loads((ROOT/'examples/sky130_ldo_01v8/white-line-input.json').read_text())
R={p['name']:p for p in D['passives'] if p['type']=='resistor'}
OUT=ROOT/'examples/sky130_ldo_01v8/passive-banks'; OUT.mkdir(exist_ok=True)
RING=1.0; GAP=.8; INNER_GAP=1.0
# arrangement: XR5 left; XR4/XR6 right, stacked
blocks={
 'XR5':(0.0,0.0,20.0,20.75),
 'XR4':(22.0,0.0,20.0,10.55),
 'XR6':(22.0,11.55,10.0,7.15),
}
GW=max(x+w for x,y,w,h in blocks.values())
GH=max(y+h for x,y,w,h in blocks.values())
OW,OH=GW+2*(GAP+RING),GH+2*(GAP+RING)

def txt(x,y,s,size=12,c='#0f172a',w=400,anchor='start',mono=False):
 fam="'DejaVu Sans Mono',monospace" if mono else "'DejaVu Sans',sans-serif"
 return f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" font-weight="{w}" fill="{c}" text-anchor="{anchor}">{escape(str(s))}</text>'
def rect(x,y,w,h,fill='none',stroke='#0f172a',sw=1,rx=0,dash=None):
 d=f' stroke-dasharray="{dash}"' if dash else ''
 return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'
Wpx,Hpx=1200,760; S=min(900/OW,560/OH); ox=(Wpx-OW*S)/2; oy=150
def X(x): return ox+x*S
def Y(y): return oy+y*S
out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wpx}" height="{Hpx}" viewBox="0 0 {Wpx} {Hpx}">',rect(0,0,Wpx,Hpx,'#f8fafc','none',0)]
out.append(txt(28,36,'XR4/XR5/XR6 — one common resistor well',22,'#0f172a',700))
out.append(txt(28,58,'3 folded xhigh resistors · one ring · dummy only at the two outer ends · structure only',9,'#475569',mono=True))
out.append(txt(28,76,f'group {GW:.2f}×{GH:.2f} · outer {OW:.2f}×{OH:.2f} · ring {RING}/{GAP} · no DRC',8,'#b91c1c',mono=True))
# one common well + ring
out.append(rect(X(0),Y(0),OW*S,OH*S,'#fef3c7','#b45309',1.3,3))
out.append(rect(X(RING),Y(RING),(OW-2*RING)*S,(OH-2*RING)*S,'#fff7ed','#b45309',.6,1))
cx0,cy0=RING+GAP,RING+GAP
out.append(rect(X(cx0),Y(cy0),GW*S,GH*S,'#fff7ed','#d97706',.6,0))
# resistor arrays inside common well (no individual rings)
for name,(x0,y0,bw,bh) in blocks.items():
 p=R[name]; arr=p['array']; rows,cols=arr['rows'],arr['cols']; active=arr['active_cells']
 out.append(rect(X(cx0+x0),Y(cy0+y0),bw*S,bh*S,'none','#d97706',.45,0,dash='3 2'))
 out.append(txt(X(cx0+x0+1),Y(cy0+y0+4),name,7,'#92400e',700,mono=True))
 cellw=bw/cols; rowh=bh/rows
 positions=[(r,c) for r in range(rows) for c in range(cols)][:active]
 for r in range(rows):
  for c in range(cols):
   x=cx0+x0+c*cellw; y=cy0+y0+r*rowh
   segw=min(arr['segment_length_um'],cellw*.92); segh=arr['segment_width_um']
   sx=x+(cellw-segw)/2; sy=y+(rowh-segh)/2
   if (r,c) in positions:
    out.append(rect(X(sx),Y(sy),segw*S,max(segh*S,2),'#fef08a','#b45309',.4,1))
# dummy only at two outer ends of the combined group
for name,x0,y0,bw,bh in [('DM-left',0,GH/2-.35,0,0),('DM-right',GW-1.1,GH/2-.35,0,0)]:
 pass
out.append(rect(X(cx0-.55),Y(cy0+GH/2-.35),.35*S,.70*S,'#e2e8f0','#94a3b8',.7,1))
out.append(rect(X(cx0+GW+.20),Y(cy0+GH/2-.35),.35*S,.70*S,'#e2e8f0','#94a3b8',.7,1))
out.append(txt(X(cx0-.55),Y(cy0+GH/2-0.55),'DM',5,'#64748b',700,'middle',True))
out.append(txt(X(cx0+GW+.55),Y(cy0+GH/2-0.55),'DM',5,'#64748b',700,'middle',True))
out.append(txt(28,Hpx-54,'one common well/ring; no individual XR rings; no resistor end metal or connections',8,'#64748b',mono=True))
out.append('</svg>')
(OUT/'XR_GROUP.svg').write_text('\n'.join(out),encoding='utf-8')
meta={'name':'XR_GROUP','members':['XR4','XR5','XR6'],'group_um':[GW,GH],'outer_um':[OW,OH],
      'ring':[RING,GAP],'dummy':'one at each outer end','blocks':blocks}
(OUT/'XR_GROUP.json').write_text(json.dumps(meta,indent=2)+'\n')
print('wrote',GW,GH,OW,OH)
