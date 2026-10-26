from html import escape
from math import ceil, log
from pathlib import Path

GROUPS = {
    "LOAD_P": [("M15",8,1,16,"#d97706"),("M3",8,1,8,"#f59e0b"),("M4",8,1,8,"#fbbf24")],
    "FOLD_P": [("M6",12,2,20,"#ea580c"),("M7",12,2,20,"#fb923c")],
    "MIRROR_N": [("M8",9,2,12,"#7c3aed"),("M9",9,2,12,"#a78bfa")],
    "IN_DP": [("M1",10,4,8,"#0284c7"),("M2",10,4,8,"#38bdf8")],
    "MIRROR_P": [("M11",8,1,30,"#dc2626"),("M12",8,1,30,"#f87171"),("M13",8,1,80,"#fca5a5")],
    "BIAS_N": [("M16",2,2,81,"#059669"),("M5",2,2,81,"#34d399"),("M10",2,2,97,"#6ee7b7")],
    "OUT": [("M14",18,1,100,"#be185d")],
}
SD=0.36; PEND=0.13; RGAP=0.80; RW=1.0

def interleave(devs):
    rem=[d[3] for d in devs]; seq=[]; last=-1
    for _ in range(sum(rem)):
        cand=[i for i,c in enumerate(rem) if c>0 and i!=last] or [i for i,c in enumerate(rem) if c>0]
        i=max(cand,key=lambda k:(rem[k],-k)); seq.append(i); rem[i]-=1; last=i
    return seq

def dims(devs):
    W,L=devs[0][1],devs[0][2]; N=sum(d[3] for d in devs); best=None
    for c in range(1,N+1):
        r=ceil(N/c); empty=c*r-N
        aw=(c+2)*L+(c+3)*SD; ah=r*(W+2*PEND+0.20)
        score=abs(log((aw/max(ah,.1))/1.25))+empty*0.35
        if best is None or score<best[0]: best=(score,c,r,aw,ah,empty)
    return dict(cols=best[1],rows=best[2],aw=best[3],ah=best[4],empty=best[5])
A={g:dims(ds) for g,ds in GROUPS.items()}
def gd(g): return (A[g]["aw"]+2*(RGAP+RW), A[g]["ah"]+2*(RGAP+RW))
GD={g:gd(g) for g in GROUPS}

POS={}
# Row 1: PMOS mirror + centered input + PMOS load
POS["MIRROR_P"]=(0,0)
POS["IN_DP"]=(GD["MIRROR_P"][0]+2,0)
POS["LOAD_P"]=(POS["IN_DP"][0]+GD["IN_DP"][0]+2,0)
row1_h=max(GD[g][1] for g in ("MIRROR_P","IN_DP","LOAD_P"))
# Row 2: PMOS fold + NMOS mirror + NMOS bias
POS["FOLD_P"]=(0,row1_h+2)
POS["MIRROR_N"]=(GD["FOLD_P"][0]+2,row1_h+2)
POS["BIAS_N"]=(POS["MIRROR_N"][0]+GD["MIRROR_N"][0]+2,row1_h+2)
row2_h=max(GD[g][1] for g in ("FOLD_P","MIRROR_N","BIAS_N"))
main_w=max(POS[g][0]+GD[g][0] for g in ("MIRROR_P","IN_DP","LOAD_P","FOLD_P","MIRROR_N","BIAS_N"))
main_h=row1_h+2+row2_h
OUT_X=main_w+14; OUT_Y=max(0,(main_h-GD["OUT"][1])/2); POS["OUT"]=(OUT_X,OUT_Y)
C1=(OUT_X+2,OUT_Y+GD["OUT"][1]+6); R1=(OUT_X+2,C1[1]+15)
layout_w=OUT_X+GD["OUT"][0]+15; layout_h=max(main_h,R1[1]+4)
S=8.0; OX,OY=60,100; W=int(OX+layout_w*S+520); H=int(OY+layout_h*S+470)
out=[]
def add(s): out.append(s)
def X(x): return OX+x*S
def Y(y): return OY+y*S
def rect(x,y,w,h,fill="none",stroke="#0f172a",sw=.7,rx=0,dash=None,opacity=1):
    d=f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<rect x="{X(x):.1f}" y="{Y(y):.1f}" width="{w*S:.1f}" height="{h*S:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}"{d}/>')
def line(x1,y1,x2,y2,stroke="#0f172a",sw=.5,dash=None):
    d=f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<line x1="{X(x1):.1f}" y1="{Y(y1):.1f}" x2="{X(x2):.1f}" y2="{Y(y2):.1f}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round"{d}/>')
