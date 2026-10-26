from html import escape
from pathlib import Path

FONT = "'Noto Sans CJK SC','Noto Sans CJK JP',sans-serif"
MONO = "'Noto Sans Mono CJK SC','Noto Sans Mono',monospace"
BG="#0A0F16"; WHITE="#F8FAFC"; MUTED="#94A3B8"; DIM="#64748B"
CYAN="#22D3EE"; AMBER="#FBBF24"; PURPLE="#A78BFA"; GREEN="#34D399"; PINK="#F472B6"; ORANGE="#F59E0B"

S=16.0; OX=380.0; OY=220.0
out=[]
def add(s): out.append(s)
def X(x): return OX + x*S
def Y(y): return OY + y*S
def rect_um(x,y,w,h,fill="none",stroke=WHITE,rx=0,sw=1.4,dash=None,opacity=1):
    d=f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<rect x="{X(x):.1f}" y="{Y(y):.1f}" width="{w*S:.1f}" height="{h*S:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}"{d}/>')
def line_um(x1,y1,x2,y2,stroke=WHITE,sw=1.2,dash=None):
    d=f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<line x1="{X(x1):.1f}" y1="{Y(y1):.1f}" x2="{X(x2):.1f}" y2="{Y(y2):.1f}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round"{d}/>')
def text_px(x,y,s,size=13,fill=WHITE,weight=400,anchor="start",family=FONT):
    add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escape(s)}</text>')
def text_um(x,y,s,size=11,fill=WHITE,weight=400,anchor="start",family=MONO):
    text_px(X(x),Y(y),s,size,fill,weight,anchor,family)
def arrow_px(x1,y1,x2,y2,color=WHITE,sw=1.3):
    add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/>')
    import math
    ang=math.atan2(y2-y1,x2-x1); L=8
    for s in (-0.5,0.5):
        add(f'<line x1="{x2}" y1="{y2}" x2="{x2-L*math.cos(ang+s)}" y2="{y2-L*math.sin(ang+s)}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/>')

def ring(gx,gy,gw,gh,label):
    # outer ring; 1.0 um ring width, 1.5 um gap to device
    rect_um(gx,gy,gw,gh,"none",WHITE,0,1.2)
    rect_um(gx+1.0,gy+1.0,gw-2.0,gh-2.0,"none",WHITE,0,1.2)
    text_um(gx,gy-0.55,label,9,MUTED,600)

def dev(gx,gy,dx,dy,w,h,num,color,label="",dummy=False):
    fill="#111827" if dummy else "none"
    rect_um(gx+dx,gy+dy,w,h,fill,color,1,2.0,"3 3" if dummy else None)
    # S/D rails
    line_um(gx+dx+0.15,gy+dy+0.2,gx+dx+w-0.15,gy+dy+0.2,color,1.0)
    line_um(gx+dx+0.15,gy+dy+h-0.2,gx+dx+w-0.15,gy+dy+h-0.2,color,1.0)
    text_um(gx+dx+w/2,gy+dy+h/2+0.35,num,8,color,700,"middle")
    if label:
        text_um(gx+dx,gy+dy+h+0.45,label,7.5,MUTED,400)

W,H=2000,1050
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="SKY130 op-amp strict-scale white-line layout plan">')
rect_um(-1000,-1000,5000,5000,BG)
text_px(44,48,"SKY130 two-stage Miller OP — strict-scale white-line layout plan",30,WHITE,700)
text_px(44,76,"true relative dimensions · scale bar · dummy at both W ends · separate ring per matched group · MOSCAP",13,MUTED)
text_px(44,96,"synthetic SKY130 target · educational ring width/gap · not a legal layout",10,DIM,family=MONO)

# left circuit reference
text_px(44,132,"CIRCUIT REFERENCE",10,MUTED,700,family=MONO)
def ref(x,y,w,h,label,sub,color):
    rect_um(0,0,0,0)  # no-op keeps helper use explicit
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="none" stroke="{color}" stroke-width="1.3"/>')
    text_px(x+9,y+18,label,11,color,700,family=MONO)
    text_px(x+9,y+33,sub,8,MUTED)
