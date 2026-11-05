#!/usr/bin/env python3
"""Draw resistor/capacitor bank structures (XR4/5/6, XC1/3).

Structure-level white-line intent. Not GDS/DRC/LVS.
"""
from html import escape
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
D=json.loads((ROOT/'examples/sky130_ldo_01v8/white-line-input.json').read_text())
OUT=ROOT/'examples/sky130_ldo_01v8/passive-banks'; OUT.mkdir(exist_ok=True)
RING=1.0; GAP=.8
RES={p['name']:p for p in D['passives'] if p['type']=='resistor'}
CAP={p['name']:p for p in D['passives'] if p['type']=='MIM'}

def txt(x,y,s,size=12,c='#0f172a',w=400,anchor='start',mono=False):
    fam="'DejaVu Sans Mono',monospace" if mono else "'DejaVu Sans',sans-serif"
    return f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" font-weight="{w}" fill="{c}" text-anchor="{anchor}">{escape(str(s))}</text>'
def rect(x,y,w,h,fill='none',stroke='#0f172a',sw=1,rx=0,dash=None):
    d=f' stroke-dasharray="{dash}"' if dash else ''
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'

def draw_res(name,p,path):
    bw,bh=p['footprint_um']; ow,oh=bw+2*(GAP+RING),bh+2*(GAP+RING)
    arr=p['array']; rows,cols=arr['rows'],arr['cols']; dummy=arr['dummy_cells']; active=arr['active_cells']
    Wpx,Hpx=1200,900; S=min(900/ow,600/oh,110); ox=(Wpx-ow*S)/2; oy=160
    def X(x): return ox+x*S
    def Y(y): return oy+y*S
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wpx}" height="{Hpx}" viewBox="0 0 {Wpx} {Hpx}">',rect(0,0,Wpx,Hpx,'#f8fafc','none',0)]
    out.append(txt(28,36,f'{name} — folded resistor structure',22,'#0f172a',700))
    out.append(txt(28,58,f'{arr["style"]} · {cols} columns × {rows} rows · {active} active + 2 end dummy · segment {arr["segment_length_um"]}×{arr["segment_width_um"]}',9,'#475569',mono=True))
    out.append(txt(28,76,f'footprint {bw:g}×{bh:g} · outer {ow:.2f}×{oh:.2f} · ring {RING}/{GAP} · structure only, not DRC',8,'#b91c1c',mono=True))
    out.append(rect(X(0),Y(0),ow*S,oh*S,'#fef3c7','#b45309',1.2,2))
    out.append(rect(X(RING),Y(RING),(ow-2*RING)*S,(oh-2*RING)*S,'#fff7ed','#b45309',.6,1))
    cx0,cy0=RING+GAP,RING+GAP
    out.append(rect(X(cx0),Y(cy0),bw*S,bh*S,'#fff7ed','#d97706',.6,0))
    # cells: rows x cols; segment width 0.35, length 10; row pitch = bh/rows
    cellw=bw/cols; rowh=bh/rows
    # Owner decision: only one dummy at each end of the folded chain (2 total),
    # not a top/bottom boundary stack. Active cells keep their own count.
    dummy_positions={(0,0),(rows-1,cols-1)}
    active_positions=[(r,c) for r in range(rows) for c in range(cols) if (r,c) not in dummy_positions]
    active_positions=active_positions[:active]
    for r in range(rows):
        for c in range(cols):
            x=cx0+c*cellw; y=cy0+r*rowh
            if (r,c) in dummy_positions:
                style='dm'
            elif (r,c) in active_positions:
                style='active'
            else:
                style='empty'
            if style=='empty':
                out.append(rect(X(x+.06),Y(y+.06),(cellw-.12)*S,(rowh-.12)*S,'#fff','#e2e8f0',.4,1))
                continue
            segw=min(arr['segment_length_um'],cellw*0.92); segh=arr['segment_width_um']
            sx=x+(cellw-segw)/2; sy=y+(rowh-segh)/2
            fill='#fef08a' if style=='active' else '#e2e8f0'
            stroke='#b45309' if style=='active' else '#94a3b8'
            out.append(rect(X(sx),Y(sy),segw*S,max(segh*S,3),fill,stroke,.5,1))
            if style=='dm':
                out.append(txt(X(x+cellw/2),Y(y+rowh/2)+3,'DM',5,'#64748b',700,'middle',True))
    # serpentine fold intent: connect row ends alternately, not metal
    for r in range(rows-1):
        y1=cy0+(r+.5)*rowh; y2=cy0+(r+1.5)*rowh
        x1=cx0+(.06 if r%2==0 else 1-.06)*bw
        out.append(f'<path d="M {X(x1):.1f} {Y(y1):.1f} C {X(x1):.1f} {Y((y1+y2)/2):.1f}, {X(x1):.1f} {Y((y1+y2)/2):.1f}, {X(x1):.1f} {Y(y2):.1f}" fill="none" stroke="#b45309" stroke-width="1.2" opacity="0.65"/>')
    out.append(txt(28,Hpx-54,'yellow = active resistor segment · gray DM = end dummy · ring = passive ring',8,'#64748b',mono=True))
    out.append(txt(28,Hpx-34,'No resistor-end metal / vias / connections are drawn.',8,'#b91c1c',mono=True))
    out.append('</svg>')
    path.write_text('\n'.join(out),encoding='utf-8')
    return {'name':name,'kind':'resistor','core':[bw,bh],'outer':[ow,oh],'rows':rows,'cols':cols,'active':active,'dummy':dummy}

