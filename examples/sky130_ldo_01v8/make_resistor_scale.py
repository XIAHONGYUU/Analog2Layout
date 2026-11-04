#!/usr/bin/env python3
"""True-scale resistor dimension reference for XR4/XR5/XR6.
This is a dimension drawing, not a legal layout.
"""
from html import escape
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'examples/sky130_ldo_01v8/resistor-scale.svg'
PNG=ROOT/'examples/sky130_ldo_01v8/resistor-scale.png'
W,H=1600,620
out=[]
def add(s): out.append(s)
def txt(x,y,s,size=14,c='#0f172a',w=400,anchor='start',mono=False):
 fam="'DejaVu Sans Mono',monospace" if mono else "'DejaVu Sans',sans-serif"
 add(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{w}" fill="{c}" text-anchor="{anchor}">{escape(str(s))}</text>')
def rect(x,y,w,h,fill='none',stroke='#0f172a',sw=1):
 add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
def line(x1,y1,x2,y2,c='#0f172a',sw=1):
 add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{sw}"/>')
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
rect(0,0,W,H,'#f8fafc','none',0)
txt(30,38,'LDO xhigh resistor dimensions — true scale reference',26,'#0f172a',700)
txt(30,62,'dimension drawing only · active width 0.35 µm · width exaggerated in the bar for visibility · not GDS/DRC',10,'#b91c1c',mono=True)
rows=[('XR4',18,180,'20×10.55',13,2,7,20,10.55),('XR5',36,360,'20×20.75',25,2,13,20,20.75),('XR6',4,40,'10×7.15',9,1,5,10,7.15)]
scale=2.4; x0=200
for i,(name,segs,total,fold,fr,fc,dm,bw,bh) in enumerate(rows):
 y=130+i*145
 txt(30,y+12,name,16,'#b45309',700,mono=True)
 txt(30,y+32,f'{segs} × 10 µm',10,'#334155',mono=True)
 # true-length bar: each segment 10*scale, gap 0.5*scale
 x=x0
 for s in range(segs):
  rect(x,y+5,10*scale,3.5,'#fcd34d','#b45309',.5)
  x+=10*scale+0.5*scale
 # true length label and folded footprint
 txt(x0,y-10,f'active L = {total} µm · W = 0.35 µm',10,'#92400e',700,mono=True)
 txt(x0,y+30,f'folded {fr}×{fc} · block {fold} µm · {dm} dummy',9,'#334155',mono=True)
 # folded block at right
 rx=1250; ry=y-40; bs=5.5
 rect(rx,ry,bw*bs,bh*bs,'#fef3c7','#b45309',1)
 txt(rx+bw*bs/2,ry+bh*bs+13,f'{fr} rows × {fc} cols',8,'#92400e',700,'middle',mono=True)
 txt(rx+bw*bs/2,ry+bh*bs+27,f'{fold} µm footprint',8,'#92400e',400,'middle',mono=True)
 # dimensions
 line(x0,y+45,x0+total*scale/1.0,y+45,'#0f766e',1)
 txt(x0+total*scale/2,y+62,f'{total} µm',9,'#0f766e',700,'middle',mono=True)
add('</svg>')
OUT.write_text('\n'.join(out),encoding='utf-8')
print('wrote',OUT)