ref(44,150,250,44,"INP / INN","differential input",CYAN)
arrow_px(169,194,169,222,WHITE,1.2)
ref(44,222,250,44,"DP  M1/M2","input pair + DM",CYAN)
arrow_px(169,266,169,294,WHITE,1.2)
ref(44,294,250,44,"CM  M3/M4","load mirror + DM",AMBER)
arrow_px(169,338,169,366,WHITE,1.2)
ref(44,366,250,44,"OUT  M6/M7","second stage",ORANGE)
arrow_px(169,410,169,438,WHITE,1.2)
ref(44,438,250,44,"VOUT","output",ORANGE)
ref(44,520,250,44,"TAIL/BIAS  M5/M8","mirror + DM",GREEN)
arrow_px(169,520,169,490,WHITE,1.2)
ref(44,586,250,44,"EN  M9/M10","enable",PINK)
arrow_px(169,586,169,556,WHITE,1.2)
ref(44,652,250,44,"MOSCAP  C1","3 pF",PURPLE)
arrow_px(294,388,318,388,WHITE,1.2)
text_px(322,392,"to OUT node",8,MUTED,family=MONO)
text_px(44,740,"I0 ideal 30 µA",10,MUTED,600,family=MONO)
text_px(44,756,"real bias TBD",8,DIM)

# plan outer block
block_x0=-1.5; block_y0=-1.5; block_w=74.3; block_h=34.7
rect_um(block_x0,block_y0,block_w,block_h,"none",WHITE,0,1.8)
text_px(X(block_x0),Y(block_y0)-10,"LAYOUT PLAN (scale 16 px/µm)",11,MUTED,700,family=MONO)

# CM
gx,gy,gw,gh=0,0,10.28,6.25
ring(gx,gy,gw,gh,"CM RING")
dev(gx,gy,2.5,2.5,1.32,1.25,"d",WHITE,"",True)
dev(gx,gy,3.82,2.5,1.32,1.25,"1",AMBER,"")
dev(gx,gy,5.14,2.5,1.32,1.25,"2",AMBER,"")
dev(gx,gy,6.46,2.5,1.32,1.25,"d",WHITE,"",True)

# DP
gx,gy=0,8
ring(gx,gy,10.28,6.25,"DP RING")
dev(gx,gy,2.5,2.5,1.32,1.25,"d",WHITE,"",True)
dev(gx,gy,3.82,2.5,1.32,1.25,"3",CYAN,"")
dev(gx,gy,5.14,2.5,1.32,1.25,"4",CYAN,"")
dev(gx,gy,6.46,2.5,1.32,1.25,"d",WHITE,"",True)

# TAIL / BIAS
gx,gy=0,16
ring(gx,gy,10.28,6.25,"TAIL/BIAS RING")
dev(gx,gy,2.5,2.5,1.32,1.25,"d",WHITE,"",True)
dev(gx,gy,3.82,2.5,1.32,1.25,"5",GREEN,"")
dev(gx,gy,5.14,2.5,1.32,1.25,"6",GREEN,"")
dev(gx,gy,6.46,2.5,1.32,1.25,"d",WHITE,"",True)

# EN
gx,gy,gw,gh=0,23.5,7.84,7.5
ring(gx,gy,gw,gh,"EN RING")
dev(gx,gy,2.5,2.5,1.32,2.5,"7",PINK,"")
dev(gx,gy,3.82,2.5,1.32,1.5,"8",PINK,"")

# MOSCAP
cx,cy,cw,ch=12,0,47.434,31.623
rect_um(cx,cy,cw,ch,"none",PURPLE,3,2.0)
line_um(cx+2,cy+3,cx+cw-2,cy+3,PURPLE,1.4)
line_um(cx+2,cy+ch-3,cx+cw-2,cy+ch-3,PURPLE,1.4)
line_um(cx+cw/2,cy+3,cx+cw/2,cy+ch-3,PURPLE,3.0)
text_um(cx+2,cy-0.8,"C1_CC — MOSCAP",9,PURPLE,700)
text_um(cx+2,cy+6,"3 pF @ 2 fF/µm² → 1500 µm²",7.5,MUTED)
text_um(cx+2,cy+ch-5,"S/D tied",7,MUTED)

# OUT
gx,gy,gw,gh=62,0,9.26,14.0
ring(gx,gy,gw,gh,"OUT RING")
dev(gx,gy,2.5,2.5,2.64,9.0,"9",ORANGE,"")
dev(gx,gy,5.44,2.5,1.32,7.0,"10",ORANGE,"")

