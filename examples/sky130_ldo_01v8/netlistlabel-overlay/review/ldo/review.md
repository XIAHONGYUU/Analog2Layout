# 人工复核包 — ldo

- 源网表：ldo.sp
- 抽查范围：20 个器件、12 个 net、8 个 port

## 先看这里

这份包用来判断 NetlistLabel 的标注是否正确。你不需要相信我；只需要逐项确认或纠正。

1. accept：预测正确。
2. correct：预测错误，改成你认为正确的值。
3. ambiguous：确实有歧义；不计入 accuracy，单独统计。
4. 不确定时优先标 ambiguous，不要为了覆盖率硬选一个。

编辑方式：

- review.csv：用 Excel/表格软件打开，改 decision 和对应字段，最方便；
- gold.json：改 decision 和 role/class/structural_role 字段；
- 只改 decision 和标签字段，不要改 predicted。

建议先看“重点确认”，再看“抽查”；端口通常最容易判断，可以先建立信心。

## 端口

| 编号 | 端口 | 方向 | 类别 | 接口 | 差分/总线 | 置信度 | 锚点 | 预测依据 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P01 | AVDD | power | power | power | — | 0.95 | XM46.s, XM46.b, XM56.s, XM56.b, XM57.b, XM58.b | PININFO direction I; net AVDD is a power rail |
| P02 | VOUT | output | signal | analog_output | — | 0.70 | XR4.n, XM61.s | PININFO direction O; direction output and no control/power token |
| P03 | AVSS | ground | ground | ground | — | 0.95 | XM48.s, XM48.b, XM52.b, XM53.b, XM54.s, XM54.b | PININFO direction I; net AVSS is a ground/body-tied rail |
| P04 | ENA | input | enable | digital_input | — | 0.90 | x1.p0 | PININFO direction I; enable token in port name ENA |
| P05 | VREF_EXT | input | reference | analog_reference | — | 0.90 | XM78.s | PININFO direction I; reference token in port name VREF_EXT |
| P06 | SEL_EXT | input | select | digital_input | — | 0.88 | x2.p0 | PININFO direction I; select/trim token in port name SEL_EXT |
| P07 | DVDD | power | power | power | — | 0.95 | x1.p1, x2.p1 | PININFO direction I; net DVDD is a power rail |
| P08 | DVSS | ground | ground | ground | — | 0.95 | x1.p2, x1.p3, x2.p2, x2.p3 | PININFO direction I; net DVSS is a ground/body-tied rail |

## 重点确认（低置信度 / 有歧义 / 高影响）

| 编号 | 器件 | 行号 | 预测 | 匹配/分组 | top/margin | 置信度 | 复核 | 证据 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D01 | XM60 | 14 | current_mirror | —/OUT | 0.50/0.10 | 0.50 | confirm | 6 pmos devices share gate VBIAS_P and source AVDD; large fan-out cluster: likely bias distribution rather than one matched mirror |
| D02 | XC1 | 18 | decap | —/PASSIVE | 0.50/0.15 | 0.50 | confirm | one terminal on rail AVSS; topology alone cannot distinguish decoupling from compensation/filtering |
| D03 | XM70 | 27 | bias | —/START | 0.55/0.20 | 0.55 | confirm | gate VSTART is a bias-like net (multiple gates and/or a diode reference) |
| D04 | XC3 | 36 | decap | —/PASSIVE | 0.50/0.15 | 0.50 | confirm | one terminal on rail AVSS; topology alone cannot distinguish decoupling from compensation/filtering |
| D05 | XM79 | 38 | current_mirror | —/REF | 0.50/0.10 | 0.50 | confirm | 6 pmos devices share gate VBIAS_P and source AVDD; large fan-out cluster: likely bias distribution rather than one matched mirror |
| D06 | XM82 | 41 | bias | —/REF | 0.55/0.20 | 0.55 | confirm | gate VREF_INT is a bias-like net (multiple gates and/or a diode reference) |

## 抽查（高置信度，用来检验自动接受部分）