def draw_cap(name,p,path):
    bw,bh=p['footprint_um']; ow,oh=bw+2*(GAP+RING),bh+2*(GAP+RING)
    units=p.get('m',1); Wpx,Hpx=900,760; S=min(650/ow,500/oh); ox=(Wpx-ow*S)/2; oy=150
    def X(x): return ox+x*S
    def Y(y): return oy+y*S
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wpx}" height="{Hpx}" viewBox="0 0 {Wpx} {Hpx}">',rect(0,0,Wpx,Hpx,'#f8fafc','none',0)]
    out.append(txt(28,36,f'{name} — MIM capacitor structure',22,'#0f172a',700))
    out.append(txt(28,58,f'{p["array"]["style"]} · m={units} · footprint {bw:g}×{bh:g} · ring {RING}/{GAP}',9,'#475569',mono=True))
    out.append(txt(28,76,'assumed unit stack shown; plate/contact DRC not yet checked · not GDS/DRC',8,'#b91c1c',mono=True))
    out.append(rect(X(0),Y(0),ow*S,oh*S,'#ede9fe','#6d28d9',1.2,2))
    out.append(rect(X(RING),Y(RING),(ow-2*RING)*S,(oh-2*RING)*S,'#faf5ff','#6d28d9',.6,1))
    cx0,cy0=RING+GAP,RING+GAP
    out.append(rect(X(cx0),Y(cy0),bw*S,bh*S,'#faf5ff','#7c3aed',.7,0))
    unit_h=bh/units
    for u in range(units):
        y=cy0+u*unit_h
        # bottom plate / top plate inset
        out.append(rect(X(cx0+.25),Y(y+.18), (bw-.5)*S, max((unit_h-.36)*S,3),'#ddd6fe','#6d28d9',.8,1))
        out.append(rect(X(cx0+.70),Y(y+.40), (bw-1.4)*S, max((unit_h-.80)*S,2),'#c4b5fd','#4c1d95',.6,1))
        # plate contacts/vias at edges (schematic)
        for xx in (cx0+.35,cx0+bw-.35):
            out.append(rect(X(xx-.09),Y(y+unit_h/2-.09),.18*S,.18*S,'#111827','none',0,1))
        out.append(txt(X(cx0+bw/2),Y(y+unit_h/2)+3,f'unit {u+1}',5,'#4c1d95',700,'middle',True))
    out.append(txt(28,Hpx-54,'violet = MIM plates · black = plate contact/via intent · ring = passive ring',8,'#64748b',mono=True))
    out.append(txt(28,Hpx-34,'No top-level terminal metal or connection is drawn.',8,'#b91c1c',mono=True))
    out.append('</svg>')
    path.write_text('\n'.join(out),encoding='utf-8')
    return {'name':name,'kind':'MIM','core':[bw,bh],'outer':[ow,oh],'units':units}

meta=[]
for name,p in RES.items():
    meta.append(draw_res(name,p,OUT/f'{name}.svg'))
for name,p in CAP.items():
    meta.append(draw_cap(name,p,OUT/f'{name}.svg'))
(OUT/'passive-banks.json').write_text(json.dumps(meta,indent=2)+'\n')
print('generated',len(meta))
