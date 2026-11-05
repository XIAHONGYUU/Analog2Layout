#!/usr/bin/env python3
"""DNW1-only packing study using fixed bank macros; DNW2 is excluded."""
from html import escape
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
LIB=json.loads((ROOT/'examples/sky130_ldo_01v8/banks/bank-library.json').read_text())
MAN=json.loads((ROOT/'examples/sky130_ldo_01v8/white-line-manifest.json').read_text())
GAP=2.0; DNWM=2.0
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
    place={}; y=0
    for sh in shelves:
        x=0
        for it in sh['items']:
            place[it[0]]=(x,y); x+=it[1]+GAP
        y+=sh['h']
    return place,W,H
def option(target):
    place,W,H=shelf(target); dw,dh=W+2*DNWM,H+2*DNWM
    return {'target':target,'dnw':(dw,dh),'area':dw*dh,'util':eff/(dw*dh),'place':place}
opts=[('D area-min',option(24)),('C',option(30)),('A',option(40)),('B balanced',option(72))]
W,H=2200,1000;out=[]
def add(s): out.append(s)
def rect(x,y,w,h,fill='#fff',stroke='#0f172a',sw=1,dash=None,rx=0):
 d=f' stroke-dasharray="{dash}"' if dash else ''
 add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
def txt(x,y,s,size=12,c='#0f172a',w=400,anchor='start',mono=False):
 fam="'DejaVu Sans Mono',monospace" if mono else "'DejaVu Sans',sans-serif"
 add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" font-weight="{w}" fill="{c}" text-anchor="{anchor}">{escape(str(s))}</text>')
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
rect(0,0,W,H,'#f8fafc','none',0)
txt(30,38,'DNW1-only area study — fixed bank macros, no DNW2',26,'#0f172a',700)
txt(30,62,'DNW2 excluded · no bank rotation · poly vertical · bank macro outer dimensions from bank-library',9,'#b91c1c',mono=True)
for j,(name,o) in enumerate(opts):
    px=30+j*540;py=100;pw=520;ph=850
    rect(px,py,pw,ph,'#fff','#cbd5e1',1)
    dw,dh=o['dnw']; s=min((pw-40)/dw,(ph-145)/dh)
    txt(px+12,py+24,name,14,'#0f172a',700)
    txt(px+12,py+44,f'DNW1 {dw:.2f}×{dh:.2f} · area {o["area"]:.0f} µm²',8,'#334155',mono=True)
    txt(px+12,py+60,f'density {o["util"]*100:.1f}% · AR {dw/dh:.2f} · target {o["target"]}',8,'#334155',mono=True)
    ox=px+(pw-dw*s)/2; oy=py+95
    rect(ox,oy,dw*s,dh*s,'none','#0f766e',1.4,dash='5 3')
    txt(ox+2,oy-5,'DNW1',7,'#0f766e',700,mono=True)
    for n,w,h,k in blocks:
        x,y=o['place'][n]; X=ox+x*s; Y=oy+y*s
        col='#d1fae5' if k=='bank' else ('#fef3c7' if k=='passive' else '#e0f2fe')
        rect(X,Y,w*s,h*s,col,'#64748b',.5)
        if w*s>24 and h*s>9:
            txt(X+w*s/2,Y+h*s/2,n.replace('_BANK','')[:12],4.2,'#334155',700,'middle',mono=True)
    txt(px+12,py+ph-24,'DNW1 only · no XM61/DNW2 envelope in this bbox',7,'#64748b',mono=True)
add('</svg>')
(ROOT/'examples/sky130_ldo_01v8/dnw1-area-study.svg').write_text('\n'.join(out),encoding='utf-8')
json.dump([{'name':n,'target':o['target'],'dnw':o['dnw'],'area':o['area'],'util':o['util']} for n,o in opts],
          open(ROOT/'examples/sky130_ldo_01v8/dnw1-area-study.json','w'),indent=2)
print('wrote',[(n,round(o['area']),round(o['util'],3)) for n,o in opts])
