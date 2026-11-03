# 人工复核包 — ldo

- 源网表：ldo.sp
- 抽查范围：34 个器件、0 个 net、0 个 port

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

## 关键尺寸与连接

| 编号 | 器件 | 行 | W/L (µm) | nf/m | D | G | S | B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D01 | XM46 | 4 | 1/7 | 1/1 | VX | VBIAS_P | AVDD | AVDD |
| D02 | XM48 | 5 | 1/7 | 1/1 | net2 | net2 | AVSS | AVSS |
| D03 | XM55 | 9 | 1/7 | 1/1 | VERR | net2 | AVSS | AVSS |
| D04 | XM56 | 10 | 1/7 | 1/1 | VY | VBIAS_P | AVDD | AVDD |
| D05 | XM57 | 11 | 1/0.5 | 1/1 | VERR | VBIAS_C | VY | AVDD |
| D06 | XM58 | 12 | 1/0.5 | 1/1 | net2 | VBIAS_C | VX | AVDD |
| D07 | XM62 | 19 | 1/7 | 1/1 | net3 | VBIAS_P | AVDD | AVDD |
| D08 | XM63 | 20 | 1/0.5 | 1/1 | VBIAS_P | VBIAS_C | net3 | AVDD |
| D09 | XM64 | 21 | 1/7 | 1/1 | net4 | VBIAS_P | AVDD | AVDD |
| D10 | XM65 | 22 | 1/0.5 | 1/1 | VBIAS_N | VBIAS_C | net4 | AVDD |
| D11 | XM66 | 23 | 20/9 | 1/20 | VBIAS_P | VBIAS_N | net5 | AVSS |
| D12 | XM67 | 24 | 5/9 | 1/5 | VBIAS_N | VBIAS_N | AVSS | AVSS |
| D13 | XM68 | 25 | 1/10 | 1/1 | VBIAS_C | VBIAS_C | AVDD | AVDD |
| D14 | XM69 | 26 | 5/9 | 1/5 | VBIAS_C | VBIAS_N | AVSS | AVSS |
| D15 | XM83 | 42 | 1/0.5 | 1/1 | NENA | ena_3v3 | AVSS | AVSS |
| D16 | XM84 | 43 | 2.5/0.5 | 1/1 | NENA | ena_3v3 | AVDD | AVDD |
| D17 | XM85 | 44 | 1/0.5 | 1/1 | VBIAS_N | NENA | AVSS | AVSS |
| D18 | XM86 | 45 | 1/0.5 | 1/1 | VBIAS_C | ena_3v3 | AVDD | AVDD |
| D19 | XM87 | 46 | 1/0.5 | 1/1 | VERR | NENA | AVSS | AVSS |
| D20 | XM88 | 47 | 1/0.5 | 1/1 | VBIAS_P | ena_3v3 | AVDD | AVDD |
| D21 | XM89 | 48 | 1/0.5 | 1/1 | VPASS | NENA | AVSS | AVSS |
| D22 | XM90 | 49 | 1/0.5 | 1/1 | VDD_START | NENA | AVDD | AVDD |
| D23 | XM75 | 32 | 1/0.5 | 1/1 | NSEL_EXT | sel_ext_3v3 | AVSS | AVSS |
| D24 | XM76 | 33 | 2.5/0.5 | 1/1 | NSEL_EXT | sel_ext_3v3 | AVDD | AVDD |
| D25 | XM77 | 34 | 1/0.5 | 1/1 | VREF | NSEL_EXT | VREF_INT | AVSS |
| D26 | XM78 | 35 | 1/0.5 | 1/1 | VREF | sel_ext_3v3 | VREF_EXT | AVSS |
| D27 | XM79 | 38 | 1/7 | 1/1 | VREF_INT | VBIAS_P | AVDD | AVDD |
| D28 | XM80 | 39 | 1/10 | 1/1 | net8 | VREF_INT | net9 | AVSS |
| D29 | XM81 | 40 | 1/10 | 1/1 | VREF_INT | VREF_INT | net8 | AVSS |
| D30 | XM82 | 41 | 1/10 | 1/1 | net9 | VREF_INT | AVSS | AVSS |
| D31 | XM71 | 28 | 1/2 | 1/1 | net7 | net7 | AVDD | AVDD |
| D32 | XM72 | 29 | 1/2 | 1/1 | net6 | net6 | net7 | AVDD |
| D33 | XM73 | 30 | 1/2 | 1/1 | VSTART | VSTART | net6 | AVDD |
| D34 | XM74 | 31 | 5/9 | 1/5 | VSTART | VBIAS_N | AVSS | AVSS |

## 重点确认（低置信度 / 有歧义 / 高影响）

