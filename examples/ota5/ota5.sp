* Five-transistor OTA — minimal analog2layout example
* Width convention: w is per-finger, total W = w * nf * m.

.subckt ota5 vinp vinn vout vdd vss nbias

M1 n1 vinp ntail vss nmos w=5u l=0.5u nf=4 m=1 role=input_pair match=DP group=IN layout=common_centroid
M2 vout vinn ntail vss nmos w=5u l=0.5u nf=4 m=1 role=input_pair match=DP group=IN layout=common_centroid

M3 n1 n1 vdd vdd pmos w=5u l=1u nf=2 m=1 role=current_mirror match=CM group=LOAD layout=interdigitated
M4 vout n1 vdd vdd pmos w=5u l=1u nf=2 m=1 role=current_mirror match=CM group=LOAD layout=interdigitated

M5 ntail nbias vss vss nmos w=10u l=1u nf=4 m=1 role=tail_current match=TAIL group=BIAS layout=common_centroid

C1 vout vss 0.5p role=compensation group=COMP

.ends ota5
