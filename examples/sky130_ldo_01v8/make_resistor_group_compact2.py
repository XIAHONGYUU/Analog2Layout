#!/usr/bin/env python3
"""Compact stepped R bank: no rectangular fill around XR4/XR5/XR6."""
from html import escape
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
D=json.loads((ROOT/'examples/sky130_ldo_01v8/white-line-input.json').read_text())
R={p['name']:p for p in D['passives'] if p['type']=='resistor'}
DMW=.35; DMG=.5; AA=.5
# block extents include top/bottom long-edge dummies
blocks={
 'XR5':{'x':0,'y':0,'w':20,'h':17.00,'active_y':0.85,'active_h':15.30},
 'XR4':{'x':20,'y':0,'w':20,'h':9.35,'active_y':0.85,'active_h':7.65},
 'XR6':{'x':20,'y':9.35,'w':10,'h':5.10,'active_y':10.20,'active_h':3.40},
}
# union outline: XR5 full left; XR4 right top; XR6 right below; cut empty right-bottom
union=[(0,0),(40,0),(40,9.35),(30,9.35),(30,14.45),(20,14.45),(20,17.00),(0,17.00)]
GW,GH=40.0,17.0
def txt(x,y,s,size=12,c='#0f172a',w=400,anchor='start',mono=False):
 fam="'DejaVu Sans Mono',monospace" if mono else "'DejaVu Sans',sans-serif"
 return f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" font-weight="{w}" fill="{c}" text-anchor="{anchor}">{escape(str(s))}</text>'
def rect(x,y,w,h,fill='none',stroke='#0f172a',sw=1,rx=0,dash=None):
 d=f' stroke-dasharray="{dash}"' if dash else ''
 return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'
W,H=1400,760;S=min(1050/GW,520/GH);ox=(W-GW*S)/2;oy=150
def X(x): return ox+x*S
def Y(y): return oy+y*S
out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',rect(0,0,W,H,'#f8fafc','none',0)]
out.append(txt(28,36,'XR4/XR5/XR6 — compact stepped common well',22,'#0f172a',700))
out.append(txt(28,58,'no rectangular fill around XR4/XR6 · dummies included in well · AA only on stepped perimeter',9,'#475569',mono=True))
out.append(txt(28,76,'structure only · no DRC/LVS · no metal',8,'#b91c1c',mono=True))
pts=' '.join(f'{X(x):.1f},{Y(y):.1f}' for x,y in union)
# AA band as thick green stroke outside union; ring/field
out.append(f'<polygon points="{pts}" fill="#fff7ed" stroke="#16a34a" stroke-width="{AA*S:.1f}" stroke-linejoin="round"/>')
out.append(f'<polygon points="{pts}" fill="none" stroke="#b45309" stroke-width="{0.38*S:.1f}" stroke-linejoin="round"/>')
# draw blocks active + per-column dummies, all inside union
for name,b in blocks.items():
 p=R[name];arr=p['array'];cols=arr['cols'];active=arr['active_cells'];rows=(active+cols-1)//cols
 x0,y0= b['x'],b['y']; bw=b['w']; ah=b['active_h']; ay=b['active_y']; cellw=bw/cols; rowh=ah/rows
 out.append(txt(X(x0+1),Y(ay-0.45),name,7,'#92400e',700,mono=True))
 # active column backgrounds
 for c in range(cols):
  out.append(rect(X(x0+c*cellw),Y(ay),cellw*S,ah*S,'none','#d97706',.25,0,dash='3 2'))
  # dummies above/below each column
  for dy in (-DMG-DMW, ah+DMG):
   out.append(rect(X(x0+c*cellw),Y(ay+dy),cellw*S,max(DMW*S,2),'#e2e8f0','#94a3b8',.5,1))
 # active segments
 for r in range(rows):
  for c in range(cols):
   if r*cols+c>=active: continue
   x=x0+c*cellw;y=ay+r*rowh
   sw=min(arr['segment_length_um'],cellw*.92);sh=arr['segment_width_um']
   out.append(rect(X(x+(cellw-sw)/2),Y(y+(rowh-sh)/2),sw*S,max(sh*S,2),'#fef08a','#b45309',.4,1))
 # head bars at active ends (inside extent)
 for hx in (x0+.02,x0+bw-.22):
  out.append(rect(X(hx),Y(ay),.20*S,ah*S,'#ddd6fe','#6d28d9',.5,0))
  for yy in (ay+ah*.25,ay+ah*.75):
   out.append(rect(X(hx+.015),Y(yy)-.085*S,.17*S,.17*S,'#111827','none',0,0))
# AA contacts on stepped perimeter (approximate; just visual intent)
for xy in [(0,0),(40,0),(40,9.35),(30,9.35),(30,14.45),(20,14.45),(20,17),(0,17)]:
 out.append(rect(X(xy[0])-.085*S,Y(xy[1])-.085*S,.17*S,.17*S,'#111827','none',0,0))
out.append(txt(28,H-50,'green = AA/tap band on stepped perimeter · violet = resistor head intent · gray = per-column long-edge dummy',8,'#64748b',mono=True))
out.append(txt(28,H-30,'Empty rectangular area at right-bottom is removed; dummy and active are inside the stepped well.',8,'#64748b',mono=True))
out.append('</svg>')
(ROOT/'examples/sky130_ldo_01v8/passive-banks/XR_GROUP_COMPACT2.svg').write_text('\n'.join(out),encoding='utf-8')
json.dump({'name':'XR_GROUP_COMPACT2','bbox_um':[GW,GH],'union_outline':union,'blocks':blocks,
           'dummy':'per-column long-edge above/below','area_bbox':GW*GH},open(ROOT/'examples/sky130_ldo_01v8/passive-banks/XR_GROUP_COMPACT2.json','w'),indent=2)
print('wrote',GW,GH)