| 编号 | 器件 | 行号 | 预测 | 匹配/分组 | top/margin | 置信度 | 复核 | 证据 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D01 | XM79 | 38 | current_mirror | —/REF | 0.50/0.10 | 0.50 | confirm | 6 pmos devices share gate VBIAS_P and source AVDD; large fan-out cluster: likely bias distribution rather than one matched mirror |
| D02 | XM82 | 41 | bias | —/REF | 0.55/0.20 | 0.55 | confirm | gate VREF_INT is a bias-like net (multiple gates and/or a diode reference) |

## 抽查（高置信度，用来检验自动接受部分）

| 编号 | 器件 | 行号 | 预测 | 匹配/分组 | top/margin | 置信度 | 复核 | 证据 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D01 | XM46 | 4 | current_mirror | LOAD_AMP/AMP | 0.85/0.45 | 0.85 | auto | 6 pmos devices share gate VBIAS_P and source AVDD; large fan-out cluster: likely bias distribution rather than one matched mirror; match group LOAD_AMP: same type/model/gate on the two pair drains |
| D02 | XM48 | 5 | current_mirror | MIR_AMP_net2/AMP | 0.82/0.47 | 0.82 | auto | diode-connected reference of MIR_NMOS_net2_AVSS; 2 nmos devices share gate net2 and source AVSS; XM48 is the diode-connected reference |
| D03 | XM55 | 9 | current_mirror | MIR_AMP_net2/AMP | 0.82/0.47 | 0.82 | auto | 2 nmos devices share gate net2 and source AVSS; XM48 is the diode-connected reference; source is at a rail; drain drives a load/current source (common-source stage) |
| D04 | XM56 | 10 | current_mirror | LOAD_AMP/AMP | 0.85/0.45 | 0.85 | auto | 6 pmos devices share gate VBIAS_P and source AVDD; large fan-out cluster: likely bias distribution rather than one matched mirror; match group LOAD_AMP: same type/model/gate on the two pair drains |
| D05 | XM57 | 11 | cascode | CAS_AMP/AMP | 0.82/0.47 | 0.82 | auto | source VY is the drain of XM56; gate VBIAS_C is bias-like and not the source/drain of this stack; match group CAS_AMP: two cascodes share a bias gate in the same block |
| D06 | XM58 | 12 | cascode | CAS_AMP/AMP | 0.82/0.47 | 0.82 | auto | source VX is the drain of XM46; gate VBIAS_C is bias-like and not the source/drain of this stack; match group CAS_AMP: two cascodes share a bias gate in the same block |
| D07 | XM62 | 19 | current_mirror | MIR_BIAS_VBIAS_P/BIAS | 0.75/0.35 | 0.75 | auto | 6 pmos devices share gate VBIAS_P and source AVDD; large fan-out cluster: likely bias distribution rather than one matched mirror; match group MIR_BIAS_VBIAS_P: same mirror gate and source in one block |
| D08 | XM63 | 20 | cascode | CAS_BIAS/BIAS | 0.82/0.47 | 0.82 | auto | source net3 is the drain of XM62; gate VBIAS_C is bias-like and not the source/drain of this stack; match group CAS_BIAS: two cascodes share a bias gate in the same block |
| D09 | XM64 | 21 | current_mirror | MIR_BIAS_VBIAS_P/BIAS | 0.75/0.35 | 0.75 | auto | 6 pmos devices share gate VBIAS_P and source AVDD; large fan-out cluster: likely bias distribution rather than one matched mirror; match group MIR_BIAS_VBIAS_P: same mirror gate and source in one block |
| D10 | XM65 | 22 | cascode | CAS_BIAS/BIAS | 0.82/0.47 | 0.82 | auto | source net4 is the drain of XM64; gate VBIAS_C is bias-like and not the source/drain of this stack; match group CAS_BIAS: two cascodes share a bias gate in the same block |
| D11 | XM66 | 23 | current_mirror | MIR_BIAS_DEG/BIAS | 0.70/0.35 | 0.70 | auto | shares mirror gate VBIAS_N with XM54, XM67, XM69, XM74; source net5 differs from the rail-tied mirror source; possible degeneration; match group MIR_BIAS_DEG: same mirror gate, one source rail-tied and one degenerated |
| D12 | XM67 | 24 | current_mirror | MIR_BIAS_DEG/BIAS | 0.82/0.47 | 0.82 | auto | diode-connected reference of MIR_NMOS_VBIAS_N_AVSS; 4 nmos devices share gate VBIAS_N and source AVSS; XM67 is the diode-connected reference |
| D13 | XM68 | 25 | bias | —/BIAS | 0.72/0.27 | 0.72 | auto | gate net VBIAS_C equals drain net VBIAS_C (diode-connected) |
| D14 | XM69 | 26 | current_mirror | —/BIAS | 0.82/0.47 | 0.82 | auto | 4 nmos devices share gate VBIAS_N and source AVSS; XM67 is the diode-connected reference; source is at a rail; drain drives a load/current source (common-source stage) |
| D15 | XM83 | 42 | logic | —/CTRL_EN | 0.88/0.53 | 0.88 | auto | XM83/XM84 share gate ena_3v3 and drain NENA; XM83 source AVSS and XM84 source AVDD are opposite rails; source is at a rail; drain drives a load/current source (common-source stage) |
| D16 | XM84 | 43 | logic | —/CTRL_EN | 0.88/0.53 | 0.88 | auto | XM83/XM84 share gate ena_3v3 and drain NENA; XM83 source AVSS and XM84 source AVDD are opposite rails; source is at a rail; drain drives a load/current source (common-source stage) |
| D17 | XM85 | 44 | enable_switch | —/CTRL_EN | 0.80/0.45 | 0.80 | auto | gate NENA is a enable net; NENA is the inverted output of ena_3v3 (XM83/XM84 pair); x1 (sky130_fd_sc_hvl__lsbuflv2hv_1) drives ena_3v3 from ENA |
| D18 | XM86 | 45 | enable_switch | —/CTRL_EN | 0.80/0.45 | 0.80 | auto | gate ena_3v3 is a enable net; x1 (sky130_fd_sc_hvl__lsbuflv2hv_1) drives ena_3v3 from ENA; control-like port name ENA |
| D19 | XM87 | 46 | enable_switch | —/CTRL_EN | 0.80/0.45 | 0.80 | auto | gate NENA is a enable net; NENA is the inverted output of ena_3v3 (XM83/XM84 pair); x1 (sky130_fd_sc_hvl__lsbuflv2hv_1) drives ena_3v3 from ENA |
| D20 | XM88 | 47 | enable_switch | —/CTRL_EN | 0.80/0.45 | 0.80 | auto | gate ena_3v3 is a enable net; x1 (sky130_fd_sc_hvl__lsbuflv2hv_1) drives ena_3v3 from ENA; control-like port name ENA |
| D21 | XM89 | 48 | enable_switch | —/CTRL_EN | 0.80/0.45 | 0.80 | auto | gate NENA is a enable net; NENA is the inverted output of ena_3v3 (XM83/XM84 pair); x1 (sky130_fd_sc_hvl__lsbuflv2hv_1) drives ena_3v3 from ENA |
| D22 | XM90 | 49 | enable_switch | —/CTRL_EN | 0.80/0.45 | 0.80 | auto | gate NENA is a enable net; NENA is the inverted output of ena_3v3 (XM83/XM84 pair); x1 (sky130_fd_sc_hvl__lsbuflv2hv_1) drives ena_3v3 from ENA |
| D23 | XM75 | 32 | logic | —/CTRL_SEL | 0.88/0.53 | 0.88 | auto | XM75/XM76 share gate sel_ext_3v3 and drain NSEL_EXT; XM75 source AVSS and XM76 source AVDD are opposite rails; source is at a rail; drain drives a load/current source (common-source stage) |
| D24 | XM76 | 33 | logic | —/CTRL_SEL | 0.88/0.53 | 0.88 | auto | XM75/XM76 share gate sel_ext_3v3 and drain NSEL_EXT; XM75 source AVSS and XM76 source AVDD are opposite rails; source is at a rail; drain drives a load/current source (common-source stage) |
| D25 | XM77 | 34 | adj_switch | —/CTRL_SEL | 0.78/0.43 | 0.78 | auto | XM77/XM78 share drain VREF but select different sources VREF_INT/VREF_EXT; gates NSEL_EXT/sel_ext_3v3 are control nets |
| D26 | XM78 | 35 | adj_switch | —/CTRL_SEL | 0.78/0.43 | 0.78 | auto | XM77/XM78 share drain VREF but select different sources VREF_INT/VREF_EXT; gates NSEL_EXT/sel_ext_3v3 are control nets |
| D27 | XM80 | 39 | cascode | —/REF | 0.82/0.47 | 0.82 | auto | source net9 is the drain of XM82; gate VREF_INT is bias-like and not the source/drain of this stack |
| D28 | XM81 | 40 | bias | —/REF | 0.72/0.27 | 0.72 | auto | gate net VREF_INT equals drain net VREF_INT (diode-connected) |
| D29 | XM71 | 28 | bias | —/START | 0.72/0.27 | 0.72 | auto | gate net net7 equals drain net net7 (diode-connected) |
| D30 | XM72 | 29 | bias | —/START | 0.72/0.27 | 0.72 | auto | gate net net6 equals drain net net6 (diode-connected) |
| D31 | XM73 | 30 | bias | —/START | 0.72/0.27 | 0.72 | auto | gate net VSTART equals drain net VSTART (diode-connected) |
| D32 | XM74 | 31 | current_mirror | —/START | 0.82/0.47 | 0.82 | auto | 4 nmos devices share gate VBIAS_N and source AVSS; XM67 is the diode-connected reference |