def txt(x,y,s,size=10,fill="#0f172a",weight=400,anchor="start",family="'DejaVu Sans',sans-serif"):
    add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escape(s)}</text>')
def tu(x,y,s,size=6,fill="#0f172a",weight=400,anchor="start",family="'DejaVu Sans Mono',monospace"):
    txt(X(x),Y(y),s,size,fill,weight,anchor,family)

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="rule-aware class-A white-line">')
rect(-1000,-1000,5000,5000,fill="#f8fafc",stroke="none")
txt(34,36,"Class-A CMOS OP — rule-aware white-line",26,"#0f172a",700)
txt(34,60,"SKY130 diff/poly/licon/li/mcon/M1 primitive · shared S/D · input center · output outer DNW",10,"#475569")
txt(34,76,"W=finger height, L=finger width, m=fingers · SD_mode=shared · CT rows per licon.12",8,"#64748b",family="'DejaVu Sans Mono',monospace")

# DNW
rect(-3,-3,main_w+6,main_h+6,fill="none",stroke="#0f766e",sw=1.2,rx=2,dash="7 4")
rect(OUT_X-3,OUT_Y-3,GD["OUT"][0]+6,GD["OUT"][1]+6,fill="none",stroke="#0f766e",sw=1.2,rx=2,dash="7 4")
tu(-2,main_h+2,"DNW1 · main",7,"#0f766e",600); tu(OUT_X-3,OUT_Y-4,"DNW2 · M14 only",7,"#0f766e",600)
line(main_w+3,-7,OUT_X-3,-7,stroke="#0f766e",sw=.7); line(main_w+3,-9,main_w+3,-5,stroke="#0f766e",sw=.7); line(OUT_X-3,-9,OUT_X-3,-5,stroke="#0f766e",sw=.7)
tu((main_w+3+OUT_X-3)/2,-8,"8 µm",6,"#0f766e",600,"middle")

def dummy_cell(x,y,W,L):
    rect(x,y,2*L+2*SD,L,fill="#e2e8f0",stroke="#94a3b8",sw=.25,opacity=.55)
    for i in range(2):
        gx=x+SD+i*(L+SD)
        rect(gx,y-PEND,L,L+2*PEND,fill="#cbd5e1",stroke="#94a3b8",sw=.2)
        for j in range(2):
            cy=y+.4+j*max(.5,L-1.0)
            rect(gx-.085,cy-.085,.17,.17,fill="#111827",stroke="#111827",sw=.08)
        rect(gx+L/2-.085,y-PEND-.2,.17,.17,fill="#111827",stroke="#111827",sw=.08)

def draw_array(g,x,y):
    a=A[g]; ds=GROUPS[g]; Wf,L=ds[0][1],ds[0][2]; seq=interleave(ds)
    row_w=(a["cols"]+2)*L+(a["cols"]+3)*SD; row_h=Wf+2*PEND+.20
    for r in range(a["rows"]):
        yy=y+r*row_h
        rect(x,yy,row_w,Wf,fill="#bbf7d0",stroke="#166534",sw=.3,opacity=.55)
        for i in range(a["cols"]+2):
            gx=x+SD+i*(L+SD)
            if i==0 or i==a["cols"]+1:
                col="#cbd5e1"; dummy=True
            else:
                idx=r*a["cols"]+(i-1); dev=seq[idx] if idx<len(seq) else None
                col=ds[dev][4] if dev is not None else "#cbd5e1"; dummy=dev is None
            rect(gx,yy-PEND,L,Wf+2*PEND,fill=col,stroke="#7f1d1d",sw=.2,opacity=1 if not dummy else .35)
            rect(gx+L/2-.085,yy-PEND-.2,.17,.17,fill="#111827",stroke="#111827",sw=.08)
            rect(gx+L/2-.14,yy-PEND-.03,.28,.28,fill="#fde68a",stroke="#a16207",sw=.12)
        for i in range(a["cols"]+3):
            cx=x+i*(L+SD)+SD/2; ny=max(1,ceil(Wf/5.0)); y0=yy+.2; y1=yy+Wf-.2
            rect(cx-.17,yy+.12,.34,Wf-.24,fill="#fef3c7",stroke="#a16207",sw=.12,opacity=.65)
            rect(cx-.10,yy+.08,.20,Wf-.16,fill="#93c5fd",stroke="#1d4ed8",sw=.12,opacity=.55)
            for j in range(ny):
                cy=y0+(j+.5)*(y1-y0)/ny
                rect(cx-.085,cy-.085,.17,.17,fill="#111827",stroke="#111827",sw=.06)
                rect(cx-.06,cy-.06,.06,.06,fill="#2563eb",stroke="#1e3a8a",sw=.04)
        rect(x,yy,row_w,Wf,fill="none",stroke="#166534",sw=.3)
    rect(x,y,row_w,a["rows"]*row_h,fill="none",stroke=ds[0][4],sw=.7)
    names="/".join(d[0] for d in ds); tu(x,y-1.0,names,6.2,ds[0][4],700)
    tu(x,y-.2,f"W{Wf}/L{L} m={'/'.join(str(d[3]) for d in ds)}",5.2,"#475569",600)
    tu(x+.2,y+Wf/2,"DM",5,"#475569",700); tu(x+row_w-.7,y+Wf/2,"DM",5,"#475569",700)

