#!/usr/bin/env python3
"""Three passive-placement study variants for the LDO FB/BIAS/REF resistors.
Illustrative placement study only; not GDS/DRC/LVS.
"""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "examples/sky130_ldo_01v8/resistor-variants.svg"
PNG = ROOT / "examples/sky130_ldo_01v8/resistor-variants.png"

W, H = 1860, 760
PW, PH = 600, 600
COL = {"amp": "#0284c7", "bias": "#059669", "ref": "#7c3aed", "fb": "#b45309", "passive": "#7c3aed"}
out = []
def add(s): out.append(s)
def rect(x,y,w,h,fill="#fff",stroke="#0f172a",sw=1.2,rx=4,dash=None):
    d=f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
def txt(x,y,s,size=14,c="#0f172a",w=400,anchor="start",mono=False):
    fam="'DejaVu Sans Mono',monospace" if mono else "'DejaVu Sans',sans-serif"
    add(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{w}" fill="{c}" text-anchor="{anchor}">{escape(str(s))}</text>')
def line(x1,y1,x2,y2,c="#0f172a",sw=1.4,dash=None):
    d=f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{sw}" stroke-linecap="round"{d}/>')
def box(x,y,w,h,label,c):
    color=COL.get(c,"#64748b")
    rect(x,y,w,h,color+"18",color,1.3)
    txt(x+w/2,y+h/2+5,label,13,color,700,"middle")
def res(x,y,w,h,name,neta,netb,c="#b45309"):
    rect(x,y,w,h,"#fef3c7",c,1.2); txt(x+w/2,y+h/2-3,name,12,c,700,"middle",True); txt(x+w/2,y+h/2+13,f"{neta}–{netb}",9,"#334155",400,"middle",True)

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
rect(0,0,W,H,"#f8fafc","none",0)
txt(30,38,"LDO passive placement / connection study",26,"#0f172a",700)
txt(30,62,"Illustrative only · netlist terminals shown · no S/D metal, contacts, DRC or LVS",10,"#b91c1c",400,mono=True)
for i,(title,sub) in enumerate([
    ("V1 — current free placement","ADJACENT BUT NOT CONNECTED"),
    ("V2 — series FB divider","SHARED VM TAP / FUNCTIONAL ZONES"),
    ("V3 — rotated FB divider","SHARED VM TAP / ALTERNATIVE ORIENTATION"),
]):
    ox=30+i*(PW+20); oy=100
    rect(ox,oy,PW,PH,"#fff","#cbd5e1",1)
    txt(ox+16,oy+28,title,16,"#0f172a",700)
    txt(ox+16,oy+48,sub,9,"#b91c1c" if i==0 else "#047857",700,mono=True)
    # DNW1 and functional zones
    rect(ox+20,oy+70,PW-40,460,"none","#0f766e",1,dash="6 3")
    txt(ox+28,oy+88,"DNW1",8,"#0f766e",700,mono=True)
    box(ox+45,oy+110,120,65,"AMP\nVERR","amp")
    box(ox+45,oy+215,120,85,"BIAS\nXM66","bias")
    box(ox+45,oy+345,120,65,"REF\nVREF","ref")
    # passive layouts differ
    if i==0:
        box(ox+270,oy+110,210,180,"FB zone","fb")
        res(ox+285,oy+145,80,55,"XR5","AVSS","VM")
        res(ox+385,oy+145,80,55,"XR4","VM","VOUT")
        rect(ox+280,oy+135,190,75,"none","#dc2626",1.2,dash="4 3")
        txt(ox+375,oy+235,"VM not drawn across two rings",9,"#b91c1c",700,"middle",True)
        res(ox+270,oy+350,110,60,"XR6","AVSS","net5")
        txt(ox+325,oy+430,"far from XM66 source",9,"#b91c1c",700,"middle",True)
        res(ox+430,oy+345,75,55,"XC1","VERR","AVSS")
        res(ox+430,oy+435,75,55,"XC3","VREF","AVSS")
        txt(ox+300,oy+520,"Verdict: placement is not connectivity-proof.",9,"#b91c1c",700,mono=True)
    elif i==1:
        # one FB ring, series divider
        rect(ox+255,oy+120,250,130,"#fef3c7","#b45309",1.2)
        txt(ox+380,oy+140,"FB DIVIDER · one ring",10,"#92400e",700,"middle",True)
        res(ox+270,oy+155,85,55,"XR5","AVSS","VM")
        res(ox+400,oy+155,85,55,"XR4","VM","VOUT")
        line(ox+355,oy+182,ox+400,oy+182,"#047857",2)
        txt(ox+377,oy+176,"VM",8,"#047857",700,"middle",True)
        res(ox+210,oy+225,110,55,"XR6","AVSS","net5")
        line(ox+165,oy+245,ox+210,oy+245,"#047857",2)
        txt(ox+188,oy+239,"net5",8,"#047857",700,"middle",True)
        res(ox+280,oy+470,80,55,"XC1","VERR","AVSS")
        res(ox+430,oy+470,80,55,"XC3","VREF","AVSS")
        line(ox+165,oy+140,ox+280,oy+497,"#0284c7",1,dash="3 3")
        line(ox+165,oy+377,ox+430,oy+497,"#7c3aed",1,dash="3 3")
        txt(ox+300,oy+550,"Verdict: series VM + functional zones are explicit.",9,"#047857",700,mono=True)
    else:
        rect(ox+280,oy+115,180,175,"#fef3c7","#b45309",1.2)
        txt(ox+370,oy+135,"FB DIVIDER · vertical",10,"#92400e",700,"middle",True)
        res(ox+320,oy+150,80,55,"XR5","AVSS","VM")
        res(ox+320,oy+225,80,55,"XR4","VM","VOUT")
        line(ox+360,oy+205,ox+360,oy+225,"#047857",2)
        txt(ox+370,oy+218,"VM",8,"#047857",700,"middle",True)
        res(ox+210,oy+300,110,55,"XR6","AVSS","net5")
        line(ox+165,oy+320,ox+210,oy+320,"#047857",2)
        res(ox+280,oy+470,80,55,"XC1","VERR","AVSS")
        res(ox+430,oy+470,80,55,"XC3","VREF","AVSS")
        txt(ox+300,oy+550,"Verdict: same nets; rotated FB footprint.",9,"#047857",700,mono=True)
    txt(ox+20,oy+580,"Bank boxes are schematic; R/C boxes are not GDS geometry.",8,"#64748b",400,mono=True)
add('</svg>')
OUT.write_text('\n'.join(out),encoding='utf-8')
print('wrote',OUT)