| 编号 | 器件 | 行号 | 预测 | 匹配/分组 | top/margin | 置信度 | 复核 | 证据 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D01 | XM52 | 6 | input_pair | DP_AMP/AMP | 0.85/0.50 | 0.85 | auto | XM52/XM53 share source net1; gates VREF/VM are distinct; similar total width |
| D02 | XM53 | 7 | input_pair | DP_AMP/AMP | 0.85/0.50 | 0.85 | auto | XM52/XM53 share source net1; gates VREF/VM are distinct; similar total width |
| D03 | XM54 | 8 | tail_current | —/AMP | 0.90/0.55 | 0.90 | auto | drain net1 is the common source of a differential pair; source AVSS is a rail |
| D04 | XM59 | 13 | output_stage | —/OUT | 0.72/0.37 | 0.72 | auto | source VPASS is the gate net of a pass device; gate VERR is the high-impedance driver input |
| D05 | XR4 | 15 | feedback | FB_DIV/FB | 0.86/0.51 | 0.86 | auto | divider node VM drives gate of XM53; feedback resistors: XR4, XR5; match group FB_DIV: resistors share a feedback midpoint that drives a pair gate |
| D06 | XR5 | 16 | feedback | FB_DIV/FB | 0.86/0.51 | 0.86 | auto | divider node VM drives gate of XM53; feedback resistors: XR4, XR5; match group FB_DIV: resistors share a feedback midpoint that drives a pair gate |
| D07 | XM61 | 17 | pass_device | —/OUT | 0.95/0.60 | 0.95 | auto | total width 5000 um vs median 1 um; terminal on output port VOUT |
| D08 | XM46 | 4 | current_mirror | LOAD_AMP/AMP | 0.85/0.45 | 0.85 | auto | 6 pmos devices share gate VBIAS_P and source AVDD; large fan-out cluster: likely bias distribution rather than one matched mirror; match group LOAD_AMP: same type/model/gate on the two pair drains |
| D09 | XM48 | 5 | current_mirror | MIR_AMP_net2/AMP | 0.82/0.47 | 0.82 | auto | diode-connected reference of MIR_NMOS_net2_AVSS; 2 nmos devices share gate net2 and source AVSS; XM48 is the diode-connected reference |
| D10 | XM55 | 9 | current_mirror | MIR_AMP_net2/AMP | 0.82/0.47 | 0.82 | auto | 2 nmos devices share gate net2 and source AVSS; XM48 is the diode-connected reference; match group MIR_AMP_net2: same mirror gate and source in one block |
| D11 | XM56 | 10 | current_mirror | LOAD_AMP/AMP | 0.85/0.45 | 0.85 | auto | 6 pmos devices share gate VBIAS_P and source AVDD; large fan-out cluster: likely bias distribution rather than one matched mirror; match group LOAD_AMP: same type/model/gate on the two pair drains |
| D12 | XM57 | 11 | cascode | CAS_AMP/AMP | 0.82/0.47 | 0.82 | auto | source VY is the drain of XM56; gate VBIAS_C is bias-like and not the source/drain of this stack; match group CAS_AMP: two cascodes share a bias gate in the same block |
| D13 | XM58 | 12 | cascode | CAS_AMP/AMP | 0.82/0.47 | 0.82 | auto | source VX is the drain of XM46; gate VBIAS_C is bias-like and not the source/drain of this stack; match group CAS_AMP: two cascodes share a bias gate in the same block |
| D14 | XM62 | 19 | current_mirror | MIR_BIAS_VBIAS_P/BIAS | 0.75/0.35 | 0.75 | auto | 6 pmos devices share gate VBIAS_P and source AVDD; large fan-out cluster: likely bias distribution rather than one matched mirror; match group MIR_BIAS_VBIAS_P: same mirror gate and source in one block |

## 重点 net

| 编号 | net | 类别/结构角色 | block | 置信度 | 复核 | 证据 |
| --- | --- | --- | --- | --- | --- | --- |
| N01 | VERR | signal/gain_node | AMP | 0.65 | confirm | net VERR is a multi-drain high-impedance gain node |

## 抽查 net

| 编号 | net | 类别/结构角色 | block | 置信度 | 复核 | 证据 |
| --- | --- | --- | --- | --- | --- | --- |
| N01 | net1 | signal/tail | AMP | 0.85 | auto | net net1 is the common source of pair XM52/XM53 |
| N02 | VM | signal/feedback | FB | 0.80 | auto | net VM is a divider midpoint that drives a pair gate |
| N03 | VPASS | control/pass_gate | OUT | 0.80 | auto | net VPASS is the gate of a pass device |
| N04 | VBIAS_P | bias/mirror_gate | BIAS | 0.80 | auto | net VBIAS_P is shared by mirror/diode gates |
| N05 | net2 | bias/mirror_gate | AMP | 0.80 | auto | net net2 is shared by mirror/diode gates |
| N06 | VREF | reference/reference | CTRL_SEL | 0.80 | auto | net VREF is a reference name or belongs to the REF block |
| N07 | VBIAS_N | bias/mirror_gate | BIAS | 0.80 | auto | net VBIAS_N is shared by mirror/diode gates |
| N08 | VBIAS_C | bias/mirror_gate | BIAS | 0.80 | auto | net VBIAS_C is shared by mirror/diode gates |
| N09 | VDD_START | signal/startup | START | 0.75 | auto | net VDD_START belongs to the startup network |
| N10 | VSTART | signal/startup | START | 0.75 | auto | net VSTART belongs to the startup network |
| N11 | net7 | signal/startup | START | 0.75 | auto | net net7 belongs to the startup network |

