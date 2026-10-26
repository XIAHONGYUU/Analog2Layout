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

def array(x,y,w,h,count,label,sub="",color=WHITE,fill="none"):
    rect(x,y,w,h,fill,color,3,2.0)
    margin=8; gap=4
    fw=(w-2*margin-(count-1)*gap)/count
    for i in range(count):
        fx=x+margin+i*(fw+gap)
        rect(fx,y+8,fw,h-16,"none",color,1,1.7)
    line(x+5,y+4,x+w-5,y+4,color,2)
    line(x+5,y+h-4,x+w-5,y+h-4,color,2)
    text(x+2,y-7,label,10.5,color,700,family=MONO)
    if sub: text(x+2,y+h+14,sub,8.5,MUTED,400,family=MONO)

def ring(x,y,w,h,label=""):
    rect(x,y,w,h,"none",WHITE,8,1.3,"5 6")

def dm(x,y,w,h,count,label="DM"):
    array(x,y,w,h,count,label,"",WHITE)

def moscap(x,y,w,h):
    # layout-style MOSCAP: one large gate plate, S/D tied at both ends
    rect(x,y,w,h,"none",PURPLE,5,2.0)
    line(x+10,y+18,x+w-10,y+18,PURPLE,2)
    line(x+10,y+h-18,x+w-10,y+h-18,PURPLE,2)
    line(x+18,y+18,x+18,y+h-18,PURPLE,4)
    text(x+2,y-8,"C1_CC",11,PURPLE,700,family=MONO)
    text(x+2,y+22,"MOSCAP",9,PURPLE,600,family=MONO)
    text(x+2,y+h-8,"S/D tied",8,MUTED,family=MONO)

def refbox(x,y,w,h,label,sub="",color=WHITE):
    rect(x,y,w,h,"none",color,8,1.4)
    text(x+10,y+20,label,12,color,700,family=MONO)
    if sub: text(x+10,y+36,sub,9,MUTED,400,family=MONO)

W,H=1800,1100
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="SKY130 op-amp white-line layout plan v0.2">')
rect(0,0,W,H,BG)
text(48,52,"SKY130 two-stage Miller OP — white-line layout plan v0.2",31,WHITE,700)
text(48,82,"dummy at both W ends · source/drain shared · separate ring per matched group · MOSCAP C1",14,MUTED)
text(48,104,"not to scale · educational ring placeholder · MOSCAP density pending",11,DIM,family=MONO)

# left circuit reference
line(350,140,350,1010,DIM,1)
text(48,150,"CIRCUIT REFERENCE",11,MUTED,700,family=MONO)
refbox(64,180,210,48,"INP / INN","differential input",CYAN)
arrow(169,228,169,258,WHITE,1.4)
refbox(64,260,210,48,"DP  M1/M2","input pair + DM",CYAN)
arrow(169,308,169,338,WHITE,1.4)
refbox(64,340,210,48,"CM  M3/M4","load mirror + DM",AMBER)
arrow(169,388,169,418,WHITE,1.4)
refbox(64,420,210,48,"OUT  M6/M7","second stage",ORANGE)
arrow(169,468,169,498,WHITE,1.4)
refbox(64,500,210,48,"VOUT","output",ORANGE)
refbox(64,620,210,48,"TAIL/BIAS  M5/M8","mirror + DM",GREEN)
arrow(169,620,169,590,WHITE,1.4)
refbox(64,700,210,48,"EN  M9/M10","active-high enable",PINK)
arrow(169,700,169,668,WHITE,1.4)
refbox(64,780,210,48,"MOSCAP  C1","3 pF · preferred",PURPLE)
arrow(274,444,300,444,WHITE,1.4)
text(304,448,"to OUT node",9,MUTED,family=MONO)
text(64,860,"I0 ideal 30 µA",11,MUTED,600,family=MONO)
text(64,878,"real bias TBD",9,DIM,family=MONO)

# plan
rect(420,180,1260,770,"none",WHITE,8,2.0)
text(436,170,"LAYOUT PLAN",11,MUTED,700,family=MONO)
text(436,944,"solid = device / DM · dashed = ring · no legal spacing claim",10,MUTED,family=MONO)

