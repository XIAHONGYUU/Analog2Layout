#!/usr/bin/env python3
"""Generate schematic bank-level MOS drawings from bank-specs.json.

Same MOS primitive as the DRC-aware NMOS_2X0.5 template: diff, vertical poly,
licon contacts, dummy cells, tap/body ring. No S/D metal, no global DNW.
"""
from html import escape
from pathlib import Path
import json, math

ROOT=Path(__file__).resolve().parents[2]
SPEC=json.loads((ROOT/'examples/sky130_ldo_01v8/bank-specs.json').read_text())
OUT=ROOT/'examples/sky130_ldo_01v8/banks'; OUT.mkdir(exist_ok=True)
# primitive DRC dimensions
SD=.30; CONT=.17; EXT=.13; SP=.27; GAP=.80; RING=.50

def geom(b):
    if b.get('kind')=='output_bank':
        return None
    L=float(b['active_l_um']); W=float(b['array']['fingers']) # placeholder overwritten below
    # W is stored per bank only indirectly; recover from members via manifest/input
    return L

def txt(x,y,s,size=12,c='#0f172a',w=400,anchor='start',mono=False):
    fam="'DejaVu Sans Mono',monospace" if mono else "'DejaVu Sans',sans-serif"
    return f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" font-weight="{w}" fill="{c}" text-anchor="{anchor}">{escape(str(s))}</text>'
def rect(x,y,w,h,fill='none',stroke='#0f172a',sw=1,rx=0,dash=None):
    d=f' stroke-dasharray="{dash}"' if dash else ''
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'

def draw_bank(name,b,path):
    # W/L from input
    D=json.loads((ROOT/'examples/sky130_ldo_01v8/white-line-input.json').read_text())
    devs={d['name']:d for d in D['devices']}
    L=float(b['active_l_um']); W=float(devs[b['members'][0]]['W_um'])
    rows=int(b['array']['rows']); cols=int(b['array']['cols'])
    ds=int(b.get('dummy',{}).get('sides',0)); dcols=2 if ds==2 else 0
    # Dummy devices use L=0.5, not the active L (owner-confirmed earlier).
    cw=L+2*SD; cwd=0.5+2*SD; ch=W+2*EXT
    widths = ([cwd] if dcols else []) + [cw]*cols + ([cwd] if dcols else [])
    slots=len(widths)
    corew=sum(widths)+(slots-1)*SP; coreh=rows*ch+(rows-1)*SP
    ow=corew+2*(GAP+RING); oh=coreh+2*(GAP+RING)
    # scale
    S=min(900/ow,620/oh,130)
    Wpx=1200; Hpx=800; ox=90; oy=150
    def X(x): return ox+x*S
    def Y(y): return oy+y*S
    def R(x,y,w,h,fill='none',stroke='#0f172a',sw=1,rx=0):
        return rect(X(x),Y(y),w*S,h*S,fill,stroke,sw,rx)
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wpx}" height="{Hpx}" viewBox="0 0 {Wpx} {Hpx}">',rect(0,0,Wpx,Hpx,'#f8fafc','none',0)]
    out.append(txt(28,36,f'{name} — bank white-line template',22,'#0f172a',700))
    out.append(txt(28,58,f'{b["type"]} · {rows}×{cols} · {L:g}/{W:g} · dummy {ds} side(s) · vertical poly',9,'#475569',mono=True))
    out.append(txt(28,76,f'core {corew:.2f}×{coreh:.2f} µm · outer {ow:.2f}×{oh:.2f} µm · schematic primitive, not full DRC',8,'#b91c1c',mono=True))
    out.append(R(0,0,ow,oh,'#d1fae5','#0f766e',1.2,2))
    out.append(R(RING,RING,ow-2*RING,oh-2*RING,'#f8fafc','#0f766e',.5,1))
    cx0,cy0=RING+GAP,RING+GAP
    out.append(R(cx0,cy0,corew,coreh,'#f8fafc','#94a3b8',.5,0))
    labels=[]
    # active names in row-major
    for r in range(rows):
        for c in range(cols):
            labels.append(b['members'][(r*cols+c)%len(b['members'])])
    # cells with dummy columns; dummy gate L is 0.5, active L is bank L.
    for r in range(rows):
        xpos=cx0
        for c,cellw in enumerate(widths):
            is_dummy = (dcols and (c == 0 or c == slots-1))
            label='DM' if is_dummy else labels[r*cols + (c-1 if dcols else c)]
            y=cy0+r*(ch+SP)
            out.append(R(xpos,y,cellw,ch,'#bbf7d0' if not is_dummy else '#e2e8f0','#16a34a' if not is_dummy else '#94a3b8',.5,0))
            cellL = 0.5 if is_dummy else L
            gx=xpos+(cellw-cellL)/2
            out.append(R(gx,y-EXT,cellL,W+2*EXT,'#fecaca' if not is_dummy else '#e2e8f0','#dc2626' if not is_dummy else '#94a3b8',.5,0))
            if not is_dummy:
                n=3 if W>=1.5 else 1
                for j in range(n):
                    yy=y+(W*(j+1)/(n+1))-CONT/2
                    for xx in (xpos+SD/2, xpos+cellw-SD/2):
                        out.append(R(xx-CONT/2,yy,CONT,CONT,'#111827','none',0,0))
                out.append(txt(X(xpos+cellw/2),Y(y)-6,label,5,'#7f1d1d',700,'middle',True))
            xpos += cellw+SP
    # distributed tap contacts on ring
    xs=[RING/2+k*.55 for k in range(int((ow-RING)/.55)+1)]
    ys=[RING/2+k*.55 for k in range(int((oh-RING)/.55)+1)]
    for x in xs:
        for y in (RING/2,oh-RING/2): out.append(R(x-CONT/2,y-CONT/2,CONT,CONT,'#0f766e','none',0,0))
    for y in ys:
        for x in (RING/2,ow-RING/2): out.append(R(x-CONT/2,y-CONT/2,CONT,CONT,'#0f766e','none',0,0))
    out.append(txt(28,720,'diff / poly / licon / dummy / tap ring · no S/D metal route · global placement and DNW are later',8,'#64748b',mono=True))
    out.append('</svg>')
    path.write_text('\n'.join(out),encoding='utf-8')
    return {'bank':name,'core_um':[corew,coreh],'outer_um':[ow,oh],'rows':rows,'cols':cols,'dummy_sides':ds,'L':L,'W':W}