# ports
text_px(X(36),Y(-1.5)-12,"VDD",11,AMBER,700,"middle",MONO)
line_um(36,-1.5,36,0,AMBER,1.4)
text_px(X(36),Y(33.2)+16,"VSS",11,MUTED,700,"middle",MONO)
line_um(36,33.2,36,34.7,MUTED,1.4)
text_px(X(-1.5)-14,Y(10.5)+12,"INP",10,CYAN,700,"end",MONO)
text_px(X(-1.5)-14,Y(11.5)+12,"INN",10,CYAN,700,"end",MONO)
line_um(-1.5,10.5,0,10.5,CYAN,1.2)
line_um(-1.5,11.5,0,11.5,CYAN,1.2)
text_px(X(72.8)+10,Y(7)+4,"VOUT",10,ORANGE,700,family=MONO)
line_um(72.8,7,74.3,7,ORANGE,1.2)
text_px(X(4),Y(34.0)+4,"EN",10,PINK,700,"middle",MONO)
line_um(4,31.0,4,33.2,PINK,1.2)

# scale bar / dimensions
sx=380; sy=820
line_um(0,38,0,38,WHITE,0)  # no-op
add(f'<line x1="{sx}" y1="{sy}" x2="{sx+10*S}" y2="{sy}" stroke="{WHITE}" stroke-width="2"/>')
add(f'<line x1="{sx}" y1="{sy-5}" x2="{sx}" y2="{sy+5}" stroke="{WHITE}" stroke-width="2"/>')
add(f'<line x1="{sx+10*S}" y1="{sy-5}" x2="{sx+10*S}" y2="{sy+5}" stroke="{WHITE}" stroke-width="2"/>')
text_px(sx+10*S/2,sy-10,"10 µm",10,WHITE,600,"middle",MONO)
text_px(sx,sy+22,"scale bar · all device boxes are drawn from w_layout/h_layout",9,MUTED)

# width/height dims
add(f'<line x1="{X(block_x0)}" y1="{Y(block_y0)-28}" x2="{X(block_x0+block_w)}" y2="{Y(block_y0)-28}" stroke="{MUTED}" stroke-width="1"/>')
text_px((X(block_x0)+X(block_x0+block_w))/2,Y(block_y0)-34,f"{block_w:.1f} µm",9,MUTED,400,"middle",MONO)
add(f'<line x1="{X(block_x0+block_w)+28}" y1="{Y(block_y0)}" x2="{X(block_x0+block_w)+28}" y2="{Y(block_y0+block_h)}" stroke="{MUTED}" stroke-width="1"/>')
text_px(X(block_x0+block_w)+36,(Y(block_y0)+Y(block_y0+block_h))/2,f"{block_h:.1f} µm",9,MUTED,400,"start",MONO)

# legend
lx=1580; ly=200
text_px(lx,ly,"DEVICE LEGEND",10,MUTED,700,family=MONO)
text_px(lx,ly+18,"#   name        W/L (µm)   nf",9,DIM,400,family=MONO)
rows=[
 ("1","M3_CM","0.75/0.5","1"),("2","M4_CM","0.75/0.5","1"),
 ("3","M1_DP","0.75/0.5","1"),("4","M2_DP","0.75/0.5","1"),
 ("5","M5_TAIL","0.75/0.5","1"),("6","M8_BIAS","0.75/0.5","1"),
 ("7","M9_EN","2/0.5","1"),("8","M10_EN_PD","1/0.5","1"),
 ("9","M6_OUT","8.5/0.5","2"),("10","M7_OUT","6.5/0.5","1"),
 ("d","boundary DM","same as active","1"),
]
ry=ly+40
for n,name,wl,nf in rows:
    text_px(lx,ry,n,8,WHITE,600,family=MONO)
    text_px(lx+34,ry,name,8,WHITE,400,family=MONO)
    text_px(lx+142,ry,wl,8,MUTED,400,family=MONO)
    text_px(lx+222,ry,nf,8,MUTED,400,family=MONO)
    ry+=20
text_px(lx,ry+10,"d = dummy, same W/L, S/D shared",8,MUTED)
text_px(lx,ry+26,"ring: 1.0 µm width / 1.5 µm gap",8,MUTED)
text_px(lx,ry+42,"educational placeholder, not PDK",8,MUTED)
text_px(lx,ry+62,"DP: common-centroid / ABBA",8,MUTED)
text_px(lx,ry+78,"EN=0: M9 off / M10 high",8,MUTED)
text_px(lx,ry+94,"OUT: wide metal / vias / EM",8,MUTED)

# footer
add(f'<line x1="44" y1="1015" x2="1956" y2="1015" stroke="{DIM}" stroke-width="1"/>')
text_px(44,1040,"strict-scale sketch · device boxes from generic-180 w_layout/h_layout · not a legal layout",9,MUTED)
text_px(1956,1040,"v0.3 · synthetic SKY130 target",9,DIM,400,"end")
add('</svg>')
Path('docs/targets/sky130-opamp/white-line.svg').write_text('\n'.join(out),encoding='utf-8')
print('wrote')
