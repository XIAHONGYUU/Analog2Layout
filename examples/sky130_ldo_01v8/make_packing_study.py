#!/usr/bin/env python3
"""DNW1 packing study P0/P1/P2/P3. Block-level visual, not GDS/DRC."""
from html import escape
from pathlib import Path
import importlib.util, itertools, json

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('comp',ROOT/'examples/sky130_ldo_01v8/make_white_line.py')
comp=importlib.util.module_from_spec(spec); spec.loader.exec_module(comp)
wb=comp.make_well_blocks(); pb=comp.make_passive_blocks(); bb=comp.make_blackbox_blocks()
blocks=wb+pb+bb
eff=sum(b['w']*b['h'] for b in blocks)
passb=comp.make_pass_block(); PW,PH=passb['w'],passb['h']

def pack(target,mask=0):
    items=[]
    for i,b in enumerate(blocks):
        rot=bool((mask>>i)&1)
        w,h=(b['h'],b['w']) if rot else (b['w'],b['h'])
        items.append((b['name'],w,h,rot))
    place,W,H=comp.shelf_pack([(n,w,h) for n,w,h,r in items],target,gap=comp.GROUP_GAP)
    dw,dh=W+2*comp.DNW_MARGIN,H+2*comp.DNW_MARGIN
    right=(dw+8+PW)*max(dh,PH); below=max(dw,PW)*(dh+8+PH)
    if right<=below:
        mode='right'; bw=dw+8+PW; bh=max(dh,PH); px=dw+8; py=(bh-PH)/2
    else:
        mode='below'; bw=max(dw,PW); bh=dh+8+PH; px=(bw-PW)/2; py=dh+8
    return {'target':target,'mask':mask,'mode':mode,'dnw':(dw,dh),'bbox':(bw,bh),
            'area':bw*bh,'util':eff/(dw*dh),'place':place,'items':items,
            'pass_xy':(px,py)}
man=json.loads((ROOT/'examples/sky130_ldo_01v8/white-line-manifest.json').read_text())
# manifest block coords include the 2 um DNW margin; remove it for local packing coords
mplace={b['name']:(b['x']-comp.DNW_MARGIN,b['y']-comp.DNW_MARGIN) for b in man['blocks']}
P0={'target':38,'mask':0,'mode':'right','dnw':tuple(man['dnw1'][k] for k in ('w','h')),
    'bbox':tuple(man['bbox_um']),'area':man['area_um2'],'util':eff/(man['dnw1']['w']*man['dnw1']['h']),
    'place':mplace,'items':[(b['name'],b['w'],b['h'],False) for b in blocks],
    'pass_xy':(man['pass']['x']-comp.DNW_MARGIN,man['pass']['y']-comp.DNW_MARGIN)}
P1=pack(44); P2=pack(24); P3=pack(36,38700)
opts=[P0,P1,P2,P3]; names=['P0 current','P1 target 44','P2 target 24','P3 rotation-aware']
# draw
W,H=2000,900; out=[]
def add(s): out.append(s)
def rect(x,y,w,h,fill='#fff',stroke='#0f172a',sw=1,rx=0,dash=None):
 d=f' stroke-dasharray="{dash}"' if dash else ''
 add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
def txt(x,y,s,size=12,c='#0f172a',w=400,anchor='start',mono=False):
 fam="'DejaVu Sans Mono',monospace" if mono else "'DejaVu Sans',sans-serif"
 add(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{w}" fill="{c}" text-anchor="{anchor}">{escape(str(s))}</text>')
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
rect(0,0,W,H,'#f8fafc','none',0)
txt(30,40,'DNW1 packing study — P0 / P1 / P2 / P3',26,'#0f172a',700)
txt(30,65,'Block-level visual only · pass envelope shown · no GDS/DRC/LVS',10,'#b91c1c',mono=True)
for j,o in enumerate(opts):
    px=30+j*485; py=100; panelw=450; panelh=720
    rect(px,py,panelw,panelh,'#fff','#cbd5e1',1)
    txt(px+14,py+25,names[j],14,'#0f172a',700)
    bw,bh=o['bbox']; dw,dh=o['dnw']
    txt(px+14,py+45,f'DNW1 {dw:.1f}×{dh:.1f} · density {o["util"]*100:.1f}%',8,'#334155',mono=True)
    txt(px+14,py+60,f'bbox {bw:.1f}×{bh:.1f} · area {o["area"]:.0f}',8,'#334155',mono=True)
    # scale fitting
    s=min((panelw-40)/bw,(panelh-150)/bh)
    ox=px+20; oy=py+100
    # DNW1
    rect(ox,oy,dw*s,dh*s,'none','#0f766e',1.5,dash='5 3')
    txt(ox+2,oy-5,'DNW1',7,'#0f766e',700,mono=True)
    # blocks
    for n,w,h,rot in o['items']:
        bx,by=o['place'][n]; x=ox+bx*s; y=oy+by*s
        col='#d1fae5' if n.startswith(('P','N')) else '#fef3c7'
        rect(x,y,w*s,h*s,col,'#64748b',.6)
        if w*s>26 and h*s>12:
            txt(x+w*s/2,y+h*s/2+3,n.replace('_BANK','').replace('_PW','').replace('_NW','')[:12],5,'#334155',700,'middle',mono=True)
        if rot:
            txt(x+2,y+7,'R90',5,'#b91c1c',700,mono=True)
    # pass envelope at position for right/below
    ppx,ppy=o['pass_xy']; x=ox+ppx*s; y=oy+ppy*s
    rect(x,y,PW*s,PH*s,'#fce7f3','#be185d',1,dash='4 2')
    txt(x+3,y+12,'XM61 pass envelope',6,'#9d174d',700,mono=True)
    # bbox
    rect(ox,oy,bw*s,bh*s,'none','#0f172a',1)
    txt(px+14,py+panelh-28,('mode '+o['mode']+' · rotated blocks '+str(bin(o['mask']).count('1'))),7,'#64748b',mono=True)
add('</svg>')
(Path(ROOT/'examples/sky130_ldo_01v8/dnw1-packing-study.svg')).write_text('\n'.join(out),encoding='utf-8')
json.dump([{k:o[k] for k in ('target','mask','mode','dnw','bbox','area','util')} for o in opts],
          open(ROOT/'examples/sky130_ldo_01v8/dnw1-packing-study.json','w'),indent=2)
print('wrote study', [round(o['area']) for o in opts])