def draw_pass(path):
    D=json.loads((ROOT/'examples/sky130_ldo_01v8/white-line-input.json').read_text())
    p=SPEC['banks']['PASS_XM61']
    W=float(next(d for d in D['devices'] if d['name']=='XM61')['W_um']); L=float(p['active_l_um'])
    cw=L+2*SD; ch=W+2*EXT
    # one subbank 1x34 -> core
    aw=34*cw+33*SP; ah=ch
    sw=aw+2*(GAP+RING); sh=ah+2*(GAP+RING)
    gw=2*sw+2*GAP+RING; gh=3*sh+2*(2*GAP+RING)
    dw,dh=gw+4,gh+4
    Wpx,Hpx=1200,900; S=min(900/dw,650/dh)
    ox,oy=100,150
    def X(x): return ox+x*S
    def Y(y): return oy+y*S
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wpx}" height="{Hpx}" viewBox="0 0 {Wpx} {Hpx}">',rect(0,0,Wpx,Hpx,'#f8fafc','none',0)]
    out.append(txt(28,36,'PASS_XM61 — 6 sub-bank output white-line template',22,'#0f172a',700))
    out.append(txt(28,58,f'6 × 34 fingers · W={W:g} · body ring 2.0/2.0 shared · DNW2 schematic',9,'#475569',mono=True))
    out.append(txt(28,76,'Schematic primitive only; S/D metal, DNW polygons and routing are later stages.',8,'#b91c1c',mono=True))
    # DNW2 envelope
    out.append(rect(X(0),Y(0),dw*S,dh*S,'#fce7f3','#be185d',1.2,5))
    # subbanks 3x2 shared rings (simplified)
    for k in range(6):
        rr,cc=divmod(k,2)
        x=4+cc*(sw+2*GAP+RING-2*RING); y=4+rr*(sh+2*GAP+RING-2*RING)
        out.append(rect(X(x),Y(y),sw*S,sh*S,'#d1fae5','#be185d',.7,2))
        out.append(rect(X(x+RING),Y(y+RING),(sw-2*RING)*S,(sh-2*RING)*S,'#f8fafc','#be185d',.4,1))
        out.append(txt(X(x+sw/2),Y(y+sh/2),f'XM61 #{k+1}\n34 fingers',5,'#9d174d',700,'middle',True))
    out.append('</svg>')
    path.write_text('\n'.join(out),encoding='utf-8')
    return {'bank':'PASS_XM61','core_um':[aw,ah],'outer_um':[dw,dh],'rows':1,'cols':34,'dummy_sides':0,'L':L,'W':W}

meta=[]
for name,b in SPEC['banks'].items():
    if name=='PASS_XM61':
        meta.append(draw_pass(OUT/f'{name}.svg'))
    else:
        meta.append(draw_bank(name,b,OUT/f'{name}.svg'))
(OUT/'bank-library.json').write_text(json.dumps(meta,indent=2)+'\n')
print('generated',len(meta),'banks')
