* Name-only OTA — demonstrates role/match/group inference from device names.
* No role=, match= or group= annotations: real simulation/verification netlists
* often carry semantics only in the instance name.
*
* Names used here:
*   M1_DP / M2_DP    input pair, match DP
*   M3_CM / M4_CM    current mirror, match CM
*   M5_TAIL          tail current, match TAIL
*   M6_OUT / M7_OUT  output stage, group OUT
*   M8_EN / M9_ADJ   enable / trim switch
*   C1_CC            compensation capacitor

.subckt ota_named vinp vinn vout vdd vss nbias en adj

M1_DP n1 vinp ntail vss nmos w=5u l=0.5u nf=4 m=1
M2_DP n2 vinn ntail vss nmos w=5u l=0.5u nf=4 m=1

M3_CM n1 n1 vdd vdd pmos w=5u l=1u nf=2 m=1
M4_CM n2 n1 vdd vdd pmos w=5u l=1u nf=2 m=1

M5_TAIL ntail nbias vss vss nmos w=10u l=1u nf=4 m=1

M6_OUT n3 n2 vss vss nmos w=10u l=1u nf=4 m=1
M7_OUT vout n3 vdd vdd pmos w=10u l=1u nf=8 m=1

M8_EN ntail en vss vss nmos w=2u l=0.5u nf=1 m=1
M9_ADJ nbias adj vss vss nmos w=1u l=0.5u nf=1 m=1

C1_CC n2 vout 1.5p

.ends ota_named