# ports
text(900,160,"VDD",12,AMBER,700,"middle",MONO)
line(900,180,900,220,AMBER,2)
text(900,1015,"VSS",12,MUTED,700,"middle",MONO)
line(900,950,900,1000,MUTED,2)
text(408,500,"INP",11,CYAN,700,"end",MONO)
text(408,550,"INN",11,CYAN,700,"end",MONO)
line(420,495,450,495,CYAN,2)
line(420,545,450,545,CYAN,2)
text(1692,600,"VOUT",12,ORANGE,700,family=MONO)
line(1680,600,1720,600,ORANGE,2)
text(880,980,"EN",11,PINK,700,"middle",MONO)
line(880,950,880,990,PINK,2)

# CM: dummy / M3 / M4 / dummy
ring(450,225,480,175,"RING")
text(432,215,"CM",12,WHITE,700,family=MONO)
dm(470,255,85,105,4,"DM")
array(565,255,85,105,4,"M3_CM","0.75/0.5",AMBER)
array(660,255,85,105,4,"M4_CM","0.75/0.5",AMBER)
dm(755,255,85,105,4,"DM")
text(470,378,"S/D shared",8,MUTED,family=MONO)

# DP: dummy / M1 / M2 / dummy
ring(450,420,480,185,"RING")
text(432,410,"DP",12,WHITE,700,family=MONO)
dm(470,455,85,115,4,"DM")
array(565,455,85,115,4,"M1_DP","0.75/0.5",CYAN)
array(660,455,85,115,4,"M2_DP","0.75/0.5",CYAN)
dm(755,455,85,115,4,"DM")
text(470,588,"S/D shared",8,MUTED,family=MONO)

# TAIL / BIAS ring
ring(450,630,350,180,"RING")
text(432,620,"TAIL/BIAS",12,WHITE,700,family=MONO)
dm(470,665,70,100,2,"DM")
array(550,665,70,100,2,"M5_TAIL","0.75/0.5",GREEN)
array(630,665,70,100,2,"M8_BIAS","0.75/0.5",GREEN)
dm(710,665,70,100,2,"DM")
text(470,788,"M5/M8 ratio · single tail?",8,MUTED,family=MONO)

# EN ring
ring(820,630,210,180,"RING")
text(802,620,"EN",12,WHITE,700,family=MONO)
array(840,665,75,100,2,"M9_EN","2/0.5",PINK)
array(930,665,75,100,2,"M10_EN_PD","1/0.5",PINK)
text(840,788,"EN=0: M9 off · M10 high",8,MUTED,family=MONO)

# MOSCAP
moscap(1080,470,150,200)
text(1080,700,"density: 2 pF/µm² stated",8,MUTED,family=MONO)
text(1080,714,"unit check pending",8,MUTED,family=MONO)

# OUT ring
ring(1300,300,280,520,"RING")
text(1282,290,"OUT",12,WHITE,700,family=MONO)
array(1330,330,170,150,2,"M6_OUT","8.5/0.5 · nf=2",ORANGE)
array(1330,550,120,120,1,"M7_OUT","6.5/0.5",ORANGE)
text(1330,700,"wide metal / multi-via / EM",8,MUTED,family=MONO)

# I0 dashed
rect(1080,300,100,60,"none",GREEN,5,1.2,"4 4")
text(1130,330,"I0",11,GREEN,700,"middle",MONO)
text(1130,348,"30 µA",9,MUTED,400,"middle",MONO)

# ring gap note
text(450,830,"RING gap/width: educational placeholder (1.0/1.5 µm), not PDK",8,MUTED,family=MONO)

# footer
line(48,1040,1752,1040,DIM,1)
text(48,1068,"v0.2 · dummies at W ends, S/D shared, separate rings, MOSCAP · not a legal layout",10,MUTED)
text(1752,1068,"synthetic SKY130 target",10,DIM,400,"end")
add('</svg>')
Path('docs/targets/sky130-opamp/white-line.svg').write_text('\n'.join(out),encoding='utf-8')
print('wrote')
