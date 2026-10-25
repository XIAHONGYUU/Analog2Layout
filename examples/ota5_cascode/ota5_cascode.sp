* Five-transistor OTA with cascode load — area/architecture comparison example
* Width convention: w is per-finger, total W = w * nf * m.

.subckt ota5_cascode vinp vinn vout vdd vss nbias vbias

M1 n3 vinp ntail vss nmos w=5u l=0.5u nf=4 m=1 role=input_pair match=DP group=IN layout=common_centroid
M2 vout vinn ntail vss nmos w=5u l=0.5u nf=4 m=1 role=input_pair match=DP group=IN layout=common_centroid

M3 n1 n1 vdd vdd pmos w=5u l=1u nf=2 m=1 role=current_mirror match=CM group=LOAD layout=interdigitated
M4 n2 n1 vdd vdd pmos w=5u l=1u nf=2 m=1 role=current_mirror match=CM group=LOAD layout=interdigitated

M6 n3 vbias n1 vdd pmos w=5u l=1u nf=2 m=1 role=cascode match=CAS group=LOAD layout=stacked
M7 vout vbias n2 vdd pmos w=5u l=1u nf=2 m=1 role=cascode match=CAS group=LOAD layout=stacked

M5 ntail nbias vss vss nmos w=10u l=1u nf=4 m=1 role=tail_current match=TAIL group=BIAS layout=common_centroid

C1 vout vss 0.5p role=compensation group=COMP

.ends ota5_cascode