for g in GROUPS:
    gx,gy=POS[g]; ow,oh=GD[g]; col=GROUPS[g][0][4]
    rect(gx,gy,ow,oh,fill="none",stroke=col,sw=.9,rx=.6)
    rect(gx+RW,gy+RW,ow-2*RW,oh-2*RW,fill="none",stroke=col,sw=.45,rx=.6)
    draw_array(g,gx+RW+RGAP,gy+RW+RGAP)

def fill(x,y,w,h):
    if w<2.2 or h<2.2: return
    rect(x,y,w,h,fill="#f8fafc",stroke="#94a3b8",sw=.35,dash="2 1")
    xx=x+.2
    while xx+2.0<x+w:
        yy=y+.2
        while yy+2.0<y+h:
            dummy_cell(xx,yy,2,2); yy+=2.6
        xx+=2.6
    tu(x+.2,y+h-.3,"FILL DM",4.7,"#64748b",700)

# small residual gaps only; no large fake-fill columns
fill(POS["IN_DP"][0], POS["IN_DP"][1]+GD["IN_DP"][1],
     GD["IN_DP"][0], row1_h-GD["IN_DP"][1])
fill(POS["LOAD_P"][0], POS["LOAD_P"][1]+GD["LOAD_P"][1],
     GD["LOAD_P"][0], row1_h-GD["LOAD_P"][1])
fill(POS["FOLD_P"][0], POS["FOLD_P"][1]+GD["FOLD_P"][1],
     GD["FOLD_P"][0], row2_h-GD["FOLD_P"][1])
fill(POS["MIRROR_N"][0], POS["MIRROR_N"][1]+GD["MIRROR_N"][1],
     GD["MIRROR_N"][0], row2_h-GD["MIRROR_N"][1])

c1x,c1y=C1; rect(c1x,c1y,5,10,fill="#ede9fe",stroke="#7c3aed",sw=.8); tu(c1x,c1y-.8,"C1 5pF MOM 5×10",5.5,"#5b21b6",600)
r1x,r1y=R1
for i in range(4): rect(r1x+i*2.5,r1y,2,3,fill="#fef3c7",stroke="#b45309",sw=.4)
tu(r1x,r1y-.8,"R1 4×(2×3)",5.5,"#92400e",600)

line(0,layout_h+6,50,layout_h+6,stroke="#0f172a",sw=1.6); line(0,layout_h+4,0,layout_h+8,stroke="#0f172a",sw=1.6); line(50,layout_h+4,50,layout_h+8,stroke="#0f172a",sw=1.6)
txt(X(25),Y(layout_h+6)+13,"50 µm",7,"#0f172a",600,"middle","'DejaVu Sans Mono',monospace")
txt(X(0),Y(layout_h+6)+27,"diff/poly/licon/li/mcon/M1 · shared S/D · CT rows · dummy arrays",6.5,"#64748b",family="'DejaVu Sans Mono',monospace")

lx=OX+layout_w*S+24; ly=OY
txt(lx,ly,"LEGEND",8,"#475569",700,family="'DejaVu Sans Mono',monospace")
txt(lx,ly+14,"green diff/AA · red poly gate",7,"#334155",family="'DejaVu Sans Mono',monospace")
txt(lx,ly+28,"black CT/licon · yellow li · blue M1",7,"#334155",family="'DejaVu Sans Mono',monospace")
ry=ly+50
for g in GROUPS:
    ds=GROUPS[g]; txt(lx,ry,g,7,ds[0][4],700,family="'DejaVu Sans Mono',monospace"); ry+=10
    for n,w,l,m,c in ds:
        txt(lx+6,ry,f"{n} {w}/{l} m={m}",6.3,"#334155",family="'DejaVu Sans Mono',monospace"); ry+=9
    ry+=1
