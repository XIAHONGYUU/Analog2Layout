#!/usr/bin/env python3
"""Step-1 output-FET DNW shape/area study for XM61 (illustrative, not DRC)."""
from html import escape
from pathlib import Path
import json, math
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'examples/sky130_ldo_01v8/output-dnw-study.svg'
PNG=ROOT/'examples/sky130_ldo_01v8/output-dnw-study.png'
JSON=ROOT/'examples/sky130_ldo_01v8/output-dnw-study.json'

FW=0.86; L=0.5; BODY_GAP=2.0; BODY_W=2.0; DNW_MARGIN=2.0; GUARD=2.0
opts=[]
for nf in (200,100,67,50,40):
    W=1000/nf; fh=W+.60
    best=None
    for rows in range(1,nf+1):
        cols=math.ceil(nf/rows); cw=cols*FW; ch=rows*fh
        for br,bc in ((1,5),(5,1),(2,3),(3,2)):
            gw=bc*cw+2*(BODY_GAP+BODY_W)+(bc-1)*(2*BODY_GAP+BODY_W)
            gh=br*ch+2*(BODY_GAP+BODY_W)+(br-1)*(2*BODY_GAP+BODY_W)
            dw,dh=gw+2*DNW_MARGIN,gh+2*DNW_MARGIN
            area=dw*dh
            if best is None or area<best[0]:
                best=(area,W,nf,rows,cols,br,bc,cw,ch,gw,gh,dw,dh,cols*fh)
    opts.append(best)
# name/table
names=['A','B','C','D','E']
W,H=2200,1300
out=[]
def add(s): out.append(s)
def rect(x,y,w,h,fill='none',stroke='#0f172a',sw=1.2,rx=0,dash=None):
 d=f' stroke-dasharray="{dash}"' if dash else ''
 add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
def txt(x,y,s,size=14,c='#0f172a',w=400,anchor='start',mono=False):
 fam="'DejaVu Sans Mono',monospace" if mono else "'DejaVu Sans',sans-serif"
 add(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{w}" fill="{c}" text-anchor="{anchor}">{escape(str(s))}</text>')
def line(x1,y1,x2,y2,c='#0f172a',sw=1):
 add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{sw}"/>')
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
rect(0,0,W,H,'#f8fafc','none',0)
txt(30,38,'XM61 output-FET DNW shape / area study',26,'#0f172a',700)
txt(30,62,'Step 1 · total W=5000 µm · five 1000 µm body-ringed sub-banks · shared ring walls · DNW margin 2 µm · outer guard 2/2',10,'#b91c1c',mono=True)
# table
cols=['opt','W/finger','fingers/sub','array','sub-banks','DNW µm','DNW area','AR','guard envelope']
xs=[30,120,260,390,510,640,830,960,1080]
for i,c in enumerate(cols): txt(xs[i],100,c,10,'#475569',700,mono=True)
for j,o in enumerate(opts):
    area,Wf,nf,rows,colsx,br,bc,cw,ch,gw,gh,dw,dh,_=o
    y=125+j*24
    vals=[names[j],f'{Wf:.3f}',str(nf),f'{rows}×{colsx}',f'{br}×{bc}',f'{dw:.1f}×{dh:.1f}',f'{area:.0f}',f'{dw/dh:.2f}',f'{dw+8:.1f}×{dh+8:.1f}']
    for i,v in enumerate(vals): txt(xs[i],y,v,9,'#334155',400,mono=True)
# panels
panel_w=400; panel_h=760; ox=30; oy=250
for j,o in enumerate(opts):
    area,Wf,nf,rows,colsx,br,bc,cw,ch,gw,gh,dw,dh,_=o
    px=ox+j*(panel_w+18); py=oy
    rect(px,py,panel_w,panel_h,'#fff','#cbd5e1',1)
    txt(px+14,py+24,f'{names[j]} — W={Wf:.2f} µm',13,'#0f172a',700,mono=True)
    txt(px+14,py+42,f'{nf}/sub · {rows}×{colsx} · {br}×{bc} sub-banks',8,'#475569',400,mono=True)
    # draw DNW scaled to panel
    sx=(panel_w-40)/max(dw,dh); sy=(panel_h-125)/max(dw,dh)
    s=min(sx,sy)
    dx=px+(panel_w-dw*s)/2; dy=py+65
    # outer guard envelope
    rect(dx-4*s,dy-4*s,dw*s+8*s,dh*s+8*s,'#fce7f3','#be185d',1.2,dash='4 2')
    rect(dx,dy,dw*s,dh*s,'none','#0f766e',1.4)
    txt(dx+3,dy-6,'DNW2 + guard',7,'#9d174d',700,mono=True)
    # body cores simplified
    for k in range(5):
        rr,cc=divmod(k,bc)
        cx=dx+(DNW_MARGIN+4+cc*(cw+2*BODY_GAP+BODY_W))*s
        cy=dy+(DNW_MARGIN+4+rr*(ch+2*BODY_GAP+BODY_W))*s
        rect(cx,cy,cw*s,ch*s,'#d1fae5','#be185d',.6)
        txt(cx+cw*s/2,cy+ch*s/2,'RING',6,'#9d174d',700,'middle',mono=True)
    txt(px+14,py+panel_h-42,f'DNW {dw:.1f}×{dh:.1f} µm · area {area:.0f} µm²',9,'#0f172a',700,mono=True)
    txt(px+14,py+panel_h-24,f'aspect {dw/dh:.2f} · guard {(dw+8):.1f}×{(dh+8):.1f}',8,'#475569',400,mono=True)
txt(30,H-32,'DNW-area differences are <7%; shape (wide/tall) is the main choice. Not GDS/DRC/LVS.',9,'#b91c1c',mono=True)
add('</svg>')
OUT.write_text('\n'.join(out),encoding='utf-8')
# JSON
JSON.write_text(json.dumps([{'option':names[j],'finger_w_um':o[1],'fingers_per_sub':o[2],'rows':o[3],'cols':o[4],'subbank_rows':o[5],'subbank_cols':o[6],'dnw_um':[o[11],o[12]],'dnw_area_um2':o[0],'dnw_aspect':o[11]/o[12]} for j,o in enumerate(opts)],indent=2)+'\n',encoding='utf-8')
print('wrote',OUT,JSON)
