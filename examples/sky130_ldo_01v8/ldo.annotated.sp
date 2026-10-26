* SKY130 1.8V LDO — agent role proposal v0.1
* Source: fossi-foundation/sky130_am_ip__ldo_01v8 (Apache-2.0)
* The role=/match=/group= values below are PROPOSED by the agent from topology.
* They are not analog-approved; review before using for signoff.
** sch_path: /home/tim/gits/cheetah_v3_analog/dependencies/sky130_am_ip__ldo_01v8/xschem/sky130_am_ip__ldo_01v8.sch
.subckt sky130_am_ip__ldo_01v8 AVDD VOUT AVSS ENA VREF_EXT SEL_EXT DVDD DVSS
*.PININFO ENA:I AVDD:I AVSS:I VOUT:O SEL_EXT:I VREF_EXT:I DVDD:I DVSS:I
XM46 VX VBIAS_P AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=7 W=1 nf=1 m=1 role=current_mirror group=ERR match=LOAD layout=interdigitated
XM48 net2 net2 AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=7 W=1 nf=1 m=1 role=bias group=BIAS
XM52 VX VREF net1 AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=2 nf=1 m=1 role=input_pair group=ERR match=ERR_DP layout=common_centroid
XM53 VY VM net1 AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=2 nf=1 m=1 role=input_pair group=ERR match=ERR_DP layout=common_centroid
XM54 net1 VBIAS_N AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=9 W=3 nf=1 m=1 role=tail_current group=ERR
XM55 VERR net2 AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=7 W=1 nf=1 m=1 role=bias group=ERR
XM56 VY VBIAS_P AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=7 W=1 nf=1 m=1 role=current_mirror group=ERR match=LOAD layout=interdigitated
XM57 VERR VBIAS_C VY AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=cascode group=ERR match=CAS layout=stacked
XM58 net2 VBIAS_C VX AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=cascode group=ERR match=CAS layout=stacked
XM59 AVSS VERR VPASS AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=output_stage group=PASS_DRV
XM60 VPASS VBIAS_P AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=7 W=1 nf=1 m=1 role=current_mirror group=PASS_DRV
XR4 VM VOUT AVSS sky130_fd_pr__res_xhigh_po_0p35 L=180 mult=1 m=1
XR5 AVSS VM AVSS sky130_fd_pr__res_xhigh_po_0p35 L=360 mult=1 m=1
XM61 AVDD VPASS VOUT AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=5 nf=1 m=1000 role=output_stage group=PASS constraints=pass_device
XC1 VERR AVSS sky130_fd_pr__cap_mim_m3_1 W=15 L=15 m=3
XM62 net3 VBIAS_P AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=7 W=1 nf=1 m=1 role=current_mirror group=BIAS match=BIAS_P layout=interdigitated
XM63 VBIAS_P VBIAS_C net3 AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=cascode group=BIAS match=BIAS_C layout=stacked
XM64 net4 VBIAS_P AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=7 W=1 nf=1 m=1 role=current_mirror group=BIAS match=BIAS_P layout=interdigitated
XM65 VBIAS_N VBIAS_C net4 AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=cascode group=BIAS match=BIAS_C layout=stacked
XM66 VBIAS_P VBIAS_N net5 AVSS sky130_fd_pr__nfet_g5v0d10v5 L=9 W=1 nf=1 m=20 role=current_mirror group=BIAS match=BIAS_N layout=interdigitated
XM67 VBIAS_N VBIAS_N AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=9 W=1 nf=1 m=5 role=current_mirror group=BIAS match=BIAS_N layout=interdigitated
XM68 VBIAS_C VBIAS_C AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=10 W=1 nf=1 m=1 role=current_mirror group=BIAS
XM69 VBIAS_C VBIAS_N AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=9 W=1 nf=1 m=5 role=current_mirror group=BIAS
XM70 VDD_START VSTART VBIAS_N AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=bias group=START
XM71 net7 net7 AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=2 W=1 nf=1 m=1 role=bias group=START
XM72 net6 net6 net7 AVDD sky130_fd_pr__pfet_g5v0d10v5 L=2 W=1 nf=1 m=1 role=bias group=START
XM73 VSTART VSTART net6 AVDD sky130_fd_pr__pfet_g5v0d10v5 L=2 W=1 nf=1 m=1 role=bias group=START
XM74 VSTART VBIAS_N AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=9 W=1 nf=1 m=5 role=bias group=START
XM75 NSEL_EXT sel_ext_3v3 AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=adj_switch group=SEL
XM76 NSEL_EXT sel_ext_3v3 AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=2.5 nf=1 m=1 role=adj_switch group=SEL
XM77 VREF NSEL_EXT VREF_INT AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=adj_switch group=SEL
XM78 VREF sel_ext_3v3 VREF_EXT AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=adj_switch group=SEL
XC3 VREF AVSS sky130_fd_pr__cap_mim_m3_1 W=5 L=5 m=1
XR6 AVSS net5 AVSS sky130_fd_pr__res_xhigh_po_0p35 L=40 mult=1 m=1
XM79 VREF_INT VBIAS_P AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=7 W=1 nf=1 m=1 role=current_mirror group=REF
XM80 net8 VREF_INT net9 AVSS sky130_fd_pr__nfet_g5v0d10v5 L=10 W=1 nf=1 m=1 role=bias group=REF
XM81 VREF_INT VREF_INT net8 AVSS sky130_fd_pr__nfet_g5v0d10v5 L=10 W=1 nf=1 m=1 role=bias group=REF
XM82 net9 VREF_INT AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=10 W=1 nf=1 m=1 role=bias group=REF
XM83 NENA ena_3v3 AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=enable_switch group=EN
XM84 NENA ena_3v3 AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=2.5 nf=1 m=1 role=enable_switch group=EN
XM85 VBIAS_N NENA AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=enable_switch group=EN
XM86 VBIAS_C ena_3v3 AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=enable_switch group=EN
XM87 VERR NENA AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=enable_switch group=EN
XM88 VBIAS_P ena_3v3 AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=enable_switch group=EN
XM89 VPASS NENA AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=enable_switch group=EN
XM90 VDD_START NENA AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1 role=enable_switch group=EN
x1 ENA DVDD DVSS DVSS AVDD AVDD ena_3v3 sky130_fd_sc_hvl__lsbuflv2hv_1
x2 SEL_EXT DVDD DVSS DVSS AVDD AVDD sel_ext_3v3 sky130_fd_sc_hvl__lsbuflv2hv_1
.ends
.end