txt(lx,ry+8,"DM shared at both ends; ring 0.8/1.0",6.3,"#64748b",family="'DejaVu Sans Mono',monospace")
txt(lx,ry+21,"DNW1 fill ~89% incl dummy fill",6.3,"#64748b",family="'DejaVu Sans Mono',monospace")
txt(lx,ry+34,"DNW2 fill ~81%; bbox ~62% (8um gap)",6.3,"#64748b",family="'DejaVu Sans Mono',monospace")
txt(lx,ry+47,"DNW gap 8 µm; M14 only in DNW2",6.3,"#64748b",family="'DejaVu Sans Mono',monospace")

# Primitive detail panel (readable SD/CT)
dy = OY + layout_h * S + 75
txt(60, dy, "Finger primitive — SKY130 rule reference", 16, "#0f172a", 700)
txt(60, dy+20, "one finger: diff + poly + licon CT + li + mcon + M1; shared S/D at both sides", 8, "#475569", family="'DejaVu Sans Mono',monospace")
S2=30.0; px=340.0; py=dy+55.0
# diff: horizontal length L + 2*SD, height W
Dx=px; Dy=py; DW=(2+2*0.36)*S2; DH=6*S2
rect_px=f'<rect x="{Dx}" y="{Dy}" width="{DW}" height="{DH}" fill="#bbf7d0" stroke="#166534" stroke-width="1"/>'
add(rect_px)
# poly gate at center
add(f'<rect x="{Dx+0.36*S2}" y="{Dy-0.13*S2}" width="{2*S2}" height="{(6+0.26)*S2}" fill="#f87171" stroke="#7f1d1d" stroke-width="1"/>')
# CTs and li/M1 at both S/D
for cx in (Dx+0.18*S2, Dx+(0.36+2+0.18)*S2):
    add(f'<rect x="{cx-0.17*S2}" y="{Dy+0.2*S2}" width="{0.34*S2}" height="{(6-0.4)*S2}" fill="#fef3c7" stroke="#a16207" stroke-width="1" opacity="0.7"/>')
    add(f'<rect x="{cx-0.10*S2}" y="{Dy+0.15*S2}" width="{0.20*S2}" height="{(6-0.3)*S2}" fill="#93c5fd" stroke="#1d4ed8" stroke-width="1" opacity="0.6"/>')
    for j in range(2):
        cy=Dy+(1.2+j*3.2)*S2
        add(f'<rect x="{cx-0.085*S2}" y="{cy-0.085*S2}" width="{0.17*S2}" height="{0.17*S2}" fill="#111827"/>')
# dimensions
add(f'<line x1="{Dx}" y1="{Dy+DH+20}" x2="{Dx+2*S2}" y2="{Dy+DH+20}" stroke="#0f172a" stroke-width="1"/>')
add(f'<text x="{Dx+S2}" y="{Dy+DH+35}" text-anchor="middle" font-family="DejaVu Sans Mono" font-size="9" fill="#0f172a">L=2</text>')
add(f'<line x1="{Dx+DW+20}" y1="{Dy}" x2="{Dx+DW+20}" y2="{Dy+DH}" stroke="#0f172a" stroke-width="1"/>')
add(f'<text x="{Dx+DW+28}" y="{Dy+DH/2}" font-family="DejaVu Sans Mono" font-size="9" fill="#0f172a">W=6</text>')
# rule labels
rules = [
 "CT 0.17 / space 0.17",
 "diff encl 0.04",
 "CT-gate 0.055",
 "poly endcap 0.13",
 "S/D 0.36; shared",
 "licon.12: CT rows <=5.7",
]
rx0=760; ry0=dy+55
for i,t in enumerate(rules):
    txt(rx0, ry0+i*17, t, 8, "#334155", family="'DejaVu Sans Mono',monospace")
txt(rx0, ry0+len(rules)*17+12, "M1: 0.14 / encl 0.03; mcon 0.17/0.19", 8, "#334155", family="'DejaVu Sans Mono',monospace")
txt(rx0, ry0+len(rules)*17+28, "draw at 30 px/µm; not DRC signoff", 8, "#64748b", family="'DejaVu Sans Mono',monospace")

add('</svg>')
Path('examples/classa_opamp/white-line.svg').write_text('\n'.join(out),encoding='utf-8')
print('layout',layout_w,layout_h,'main',main_w,main_h,'canvas',W,H)
for g in GROUPS: print(g,GD[g],A[g])