## 重点 net

没有重点 net。

## 抽查 net

没有抽查 net。

## 网表上下文

器件行号对应源文件；net 的锚点表示它连接到的器件端子。

- XM46（第 4 行）：XM46 VX VBIAS_P AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=7 W=1 nf=1 m=1
- XM48（第 5 行）：XM48 net2 net2 AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=7 W=1 nf=1 m=1
- XM55（第 9 行）：XM55 VERR net2 AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=7 W=1 nf=1 m=1
- XM56（第 10 行）：XM56 VY VBIAS_P AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=7 W=1 nf=1 m=1
- XM57（第 11 行）：XM57 VERR VBIAS_C VY AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1
- XM58（第 12 行）：XM58 net2 VBIAS_C VX AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1
- XM62（第 19 行）：XM62 net3 VBIAS_P AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=7 W=1 nf=1 m=1
- XM63（第 20 行）：XM63 VBIAS_P VBIAS_C net3 AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1
- XM64（第 21 行）：XM64 net4 VBIAS_P AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=7 W=1 nf=1 m=1
- XM65（第 22 行）：XM65 VBIAS_N VBIAS_C net4 AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1
- XM66（第 23 行）：XM66 VBIAS_P VBIAS_N net5 AVSS sky130_fd_pr__nfet_g5v0d10v5 L=9 W=1 nf=1 m=20
- XM67（第 24 行）：XM67 VBIAS_N VBIAS_N AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=9 W=1 nf=1 m=5
- XM68（第 25 行）：XM68 VBIAS_C VBIAS_C AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=10 W=1 nf=1 m=1
- XM69（第 26 行）：XM69 VBIAS_C VBIAS_N AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=9 W=1 nf=1 m=5
- XM83（第 42 行）：XM83 NENA ena_3v3 AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1
- XM84（第 43 行）：XM84 NENA ena_3v3 AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=2.5 nf=1 m=1
- XM85（第 44 行）：XM85 VBIAS_N NENA AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1
- XM86（第 45 行）：XM86 VBIAS_C ena_3v3 AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1
- XM87（第 46 行）：XM87 VERR NENA AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1
- XM88（第 47 行）：XM88 VBIAS_P ena_3v3 AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1
- XM89（第 48 行）：XM89 VPASS NENA AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1
- XM90（第 49 行）：XM90 VDD_START NENA AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1
- XM75（第 32 行）：XM75 NSEL_EXT sel_ext_3v3 AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1
- XM76（第 33 行）：XM76 NSEL_EXT sel_ext_3v3 AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=2.5 nf=1 m=1
- XM77（第 34 行）：XM77 VREF NSEL_EXT VREF_INT AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1
- XM78（第 35 行）：XM78 VREF sel_ext_3v3 VREF_EXT AVSS sky130_fd_pr__nfet_g5v0d10v5 L=0.5 W=1 nf=1 m=1
- XM79（第 38 行）：XM79 VREF_INT VBIAS_P AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=7 W=1 nf=1 m=1
- XM80（第 39 行）：XM80 net8 VREF_INT net9 AVSS sky130_fd_pr__nfet_g5v0d10v5 L=10 W=1 nf=1 m=1
- XM81（第 40 行）：XM81 VREF_INT VREF_INT net8 AVSS sky130_fd_pr__nfet_g5v0d10v5 L=10 W=1 nf=1 m=1
- XM82（第 41 行）：XM82 net9 VREF_INT AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=10 W=1 nf=1 m=1
- XM71（第 28 行）：XM71 net7 net7 AVDD AVDD sky130_fd_pr__pfet_g5v0d10v5 L=2 W=1 nf=1 m=1
- XM72（第 29 行）：XM72 net6 net6 net7 AVDD sky130_fd_pr__pfet_g5v0d10v5 L=2 W=1 nf=1 m=1
- XM73（第 30 行）：XM73 VSTART VSTART net6 AVDD sky130_fd_pr__pfet_g5v0d10v5 L=2 W=1 nf=1 m=1
- XM74（第 31 行）：XM74 VSTART VBIAS_N AVSS AVSS sky130_fd_pr__nfet_g5v0d10v5 L=9 W=1 nf=1 m=5


## 怎么评分

    python3 -m netlistlabel evaluate \
      out/v02_ldo/annotation.json \
      review/ldo_quick/review.csv \
      --out out/eval/ldo_quick

结果会给出 strict/lenient accuracy、confusion、review rate、auto precision。
这是抽样结果，不是全局准确率；但它能告诉你错在哪里、错多少。