## 网表上下文

器件行号对应源文件；net 的锚点表示它连接到的器件端子。

- XM52（第 6 行）：XM52 VX VREF net1 AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=2 nf=1 m=1
- XM53（第 7 行）：XM53 VY VM net1 AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=2 nf=1 m=1
- XM54（第 8 行）：XM54 net1 VBIAS_N AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=9 W=3 nf=1 m=1
- XM59（第 13 行）：XM59 AVSS VERR VPASS AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1
- XR4（第 15 行）：XR4 VM VOUT AVSS sky130_fd_pr__res_xhigh_po_0p35 L=180 mult=1 m=1
- XR5（第 16 行）：XR5 AVSS VM AVSS sky130_fd_pr__res_xhigh_po_0p35 L=360 mult=1 m=1
- XM61（第 17 行）：XM61 AVDD VPASS VOUT AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=5 nf=1 m=1000
- XM60（第 14 行）：XM60 VPASS VBIAS_P AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=7 W=1 nf=1 m=1
- XC1（第 18 行）：XC1 VERR AVSS sky130_fd_pr__cap_mim_m3_1 W=15 L=15 m=3
- XM70（第 27 行）：XM70 VDD_START VSTART VBIAS_N AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1
- XC3（第 36 行）：XC3 VREF AVSS sky130_fd_pr__cap_mim_m3_1 W=5 L=5 m=1
- XM79（第 38 行）：XM79 VREF_INT VBIAS_P AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=7 W=1 nf=1 m=1
- XM82（第 41 行）：XM82 net9 VREF_INT AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=10 W=1 nf=1 m=1
- XM46（第 4 行）：XM46 VX VBIAS_P AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=7 W=1 nf=1 m=1
- XM48（第 5 行）：XM48 net2 net2 AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=7 W=1 nf=1 m=1
- XM55（第 9 行）：XM55 VERR net2 AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=7 W=1 nf=1 m=1
- XM56（第 10 行）：XM56 VY VBIAS_P AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=7 W=1 nf=1 m=1
- XM57（第 11 行）：XM57 VERR VBIAS_C VY AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1
- XM58（第 12 行）：XM58 net2 VBIAS_C VX AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1
- XM62（第 19 行）：XM62 net3 VBIAS_P AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=7 W=1 nf=1 m=1

- net1：XM52.s, XM53.s, XM54.d
- VM：XM53.g, XR4.p, XR5.n
- VERR：XM55.d, XM57.d, XM59.g, XC1.p, XM87.d
- VPASS：XM59.s, XM60.d, XM61.g, XM89.d
- VBIAS_P：XM46.g, XM56.g, XM60.g, XM62.g, XM63.d, XM64.g, XM66.d, XM79.g, XM88.d
- net2：XM48.d, XM48.g, XM55.g, XM58.d
- VREF：XM52.g, XM77.d, XM78.d, XC3.p
- VBIAS_N：XM54.g, XM65.d, XM66.g, XM67.d, XM67.g, XM69.g, XM70.s, XM74.g, XM85.d
- VBIAS_C：XM57.g, XM58.g, XM63.g, XM65.g, XM68.d, XM68.g, XM69.d, XM86.d
- VDD_START：XM70.d, XM90.d
- VSTART：XM70.g, XM73.d, XM73.g, XM74.d
- net7：XM71.d, XM71.g, XM72.s

## 怎么评分

    python3 -m netlistlabel evaluate \
      out/v02_ldo/annotation.json \
      review/ldo_quick/review.csv \
      --out out/eval/ldo_quick

结果会给出 strict/lenient accuracy、confusion、review rate、auto precision。
这是抽样结果，不是全局准确率；但它能告诉你错在哪里、错多少。
