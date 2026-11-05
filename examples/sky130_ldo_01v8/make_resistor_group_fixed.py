#!/usr/bin/env python3
"""Corrected R group: per-column long-edge dummies, explicit AA band, heads."""
from html import escape
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
D=json.loads((ROOT/'examples/sky130_ldo_01v8/white-line-input.json').read_text())
R={p['name']:p for p in D['passives'] if p['type']=='resistor'}
RING=1.0; GAP=.8; AAW=.5; DMW=.35; DMG=.5
blocks={
 'XR5':{'x':0,'y':1.7,'w':20,'h':15.30},
 'XR4':{'x':21,'y':1.7,'w':20,'h':7.65},
 'XR6':{'x':42,'y':1.7,'w':10,'h':3.40},
}
GW=52.0; GH=17.35
def txt(x,y,s,size=12,c='#0f172a',w=400,anchor='start',mono=False):
 fam="'DejaVu Sans Mono',monospace" if mono else "'DejaVu Sans',sans-serif"
 return f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" font-weight="{w}" fill="{c}" text-anchor="{anchor}">{escape(str(s))}</text>'
def rect(x,y,w,h,fill='none',stroke='#0f172a',sw=1,rx=0,dash=None):
 d=f' stroke-dasharray="{dash}"' if dash else ''
 return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'
W,H=1700,860;S=min(1250/GW,560/GH);ox=(W-GW*S)/2;oy=160
def X(x): return ox+x*S
def Y(y): return oy+y*S
out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',rect(0,0,W,H,'#f8fafc','none',0)]
out.append(txt(28,36,'XR4/XR5/XR6 — corrected R bank structure',22,'#0f172a',700))
out.append(txt(28,58,'per-column long-edge dummies · dummies inside common well · AA band only at perimeter · no AA under R',9,'#475569',mono=True))
out.append(txt(28,76,'field fill; AA/tap band; resistor heads/contacts shown as intent; no DRC/LVS',8,'#b91c1c',mono=True))
# outer AA/tap band + common passive ring
out.append(rect(X(-RING-GAP-AAW),Y(-RING-GAP-AAW),(GW+2*(RING+GAP+AAW))*S,(GH+2*(RING+GAP+AAW))*S,'none','#16a34a',2.0,0))
out.append(rect(X(-RING-GAP),Y(-RING-GAP),(GW+2*(RING+GAP))*S,(GH+2*(RING+GAP))*S,'#fef3c7','#b45309',1.2,2))
out.append(rect(X(-RING),Y(-RING),(GW+2*RING)*S,(GH+2*RING)*S,'#fff7ed','#b45309',.5,1))
out.append(rect(X(0),Y(0),GW*S,GH*S,'#fff7ed','#d97706',.4,0))
# AA band: perimeter band only, no AA in core
for side in range(4):
 if side==0: out.append(rect(X(-RING-GAP-AAW),Y(-RING-GAP-AAW),(GW+2*(RING+GAP+AAW))*S,AAW*S,'#bbf7d0','#16a34a',.6,0))
 if side==1: out.append(rect(X(-RING-GAP-AAW),Y(GH+RING+GAP),(GW+2*(RING+GAP+AAW))*S,AAW*S,'#bbf7d0','#16a34a',.6,0))
 if side==2: out.append(rect(X(-RING-GAP-AAW),Y(-RING-GAP-AAW),AAW*S,(GH+2*(RING+GAP+AAW))*S,'#bbf7d0','#16a34a',.6,0))
 if side==3: out.append(rect(X(GW+RING+GAP),Y(-RING-GAP-AAW),AAW*S,(GH+2*(RING+GAP+AAW))*S,'#bbf7d0','#16a34a',.6,0))
# AA tap contacts, centered on the AA band (not outside it)
bx0=-RING-GAP-AAW; by0=-RING-GAP-AAW
bw=GW+2*(RING+GAP+AAW); bh=GH+2*(RING+GAP+AAW)
top_y=by0+AAW/2; bot_y=by0+bh-AAW/2
left_x=bx0+AAW/2; right_x=bx0+bw-AAW/2
for xx in [bx0+0.3+k*0.55 for k in range(int((bw-0.5)/0.55)+1)]:
 if xx < bx0+bw-0.2:
  for yy in (top_y,bot_y):
   out.append(rect(X(xx)-.085*S,Y(yy)-.085*S,.17*S,.17*S,'#111827','none',0,0))
for yy in [by0+0.3+k*0.55 for k in range(int((bh-0.5)/0.55)+1)]:
 if yy < by0+bh-0.2:
  for xx in (left_x,right_x):
   out.append(rect(X(xx)-.085*S,Y(yy)-.085*S,.17*S,.17*S,'#111827','none',0,0))
# resistors
for name,b in blocks.items():
 p=R[name];arr=p['array'];cols=arr['cols'];active=arr['active_cells'];rows=(active+cols-1)//cols
 x0,y0,bw,bh=b['x'],b['y'],b['w'],b['h']; cellw=bw/cols; rowh=bh/rows
 out.append(txt(X(x0+1),Y(y0-0.5),name,7,'#92400e',700,mono=True))
 # per-column long-edge dummies (above and below each active column)
 for c in range(cols):
  for dy in (-DMG-DMW,bh+DMG):
   out.append(rect(X(x0+c*cellw),Y(y0+dy),cellw*S,max(DMW*S,2),'#e2e8f0','#94a3b8',.5,1))
 # active column backgrounds / segments
 for c in range(cols):
  out.append(rect(X(x0+c*cellw),Y(y0),cellw*S,bh*S,'none','#d97706',.25,0,dash='3 2'))
 for r in range(rows):
  for c in range(cols):
   if r*cols+c>=active: continue
   x=x0+c*cellw;y=y0+r*rowh
   sw=min(arr['segment_length_um'],cellw*.92);sh=arr['segment_width_um']
   out.append(rect(X(x+(cellw-sw)/2),Y(y+(rowh-sh)/2),sw*S,max(sh*S,2),'#fef08a','#b45309',.4,1))
 # end heads / contacts at left and right of each resistor block (intent)
 for hx in (x0-.22,x0+bw+.02):
  out.append(rect(X(hx),Y(y0),.20*S,bh*S,'#ddd6fe','#6d28d9',.5,0))
  for yy in (y0+bh*.25,y0+bh*.75):
   out.append(rect(X(hx+.01),Y(yy)-.085*S,.17*S,.17*S,'#111827','none',0,0))
out.append(txt(28,H-50,'green = AA/tap band (perimeter only) · violet = resistor head intent · gray = long-edge dummy · no AA under R',8,'#64748b',mono=True))
out.append(txt(28,H-30,'Dummy: one 10×0.35 strip above and below each active column; dummies are inside the common well.',8,'#64748b',mono=True))
out.append('</svg>')
(ROOT/'examples/sky130_ldo_01v8/passive-banks/XR_GROUP_FIXED.svg').write_text('\n'.join(out),encoding='utf-8')
json.dump({'name':'XR_GROUP_FIXED','group_um':[GW,GH],'blocks':blocks,
           'dummy':'one 10x0.35 long-edge strip above and below each active column',
           'dummy_segments':10,'aa':'perimeter band only'},
          open(ROOT/'examples/sky130_ldo_01v8/passive-banks/XR_GROUP_FIXED.json','w'),indent=2)
print('wrote')
