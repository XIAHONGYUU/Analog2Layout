#!/usr/bin/env python3
"""DNW1 assembly study from FIXED bank macros (no bank rotation).

Three area layouts: A total-area minimum, B balanced, C density-first.
Not GDS/DRC/LVS.
"""
from html import escape
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
LIB=json.loads((ROOT/'examples/sky130_ldo_01v8/banks/bank-library.json').read_text())
MAN=json.loads((ROOT/'examples/sky130_ldo_01v8/white-line-manifest.json').read_text())
GAP=2.0; DNWM=2.0; PASSW,PASSH=MAN['pass']['w'],MAN['pass']['h']
blocks=[]
for b in LIB:
    if b['bank'].startswith('PASS'): continue
    blocks.append((b['bank'],b['outer_um'][0],b['outer_um'][1],'bank'))
for p in MAN['passive_blocks']:
    blocks.append((p['name'],p['w'],p['h'],'passive'))
for b in MAN['blackboxes']:
    blocks.append((b['name'],b['w'],b['h'],'blackbox'))
eff=sum(w*h for n,w,h,k in blocks)
def shelf(target):
    shelves=[]
    for it in sorted(blocks,key=lambda x:(-x[2],-x[1])):
        placed=False
        for sh in shelves:
            if sh['w']+GAP+it[1]<=target+1e-9:
                sh['items'].append(it); sh['w']+=GAP+it[1]; sh['h']=max(sh['h'],it[2]); placed=True; break
        if not placed: shelves.append({'items':[it],'w':it[1],'h':it[2]})
    W=max(s['w'] for s in shelves); H=sum(s['h'] for s in shelves)
    place={};y=0
    for sh in shelves:
        x=0
        for it in sh['items']:
            place[it[0]]=(x,y);x+=it[1]+GAP
        y+=sh['h']
    return place,W,H
def option(target):
    place,W,H=shelf(target);dw,dh=W+2*DNWM,H+2*DNWM
    right=(dw+8+PASSW)*max(dh,PASSH); below=max(dw,PASSW)*(dh+8+PASSH)
    if right<=below: mode='right'; bw=dw+8+PASSW; bh=max(dh,PASSH); px=dw+8;py=(bh-PASSH)/2
    else: mode='below'; bw=max(dw,PASSW);bh=dh+8+PASSH;px=(bw-PASSW)/2;py=dh+8
    return {'target':target,'dnw':(dw,dh),'bbox':(bw,bh),'area':bw*bh,'util':eff/(dw*dh),
            'mode':mode,'place':place,'pass_xy':(px,py)}
opts=[('A total-area',option(40)),('B balanced',option(72)),('C density',option(30)),('D compact',option(24))]
W,H=2200,1100;out=[]
def add(s):out.append(s)
def rect(x,y,w,h,fill='#fff',stroke='#0f172a',sw=1,dash=None,rx=0):
 d=f' stroke-dasharray="{dash}"' if dash else ''
 add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
def txt(x,y,s,size=12,c='#0f172a',w=400,anchor='start',mono=False):
 fam="'DejaVu Sans Mono',monospace" if mono else "'DejaVu Sans',sans-serif"
 add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" font-weight="{w}" fill="{c}" text-anchor="{anchor}">{escape(str(s))}</text>')
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
rect(0,0,W,H,'#f8fafc','none',0)
txt(30,38,'DNW1 assembly — fixed banks, no bank rotation',26,'#0f172a',700)
txt(30,62,'A total-area · B balanced · C density · D compact · FIXED bank macros · no GDS/DRC',9,'#b91c1c',mono=True)
for j,(name,o) in enumerate(opts):
 px=30+j*540;py=100;pw=520;ph=900
 rect(px,py,pw,ph,'#fff','#cbd5e1',1)
 txt(px+12,py+24,name,14,'#0f172a',700)
 txt(px+12,py+44,f'DNW1 {o["dnw"][0]:.2f}×{o["dnw"][1]:.2f} · density {o["util"]*100:.1f}%',8,'#334155',mono=True)
 txt(px+12,py+60,f'bbox {o["bbox"][0]:.1f}×{o["bbox"][1]:.1f} · area {o["area"]:.0f}',8,'#334155',mono=True)
 dw,dh=o['dnw'];bw,bh=o['bbox'];s=min((pw-30)/bw,(ph-130)/bh)
 ox=px+15;oy=py+85
 rect(ox,oy,dw*s,dh*s,'none','#0f766e',1.3,dash='5 3')
 txt(ox+2,oy-4,'DNW1',6,'#0f766e',700,mono=True)
 for n,w,h,k in blocks:
  x,y=o['place'][n];X=ox+x*s;Y=oy+y*s
  col='#d1fae5' if k=='bank' else ('#fef3c7' if k=='passive' else '#e0f2fe')
  rect(X,Y,w*s,h*s,col,'#64748b',.5)
  if w*s>22 and h*s>8:
   txt(X+w*s/2,Y+h*s/2,n.replace('_BANK','')[:12],4.5,'#334155',700,'middle',mono=True)
 ppx,ppy=o['pass_xy'];X=ox+ppx*s;Y=oy+ppy*s
 rect(X,Y,PASSW*s,PASSH*s,'#fce7f3','#be185d',1,dash='3 2')
 txt(X+3,Y+12,'F pass',6,'#9d174d',700,mono=True)
 rect(ox,oy,bw*s,bh*s,'none','#0f172a',1)
 txt(px+12,py+ph-22,f'mode {o["mode"]} · target {o["target"]}',7,'#64748b',mono=True)
add('</svg>')
(ROOT/'examples/sky130_ldo_01v8/dnw1-assembly.svg').write_text('\n'.join(out),encoding='utf-8')
json.dump([{'name':n,**{k:o[k] for k in ('target','dnw','bbox','area','util','mode')}} for n,o in opts],
          open(ROOT/'examples/sky130_ldo_01v8/dnw1-assembly.json','w'),indent=2)
print('wrote',[(n,round(o['area']),round(o['util'],3)) for n,o in opts])
