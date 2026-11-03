* NetlistLabel annotation overlay (PROPOSAL, NOT APPROVED)
* source: examples/sky130_ldo_01v8/ldo.sp
* design: ldo
* role= is the Analog2Layout-compatible mapping; nll_role= is the extended
* NetlistLabel role. Review annotation.md before using this in a flow.
** sch_path: /home/tim/gits/cheetah_v3_analog/dependencies/sky130_am_ip__ldo_01v8/xschem/sky130_am_ip__ldo_01v8.sch
.subckt sky130_am_ip__ldo_01v8 AVDD VOUT AVSS ENA VREF_EXT SEL_EXT DVDD DVSS
*.PININFO ENA:I AVDD:I AVSS:I VOUT:O SEL_EXT:I VREF_EXT:I DVDD:I DVSS:I
XM46 VX VBIAS_P AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=7 W=1 nf=1 m=1 role=current_mirror nll_role=current_mirror group=AMP match=LOAD_AMP
XM48 net2 net2 AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=7 W=1 nf=1 m=1 role=current_mirror nll_role=current_mirror group=AMP match=MIR_AMP_net2
XM52 VX VREF net1 AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=2 nf=1 m=1 role=input_pair nll_role=input_pair group=AMP match=DP_AMP
XM53 VY VM net1 AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=2 nf=1 m=1 role=input_pair nll_role=input_pair group=AMP match=DP_AMP
XM54 net1 VBIAS_N AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=9 W=3 nf=1 m=1 role=tail_current nll_role=tail_current group=AMP
XM55 VERR net2 AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=7 W=1 nf=1 m=1 role=current_mirror nll_role=current_mirror group=AMP match=MIR_AMP_net2
XM56 VY VBIAS_P AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=7 W=1 nf=1 m=1 role=current_mirror nll_role=current_mirror group=AMP match=LOAD_AMP
XM57 VERR VBIAS_C VY AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=cascode nll_role=cascode group=AMP match=CAS_AMP
XM58 net2 VBIAS_C VX AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=cascode nll_role=cascode group=AMP match=CAS_AMP
XM59 AVSS VERR VPASS AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=output_stage nll_role=output_stage group=OUT
XM60 VPASS VBIAS_P AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=7 W=1 nf=1 m=1 role=current_mirror nll_role=current_mirror group=OUT
XR4 VM VOUT AVSS sky130_fd_pr__res_xhigh_po_0p35 L=180 mult=1 m=1 nll_role=feedback group=FB match=FB_DIV
XR5 AVSS VM AVSS sky130_fd_pr__res_xhigh_po_0p35 L=360 mult=1 m=1 nll_role=feedback group=FB match=FB_DIV
XM61 AVDD VPASS VOUT AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=5 nf=1 m=1000 role=output_stage nll_role=pass_device group=OUT
XC1 VERR AVSS sky130_fd_pr__cap_mim_m3_1 W=15 L=15 m=3 role=decap nll_role=decap group=PASSIVE
XM62 net3 VBIAS_P AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=7 W=1 nf=1 m=1 role=current_mirror nll_role=current_mirror group=BIAS match=MIR_BIAS_VBIAS_P
XM63 VBIAS_P VBIAS_C net3 AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=cascode nll_role=cascode group=BIAS match=CAS_BIAS
XM64 net4 VBIAS_P AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=7 W=1 nf=1 m=1 role=current_mirror nll_role=current_mirror group=BIAS match=MIR_BIAS_VBIAS_P
XM65 VBIAS_N VBIAS_C net4 AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=cascode nll_role=cascode group=BIAS match=CAS_BIAS
XM66 VBIAS_P VBIAS_N net5 AVSS sky130_fd_pr__nfet_g5v0d10v5 L=9 W=1 nf=1 m=20 role=current_mirror nll_role=current_mirror group=BIAS match=MIR_BIAS_DEG
XM67 VBIAS_N VBIAS_N AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=9 W=1 nf=1 m=5 role=current_mirror nll_role=current_mirror group=BIAS match=MIR_BIAS_DEG
XM68 VBIAS_C VBIAS_C AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=10 W=1 nf=1 m=1 role=bias nll_role=bias group=BIAS
XM69 VBIAS_C VBIAS_N AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=9 W=1 nf=1 m=5 role=current_mirror nll_role=current_mirror group=BIAS
XM70 VDD_START VSTART VBIAS_N AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=bias nll_role=bias group=START
XM71 net7 net7 AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=2 W=1 nf=1 m=1 role=bias nll_role=bias group=START
XM72 net6 net6 net7 AVDD sky130_fd_pr__pfet_g5v0d10v5 L=2 W=1 nf=1 m=1 role=bias nll_role=bias group=START
XM73 VSTART VSTART net6 AVDD sky130_fd_pr__pfet_g5v0d10v5 L=2 W=1 nf=1 m=1 role=bias nll_role=bias group=START
XM74 VSTART VBIAS_N AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=9 W=1 nf=1 m=5 role=current_mirror nll_role=current_mirror group=START
XM75 NSEL_EXT sel_ext_3v3 AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=adj_switch nll_role=logic group=CTRL_SEL
XM76 NSEL_EXT sel_ext_3v3 AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=2.5 nf=1 m=1 role=adj_switch nll_role=logic group=CTRL_SEL
XM77 VREF NSEL_EXT VREF_INT AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=adj_switch nll_role=adj_switch group=CTRL_SEL
XM78 VREF sel_ext_3v3 VREF_EXT AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=adj_switch nll_role=adj_switch group=CTRL_SEL
XC3 VREF AVSS sky130_fd_pr__cap_mim_m3_1 W=5 L=5 m=1 role=decap nll_role=decap group=PASSIVE
XR6 AVSS net5 AVSS sky130_fd_pr__res_xhigh_po_0p35 L=40 mult=1 m=1 role=bias nll_role=bias group=BIAS
XM79 VREF_INT VBIAS_P AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=7 W=1 nf=1 m=1 role=current_mirror nll_role=current_mirror group=REF
XM80 net8 VREF_INT net9 AVSS sky130_fd_pr__nfet_g5v0d10v5 L=10 W=1 nf=1 m=1 role=cascode nll_role=cascode group=REF
XM81 VREF_INT VREF_INT net8 AVSS sky130_fd_pr__nfet_g5v0d10v5 L=10 W=1 nf=1 m=1 role=bias nll_role=bias group=REF
XM82 net9 VREF_INT AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=10 W=1 nf=1 m=1 role=bias nll_role=bias group=REF
XM83 NENA ena_3v3 AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=enable_switch nll_role=logic group=CTRL_EN
XM84 NENA ena_3v3 AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=2.5 nf=1 m=1 role=enable_switch nll_role=logic group=CTRL_EN
XM85 VBIAS_N NENA AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=enable_switch nll_role=enable_switch group=CTRL_EN
XM86 VBIAS_C ena_3v3 AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=enable_switch nll_role=enable_switch group=CTRL_EN
XM87 VERR NENA AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=enable_switch nll_role=enable_switch group=CTRL_EN
XM88 VBIAS_P ena_3v3 AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=enable_switch nll_role=enable_switch group=CTRL_EN
XM89 VPASS NENA AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=enable_switch nll_role=enable_switch group=CTRL_EN
XM90 VDD_START NENA AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=enable_switch nll_role=enable_switch group=CTRL_EN
x1 ENA DVDD DVSS DVSS AVDD AVDD ena_3v3 sky130_fd_sc_hvl__lsbuflv2hv_1 nll_role=logic group=CTRL_EN
x2 SEL_EXT DVDD DVSS DVSS AVDD AVDD sel_ext_3v3 sky130_fd_sc_hvl__lsbuflv2hv_1 nll_role=logic group=CTRL_SEL
.ends
.end
