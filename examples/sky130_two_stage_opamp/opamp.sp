* SKY130 two-stage Miller op-amp — name-only demo netlist
*
* Base topology and device sizes:
*   https://github.com/chennakeshavadasa/Miller-Compensated-Two-stage-OPAMP-using-SKY130PDK
*   MIT License, Copyright (c) 2024 Nithin P
*
* This is a derived educational netlist, not the original project.
* Base core: 7-transistor two-stage Miller op-amp (M1..M7 + C1).
* Added here to exercise bias/enable semantics:
*   M8_BIAS    diode-connected NMOS in the bias mirror
*   M9_EN      NMOS enable switch in the bias branch
*   M10_EN_PD  PMOS pull-up that forces the bias node off when EN=0
* I0 is kept as an ideal 30 uA bias reference so the example stays small.
* A production netlist would replace I0 with a real bias generator.
*
* No role=/match=/group= annotations: instance names are the semantic source.

.subckt sky130_two_stage_opamp vinp vinn vout vdd vss en

* input pair
M1_DP  n1  vinp  ntail  vss  nmos w=0.75u l=0.5u nf=1 m=1
M2_DP  n2  vinn  ntail  vss  nmos w=0.75u l=0.5u nf=1 m=1

* PMOS load mirror
M3_CM  n1  n1  vdd  vdd  pmos w=0.75u l=0.5u nf=1 m=1
M4_CM  n2  n1  vdd  vdd  pmos w=0.75u l=0.5u nf=1 m=1

* tail current and output stage
M5_TAIL  ntail  nbias  nsw  vss  nmos w=0.75u l=0.5u nf=1 m=1
M6_OUT   vout   n2     vdd  vdd  pmos w=8.5u  l=0.5u nf=2 m=1
M7_OUT   vout   nbias  vss  vss  nmos w=6.5u  l=0.5u nf=1 m=1

* real bias mirror + enable
M8_BIAS   nbias  nbias  nsw  vss  nmos w=0.75u l=0.5u nf=1 m=1
M9_EN     nsw    en     vss  vss  nmos w=2u    l=0.5u nf=1 m=1
M10_EN_PD nbias  en     vdd  vdd  pmos w=1u    l=0.5u nf=1 m=1

* ideal bias reference (replaced by a real bias generator in production)
I0 vdd nbias 30u

* Miller compensation (10 pF external load is a testbench element, not core area)
C1_CC n2 vout 3p

.ends sky130_two_stage_opamp
