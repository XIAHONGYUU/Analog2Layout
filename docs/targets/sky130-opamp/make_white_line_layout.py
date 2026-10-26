from html import escape
from pathlib import Path

FONT = "'Noto Sans CJK SC','Noto Sans CJK JP',sans-serif"
MONO = "'Noto Sans Mono CJK SC','Noto Sans Mono',monospace"
BG="#0A0F16"; WHITE="#F8FAFC"; MUTED="#94A3B8"; DIM="#64748B"
CYAN="#22D3EE"; AMBER="#FBBF24"; PURPLE="#A78BFA"; GREEN="#34D399"; PINK="#F472B6"; ORANGE="#F59E0B"

out=[]
def add(s): out.append(s)
def rect(x,y,w,h,fill="none",stroke=WHITE,rx=0,sw=1.6,dash=None,opacity=1):
    d=f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}"{d}/>')
def line(x1,y1,x2,y2,stroke=WHITE,sw=1.6,dash=None,opacity=1):
    d=f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" opacity="{opacity}"{d}/>')
def text(x,y,s,size=13,fill=WHITE,weight=400,anchor="start",family=FONT):
    add(f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escape(s)}</text>')
def arrow(x1,y1,x2,y2,color=WHITE,sw=1.5):
    line(x1,y1,x2,y2,color,sw)
    import math
    ang=math.atan2(y2-y1,x2-x1); L=9
    for s in (-0.5,0.5):
        add(f'<line x1="{x2}" y1="{y2}" x2="{x2-L*math.cos(ang+s)}" y2="{y2-L*math.sin(ang+s)}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/>')

def dim(x1,y1,x2,y2,label,color=MUTED):
    line(x1,y1,x2,y2,color,1)
    # ticks
    if abs(x2-x1)>abs(y2-y1):
        line(x1,y1-5,x1,y1+5,color,1); line(x2,y2-5,x2,y2+5,color,1)
        text((x1+x2)/2,y1-10,label,10,color,400,"middle",MONO)
    else:
        line(x1-5,y1,x1+5,y1,color,1); line(x2-5,y2,x2+5,y2,color,1)
        text(x1+12,(y1+y2)/2,label,10,color,400,"start",MONO)

def array(x,y,w,h,count,label,sub="",color=WHITE,fills=None):
    # device array: outer boundary + count vertical fingers + top/bottom rails
    rect(x,y,w,h,"none",color,3,2.0)
    margin=10; gap=6
    fw=(w-2*margin-(count-1)*gap)/count
    for i in range(count):
        fx=x+margin+i*(fw+gap)
        rect(fx,y+10,fw,h-20,fills or "none",color,1,1.8)
    # source/drain rails
    line(x+6,y+5,x+w-6,y+5,color,2)
    line(x+6,y+h-5,x+w-6,y+h-5,color,2)
    text(x,y-8,label,12,color,700,family=MONO)
    if sub: text(x,y+h+16,sub,10,MUTED,400,family=MONO)

def dummy(x,y,w,h):
    rect(x,y,w,h,"none",WHITE,2,1.3,"4 4")
    text(x+w/2,y+h/2+3,"DM",8,MUTED,700,"middle",MONO)

def ring(x,y,w,h,label="RING"):
    rect(x,y,w,h,"none",WHITE,8,1.4,"5 6")
    # corner ticks
    for (cx,cy,dx,dy) in [(x,y,1,1),(x+w,y,-1,1),(x,y+h,1,-1),(x+w,y+h,-1,-1)]:
        line(cx,cy,cx+16*dx,cy,WHITE,2); line(cx,cy,cx,cy+16*dy,WHITE,2)
    text(x,y-8,label,10,MUTED,600,family=MONO)

def refbox(x,y,w,h,label,sub="",color=WHITE):
    rect(x,y,w,h,"none",color,8,1.4)
    text(x+10,y+20,label,12,color,700,family=MONO)
    if sub: text(x+10,y+36,sub,9,MUTED,400,family=MONO)

W,H=1800,1100
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="SKY130 op-amp white-line layout plan">')
rect(0,0,W,H,BG)
text(48,52,"SKY130 two-stage Miller OP — white-line layout plan",32,WHITE,700)
text(48,82,"layout structure + circuit reference in one view · white lines are placement/annotation, not a legal layout",15,MUTED)
text(48,104,"v0.1 · not to scale · 10 MOS + 1 cap",11,DIM,family=MONO)

# left circuit reference panel
line(350,140,350,1010,DIM,1)
text(48,150,"CIRCUIT REFERENCE",11,MUTED,700,family=MONO)
# chain
refbox(64,180,210,48,"INP / INN","differential input",CYAN)
arrow(169,228,169,258,WHITE,1.4)
refbox(64,260,210,48,"DP  M1/M2","input pair",CYAN)
arrow(169,308,169,338,WHITE,1.4)
refbox(64,340,210,48,"CM  M3/M4","PMOS load mirror",AMBER)
arrow(169,388,169,418,WHITE,1.4)
refbox(64,420,210,48,"OUT  M6/M7","second stage",ORANGE)
arrow(169,468,169,498,WHITE,1.4)
refbox(64,500,210,48,"VOUT","output",ORANGE)
# tail/bias and en
refbox(64,620,210,48,"TAIL/BIAS  M5/M8","mirror + enable",GREEN)
arrow(169,620,169,590,WHITE,1.4)
refbox(64,700,210,48,"EN  M9/M10","active-high enable",PINK)
arrow(169,700,169,668,WHITE,1.4)
refbox(64,780,210,48,"CC  C1","3 pF Miller",PURPLE)
arrow(274,444,300,444,WHITE,1.4)
text(304,448,"to OUT node",9,MUTED,family=MONO)
# I0 note
text(64,860,"I0 ideal 30 µA",11,MUTED,600,family=MONO)
text(64,878,"real bias TBD",9,DIM,family=MONO)

# plan outer block
rect(430,180,1270,770,"none",WHITE,8,2.0)
text(446,170,"LAYOUT PLAN",11,MUTED,700,family=MONO)
text(446,944,"white = device/ring/keepout · dashed = proposed dummy or ring",10,MUTED,400,family=MONO)

# ports
text(800,160,"VDD",12,AMBER,700,"middle",MONO)
line(800,180,800,200,AMBER,2)
text(800,1015,"VSS",12,MUTED,700,"middle",MONO)
line(800,950,800,1000,MUTED,2)
text(420,520,"INP",11,CYAN,700,"end",MONO)
text(420,570,"INN",11,CYAN,700,"end",MONO)
line(430,515,520,515,CYAN,2)
line(430,565,520,565,CYAN,2)
text(1712,620,"VOUT",12,ORANGE,700,family=MONO)
line(1700,620,1740,620,ORANGE,2)
text(850,980,"EN",11,PINK,700,"middle",MONO)
line(850,950,850,990,PINK,2)

# CM region
ring(500,235,340,200,"RING")
text(500,225,"CM",13,WHITE,700,family=MONO)
array(530,270,130,120,4,"M3_CM","0.75/0.5",AMBER)
array(680,270,130,120,4,"M4_CM","0.75/0.5",AMBER)
dummy(505,285,14,70); dummy(821,285,14,70)

# DP region
ring(500,455,340,220,"RING")
text(500,445,"DP",13,WHITE,700,family=MONO)
array(530,500,130,140,4,"M1_DP","0.75/0.5",CYAN)
array(680,500,130,140,4,"M2_DP","0.75/0.5",CYAN)
dummy(505,520,14,80); dummy(821,520,14,80)

# tail / bias
text(520,690,"TAIL/BIAS",12,WHITE,700,family=MONO)
array(520,730,100,120,2,"M5_TAIL","0.75/0.5",GREEN)
array(630,730,100,120,2,"M8_BIAS","0.75/0.5",GREEN)
text(520,885,"M5/M8 ratio · single tail?",9,MUTED,family=MONO)

# enable
text(780,690,"EN",12,WHITE,700,family=MONO)
array(780,730,75,120,2,"M9_EN","2/0.5",PINK)
array(865,730,85,120,2,"M10_EN_PD","1/0.5",PINK)
text(780,885,"EN=0: M9 off · M10 pulls high",9,MUTED,family=MONO)

# CC
array(1000,490,250,240,4,"C1_CC","3 pF · area dominant",PURPLE)
text(1000,760,"output node · parasitic sensitive",9,MUTED,family=MONO)

# OUT
array(1320,320,300,180,2,"M6_OUT","PMOS · 2 fingers · wide metal",ORANGE)
array(1320,590,300,180,1,"M7_OUT","NMOS · 6.5u · wide metal",ORANGE)
text(1320,805,"wide metal / multi-via / EM",9,MUTED,family=MONO)

# I0 block
rect(910,320,90,60,"none",GREEN,5,1.2,"4 4")
text(955,348,"I0",11,GREEN,700,"middle",MONO)
text(955,366,"30 µA",9,MUTED,400,"middle",MONO)

# dimensions
dim(430,920,1700,920,"block width ~97 µm (not to scale)")
dim(1720,200,1720,900,"height ~51 µm",MUTED)

# footer
line(48,1040,1752,1040,DIM,1)
text(48,1068,"white-line layout plan · circuit reference on the left · same design, one view",11,MUTED)
text(1752,1068,"v0.1 · synthetic SKY130 target",11,DIM,400,"end")
add('</svg>')
Path('docs/targets/sky130-opamp/white-line.svg').write_text('\n'.join(out),encoding='utf-8')
print('wrote')
