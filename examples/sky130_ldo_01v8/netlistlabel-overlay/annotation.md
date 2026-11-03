# NetlistLabel 标注 — ldo

> 这是**语义 overlay 提案**，不是模拟 owner 已确认的事实。原始名字保留；规范名只是可选建议；review 列与文末 review queue 需要人工确认。

## 设计概览

- 源文件: examples/sky130_ldo_01v8/ldo.sp
- 子电路: sky130_am_ip__ldo_01v8
- 端口: AVDD, VOUT, AVSS, ENA, VREF_EXT, SEL_EXT, DVDD, DVSS
- 电源/地轨: AVDD, AVSS, DVDD, DVSS
- 器件: 48 (41 MOS, 2 C, 3 R, 2 X); 端口: 8; net: 33; 功能块: 9

## 覆盖率

| 指标 | 值 |
| --- | --- |
| 端口类别覆盖率 | 8/8 = 100.0% |
| 器件 role 覆盖率 | 48/48 = 100.0% |
| MOS role 覆盖率 | 41/41 = 100.0% |
| net 类别覆盖率 | 33/33 = 100.0% |
| net 结构角色覆盖率 | 33/33 = 100.0% |
| 匹配组器件 | 16 = 33.3% |
| 待确认项 | 7 (端口 0, net 1) |
| 平均置信度 | 器件 0.77, 端口 0.90, net 0.81 |
| 结构统计 | cap_to_rail: 2, cascode: 5, common_source: 12, control_switch: 8, degeneration: 1, diff_pair: 2, diode_connected: 7, inverter: 4, level_shift: 2, mirror_candidate: 1, mirror_member: 9, mirror_reference: 2, mux: 2, pass: 1, pass_driver: 1, series_divider: 2, source_follower: 1, stack_member: 5, tail: 1 |

## 端口

| 端口 | 方向 | 类别 | 接口 | 数量 | 极性 | 差分/总线 | 置信度 | 复核 | 证据 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AVDD | power | power | power | voltage | unknown | — | 0.95 | auto | PININFO direction I; net AVDD is a power rail |
| VOUT | output | signal | analog_output | voltage | unknown | — | 0.70 | auto | PININFO direction O; direction output and no control/power token |
| AVSS | ground | ground | ground | voltage | unknown | — | 0.95 | auto | PININFO direction I; net AVSS is a ground/body-tied rail |
| ENA | input | enable | digital_input | digital | unknown | — | 0.90 | auto | PININFO direction I; enable token in port name ENA |
| VREF_EXT | input | reference | analog_reference | voltage | unknown | — | 0.90 | auto | PININFO direction I; reference token in port name VREF_EXT |
| SEL_EXT | input | select | digital_input | digital | unknown | — | 0.88 | auto | PININFO direction I; select/trim token in port name SEL_EXT |
| DVDD | power | power | power | voltage | unknown | — | 0.95 | auto | PININFO direction I; net DVDD is a power rail |
| DVSS | ground | ground | ground | voltage | unknown | — | 0.95 | auto | PININFO direction I; net DVSS is a ground/body-tied rail |

## Net

| net | 端口 | 类别 | 结构角色 | 差分/总线 | block | 置信度 | 复核 | 证据 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| VX | — | signal | cascode_mid | DP_AMP | AMP | 0.75 | auto | net VX is the source of a cascode device; differential group DP_AMP from pair XM52/XM53 |
| VBIAS_P | — | signal | mirror_gate | — | BIAS | 0.80 | auto | net VBIAS_P is a cascode output and drives a common-source gate |
| AVDD | yes | power | supply | — | — | 0.95 | auto | net AVDD is an inferred rail; port class power and interface power |
| net2 | — | signal | mirror_gate | — | AMP | 0.80 | auto | net net2 is a cascode output and drives a common-source gate |
| AVSS | yes | ground | ground | — | — | 0.95 | auto | net AVSS is an inferred rail; port class ground and interface ground |
| VREF | — | reference | reference | — | CTRL_SEL | 0.80 | auto | net VREF is a reference name or belongs to the REF block |
| net1 | — | signal | tail | DP_AMP | AMP | 0.85 | auto | net net1 is the common source of pair XM52/XM53 |
| VY | — | signal | cascode_mid | DP_AMP | AMP | 0.75 | auto | net VY is the source of a cascode device; differential group DP_AMP from pair XM52/XM53 |
| VM | — | signal | feedback | — | FB | 0.80 | auto | net VM is a divider midpoint that drives a pair gate |
| VBIAS_N | — | signal | mirror_gate | — | BIAS | 0.80 | auto | net VBIAS_N is a cascode output and drives a common-source gate |
| VERR | — | signal | gain_node | — | AMP | 0.65 | confirm | net VERR is a multi-drain high-impedance gain node |
| VBIAS_C | — | bias | mirror_gate | — | BIAS | 0.80 | auto | net VBIAS_C is shared by mirror/diode gates |
| VPASS | — | control | pass_gate | — | OUT | 0.80 | auto | net VPASS is the gate of a pass device |
| VOUT | yes | signal | output | — | OUT | 0.70 | auto | port: PININFO direction O; port: direction output and no control/power token |
| net3 | — | signal | cascode_mid | — | BIAS | 0.75 | auto | net net3 is the source of a cascode device |
| net4 | — | signal | cascode_mid | — | BIAS | 0.75 | auto | net net4 is the source of a cascode device |
| net5 | — | bias | degeneration | — | BIAS | 0.70 | auto | net net5 is a source-degeneration node |
| VDD_START | — | signal | startup | — | START | 0.75 | auto | net VDD_START belongs to the startup network |
| VSTART | — | signal | startup | — | START | 0.75 | auto | net VSTART belongs to the startup network |
| net7 | — | signal | startup | — | START | 0.75 | auto | net net7 belongs to the startup network |
| net6 | — | signal | startup | — | START | 0.75 | auto | net net6 belongs to the startup network |
| NSEL_EXT | — | control | control | — | CTRL_SEL | 0.80 | auto | net NSEL_EXT is a propagated select control net |
| sel_ext_3v3 | — | control | control | — | CTRL_SEL | 0.80 | auto | net sel_ext_3v3 is a propagated select control net |
| VREF_INT | — | reference | reference | — | REF | 0.80 | auto | net VREF_INT is a reference name or belongs to the REF block |
| VREF_EXT | yes | reference | reference | — | CTRL_SEL | 0.90 | auto | port: PININFO direction I; port: reference token in port name VREF_EXT |
| net8 | — | reference | reference | — | REF | 0.80 | auto | net net8 is a reference name or belongs to the REF block |
| net9 | — | reference | reference | — | REF | 0.80 | auto | net net9 is a reference name or belongs to the REF block |
| NENA | — | control | control | — | CTRL_EN | 0.80 | auto | net NENA is a propagated enable control net |
| ena_3v3 | — | control | control | — | CTRL_EN | 0.80 | auto | net ena_3v3 is a propagated enable control net |
| ENA | yes | enable | control | — | CTRL_EN | 0.90 | auto | port: PININFO direction I; port: enable token in port name ENA |
| DVDD | yes | power | supply | — | — | 0.95 | auto | net DVDD is an inferred rail; port class power and interface power |
| DVSS | yes | ground | ground | — | — | 0.95 | auto | net DVSS is an inferred rail; port class ground and interface ground |
| SEL_EXT | yes | select | control | — | CTRL_SEL | 0.88 | auto | port: PININFO direction I; port: select/trim token in port name SEL_EXT |

## 功能块

| block | 标签 | 器件 | 置信度 | 证据 |
| --- | --- | --- | --- | --- |
| AMP | 信号路径放大级 | XM46, XM48, XM52, XM53, XM54, XM55, XM56, XM57, XM58 | 0.76 | reachable from non-rail, non-control input ports through gate/source/drain edges; excludes the pass device and its immediate gate-drive network; roles: cascode, current_mirror, input_pair, tail_current |
| OUT | 输出/功率级 | XM59, XM60, XM61 | 0.72 | contains the pass device or a device on its gate-drive net; roles: current_mirror, output_stage, pass_device |
| BIAS | 偏置网络 | XM62, XM63, XM64, XM65, XM66, XM67, XM68, XM69, XR6 | 0.70 | mirror/cascode/bias devices outside the signal path; roles: bias, cascode, current_mirror |
| REF | 基准/参考网络 | XM79, XM80, XM81, XM82 | 0.65 | devices touching a ref/vref-like net, grown through source/drain sharing; roles: bias, cascode, current_mirror |
| START | 启动/踢偏网络 | XM70, XM71, XM72, XM73, XM74 | 0.71 | devices touching a start/kick/por-like net, grown through source/drain sharing; roles: bias, current_mirror |
| CTRL_EN | 使能/掉电控制 | x1, XM83, XM84, XM85, XM86, XM87, XM88, XM89, XM90 | 0.82 | gate net propagates from an enable-like port or inverter; roles: enable_switch, logic |
| CTRL_SEL | 选择/Trim 控制 | x2, XM75, XM76, XM77, XM78 | 0.83 | gate net propagates from a select/trim-like port or inverter; roles: adj_switch, logic |
| FB | 反馈分压/补偿网络 | XR4, XR5 | 0.86 | passive devices on a divider that drives an amplifier input; roles: feedback |
| PASSIVE | 未归类无源网络 | XC1, XC3 | 0.50 | passive devices not assigned to a functional block; roles: decap |

## 器件

| 器件 | 类型 | W/L (µm) | nf/m | D | G | S | B | role | group | match | 置信度 | 复核 | 证据 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| XM46 | pmos | 1/7 | 1/1 | VX | VBIAS_P | AVDD | AVDD | current_mirror | AMP | LOAD_AMP | 0.85 | auto | 6 pmos devices share gate VBIAS_P and source AVDD; large fan-out cluster: likely bias distribution rather than one matched mirror; match group LOAD_AMP: same type/model/gate on the two pair drains |
| XM48 | nmos | 1/7 | 1/1 | net2 | net2 | AVSS | AVSS | current_mirror | AMP | MIR_AMP_net2 | 0.82 | auto | diode-connected reference of MIR_NMOS_net2_AVSS; 2 nmos devices share gate net2 and source AVSS; XM48 is the diode-connected reference |
| XM52 | nmos | 2/0.5 | 1/1 | VX | VREF | net1 | AVSS | input_pair | AMP | DP_AMP | 0.85 | auto | XM52/XM53 share source net1; gates VREF/VM are distinct; similar total width |
| XM53 | nmos | 2/0.5 | 1/1 | VY | VM | net1 | AVSS | input_pair | AMP | DP_AMP | 0.85 | auto | XM52/XM53 share source net1; gates VREF/VM are distinct; similar total width |
| XM54 | nmos | 3/9 | 1/1 | net1 | VBIAS_N | AVSS | AVSS | tail_current | AMP | — | 0.90 | auto | drain net1 is the common source of a differential pair; source AVSS is a rail |
| XM55 | nmos | 1/7 | 1/1 | VERR | net2 | AVSS | AVSS | current_mirror | AMP | MIR_AMP_net2 | 0.82 | auto | 2 nmos devices share gate net2 and source AVSS; XM48 is the diode-connected reference; source is at a rail; drain drives a load/current source (common-source stage) |
| XM56 | pmos | 1/7 | 1/1 | VY | VBIAS_P | AVDD | AVDD | current_mirror | AMP | LOAD_AMP | 0.85 | auto | 6 pmos devices share gate VBIAS_P and source AVDD; large fan-out cluster: likely bias distribution rather than one matched mirror; match group LOAD_AMP: same type/model/gate on the two pair drains |
| XM57 | pmos | 1/0.5 | 1/1 | VERR | VBIAS_C | VY | AVDD | cascode | AMP | CAS_AMP | 0.82 | auto | source VY is the drain of XM56; gate VBIAS_C is bias-like and not the source/drain of this stack; match group CAS_AMP: two cascodes share a bias gate in the same block |
| XM58 | pmos | 1/0.5 | 1/1 | net2 | VBIAS_C | VX | AVDD | cascode | AMP | CAS_AMP | 0.82 | auto | source VX is the drain of XM46; gate VBIAS_C is bias-like and not the source/drain of this stack; match group CAS_AMP: two cascodes share a bias gate in the same block |
| XM59 | pmos | 1/0.5 | 1/1 | AVSS | VERR | VPASS | AVDD | output_stage | OUT | — | 0.72 | auto | source VPASS is the gate net of a pass device; gate VERR is the high-impedance driver input; drain is at a rail/AC ground; source drives a load or the next gate (common-drain/source follower) |
| XM60 | pmos | 1/7 | 1/1 | VPASS | VBIAS_P | AVDD | AVDD | current_mirror | OUT | — | 0.50 | confirm | 6 pmos devices share gate VBIAS_P and source AVDD; large fan-out cluster: likely bias distribution rather than one matched mirror; source is at a rail; drain drives a load/current source (common-source stage) |
| XR4 | res | — | — | — | — | — | — | feedback | FB | FB_DIV | 0.86 | auto | divider node VM drives gate of XM53; feedback resistors: XR4, XR5; match group FB_DIV: resistors share a feedback midpoint that drives a pair gate |
| XR5 | res | — | — | — | — | — | — | feedback | FB | FB_DIV | 0.86 | auto | divider node VM drives gate of XM53; feedback resistors: XR4, XR5; match group FB_DIV: resistors share a feedback midpoint that drives a pair gate |
| XM61 | nmos | 5000/0.5 | 1/1000 | AVDD | VPASS | VOUT | AVSS | pass_device | OUT | — | 0.95 | auto | total width 5000 um vs median 1 um; terminal on output port VOUT |
| XC1 | cap | — | — | — | — | — | — | decap | PASSIVE | — | 0.50 | confirm | one terminal on rail AVSS; topology alone cannot distinguish decoupling from compensation/filtering |
| XM62 | pmos | 1/7 | 1/1 | net3 | VBIAS_P | AVDD | AVDD | current_mirror | BIAS | MIR_BIAS_VBIAS_P | 0.75 | auto | 6 pmos devices share gate VBIAS_P and source AVDD; large fan-out cluster: likely bias distribution rather than one matched mirror; match group MIR_BIAS_VBIAS_P: same mirror gate and source in one block |
| XM63 | pmos | 1/0.5 | 1/1 | VBIAS_P | VBIAS_C | net3 | AVDD | cascode | BIAS | CAS_BIAS | 0.82 | auto | source net3 is the drain of XM62; gate VBIAS_C is bias-like and not the source/drain of this stack; match group CAS_BIAS: two cascodes share a bias gate in the same block |
| XM64 | pmos | 1/7 | 1/1 | net4 | VBIAS_P | AVDD | AVDD | current_mirror | BIAS | MIR_BIAS_VBIAS_P | 0.75 | auto | 6 pmos devices share gate VBIAS_P and source AVDD; large fan-out cluster: likely bias distribution rather than one matched mirror; match group MIR_BIAS_VBIAS_P: same mirror gate and source in one block |
| XM65 | pmos | 1/0.5 | 1/1 | VBIAS_N | VBIAS_C | net4 | AVDD | cascode | BIAS | CAS_BIAS | 0.82 | auto | source net4 is the drain of XM64; gate VBIAS_C is bias-like and not the source/drain of this stack; match group CAS_BIAS: two cascodes share a bias gate in the same block |
| XM66 | nmos | 20/9 | 1/20 | VBIAS_P | VBIAS_N | net5 | AVSS | current_mirror | BIAS | MIR_BIAS_DEG | 0.70 | auto | shares mirror gate VBIAS_N with XM54, XM67, XM69, XM74; source net5 differs from the rail-tied mirror source; possible degeneration; match group MIR_BIAS_DEG: same mirror gate, one source rail-tied and one degenerated |
| XM67 | nmos | 5/9 | 1/5 | VBIAS_N | VBIAS_N | AVSS | AVSS | current_mirror | BIAS | MIR_BIAS_DEG | 0.82 | auto | diode-connected reference of MIR_NMOS_VBIAS_N_AVSS; 4 nmos devices share gate VBIAS_N and source AVSS; XM67 is the diode-connected reference |
| XM68 | pmos | 1/10 | 1/1 | VBIAS_C | VBIAS_C | AVDD | AVDD | bias | BIAS | — | 0.72 | auto | gate net VBIAS_C equals drain net VBIAS_C (diode-connected) |
| XM69 | nmos | 5/9 | 1/5 | VBIAS_C | VBIAS_N | AVSS | AVSS | current_mirror | BIAS | — | 0.82 | auto | 4 nmos devices share gate VBIAS_N and source AVSS; XM67 is the diode-connected reference; source is at a rail; drain drives a load/current source (common-source stage) |
| XM70 | nmos | 1/0.5 | 1/1 | VDD_START | VSTART | VBIAS_N | AVSS | bias | START | — | 0.55 | confirm | gate VSTART is a bias-like net (multiple gates and/or a diode reference) |
| XM71 | pmos | 1/2 | 1/1 | net7 | net7 | AVDD | AVDD | bias | START | — | 0.72 | auto | gate net net7 equals drain net net7 (diode-connected) |
| XM72 | pmos | 1/2 | 1/1 | net6 | net6 | net7 | AVDD | bias | START | — | 0.72 | auto | gate net net6 equals drain net net6 (diode-connected) |
| XM73 | pmos | 1/2 | 1/1 | VSTART | VSTART | net6 | AVDD | bias | START | — | 0.72 | auto | gate net VSTART equals drain net VSTART (diode-connected) |
| XM74 | nmos | 5/9 | 1/5 | VSTART | VBIAS_N | AVSS | AVSS | current_mirror | START | — | 0.82 | auto | 4 nmos devices share gate VBIAS_N and source AVSS; XM67 is the diode-connected reference |
| XM75 | nmos | 1/0.5 | 1/1 | NSEL_EXT | sel_ext_3v3 | AVSS | AVSS | logic | CTRL_SEL | — | 0.88 | auto | XM75/XM76 share gate sel_ext_3v3 and drain NSEL_EXT; XM75 source AVSS and XM76 source AVDD are opposite rails; source is at a rail; drain drives a load/current source (common-source stage) |
| XM76 | pmos | 2.5/0.5 | 1/1 | NSEL_EXT | sel_ext_3v3 | AVDD | AVDD | logic | CTRL_SEL | — | 0.88 | auto | XM75/XM76 share gate sel_ext_3v3 and drain NSEL_EXT; XM75 source AVSS and XM76 source AVDD are opposite rails; source is at a rail; drain drives a load/current source (common-source stage) |
| XM77 | nmos | 1/0.5 | 1/1 | VREF | NSEL_EXT | VREF_INT | AVSS | adj_switch | CTRL_SEL | — | 0.78 | auto | XM77/XM78 share drain VREF but select different sources VREF_INT/VREF_EXT; gates NSEL_EXT/sel_ext_3v3 are control nets |
| XM78 | nmos | 1/0.5 | 1/1 | VREF | sel_ext_3v3 | VREF_EXT | AVSS | adj_switch | CTRL_SEL | — | 0.78 | auto | XM77/XM78 share drain VREF but select different sources VREF_INT/VREF_EXT; gates NSEL_EXT/sel_ext_3v3 are control nets |
| XC3 | cap | — | — | — | — | — | — | decap | PASSIVE | — | 0.50 | confirm | one terminal on rail AVSS; topology alone cannot distinguish decoupling from compensation/filtering |
| XR6 | res | — | — | — | — | — | — | bias | BIAS | — | 0.70 | auto | one terminal on rail AVSS; other terminal net5 is the source of XM66 |
| XM79 | pmos | 1/7 | 1/1 | VREF_INT | VBIAS_P | AVDD | AVDD | current_mirror | REF | — | 0.50 | confirm | 6 pmos devices share gate VBIAS_P and source AVDD; large fan-out cluster: likely bias distribution rather than one matched mirror |
| XM80 | nmos | 1/10 | 1/1 | net8 | VREF_INT | net9 | AVSS | cascode | REF | — | 0.82 | auto | source net9 is the drain of XM82; gate VREF_INT is bias-like and not the source/drain of this stack |
| XM81 | nmos | 1/10 | 1/1 | VREF_INT | VREF_INT | net8 | AVSS | bias | REF | — | 0.72 | auto | gate net VREF_INT equals drain net VREF_INT (diode-connected) |
| XM82 | nmos | 1/10 | 1/1 | net9 | VREF_INT | AVSS | AVSS | bias | REF | — | 0.55 | confirm | gate VREF_INT is a bias-like net (multiple gates and/or a diode reference) |
| XM83 | nmos | 1/0.5 | 1/1 | NENA | ena_3v3 | AVSS | AVSS | logic | CTRL_EN | — | 0.88 | auto | XM83/XM84 share gate ena_3v3 and drain NENA; XM83 source AVSS and XM84 source AVDD are opposite rails; source is at a rail; drain drives a load/current source (common-source stage) |
| XM84 | pmos | 2.5/0.5 | 1/1 | NENA | ena_3v3 | AVDD | AVDD | logic | CTRL_EN | — | 0.88 | auto | XM83/XM84 share gate ena_3v3 and drain NENA; XM83 source AVSS and XM84 source AVDD are opposite rails; source is at a rail; drain drives a load/current source (common-source stage) |
| XM85 | nmos | 1/0.5 | 1/1 | VBIAS_N | NENA | AVSS | AVSS | enable_switch | CTRL_EN | — | 0.80 | auto | gate NENA is a enable net; NENA is the inverted output of ena_3v3 (XM83/XM84 pair); x1 (sky130_fd_sc_hvl__lsbuflv2hv_1) drives ena_3v3 from ENA |
| XM86 | pmos | 1/0.5 | 1/1 | VBIAS_C | ena_3v3 | AVDD | AVDD | enable_switch | CTRL_EN | — | 0.80 | auto | gate ena_3v3 is a enable net; x1 (sky130_fd_sc_hvl__lsbuflv2hv_1) drives ena_3v3 from ENA; control-like port name ENA |
| XM87 | nmos | 1/0.5 | 1/1 | VERR | NENA | AVSS | AVSS | enable_switch | CTRL_EN | — | 0.80 | auto | gate NENA is a enable net; NENA is the inverted output of ena_3v3 (XM83/XM84 pair); x1 (sky130_fd_sc_hvl__lsbuflv2hv_1) drives ena_3v3 from ENA |
| XM88 | pmos | 1/0.5 | 1/1 | VBIAS_P | ena_3v3 | AVDD | AVDD | enable_switch | CTRL_EN | — | 0.80 | auto | gate ena_3v3 is a enable net; x1 (sky130_fd_sc_hvl__lsbuflv2hv_1) drives ena_3v3 from ENA; control-like port name ENA |
| XM89 | nmos | 1/0.5 | 1/1 | VPASS | NENA | AVSS | AVSS | enable_switch | CTRL_EN | — | 0.80 | auto | gate NENA is a enable net; NENA is the inverted output of ena_3v3 (XM83/XM84 pair); x1 (sky130_fd_sc_hvl__lsbuflv2hv_1) drives ena_3v3 from ENA |
| XM90 | pmos | 1/0.5 | 1/1 | VDD_START | NENA | AVDD | AVDD | enable_switch | CTRL_EN | — | 0.80 | auto | gate NENA is a enable net; NENA is the inverted output of ena_3v3 (XM83/XM84 pair); x1 (sky130_fd_sc_hvl__lsbuflv2hv_1) drives ena_3v3 from ENA |
| x1 | subckt | — | — | — | — | — | — | logic | CTRL_EN | — | 0.82 | auto | digital/level-shift subcircuit sky130_fd_sc_hvl__lsbuflv2hv_1; output ena_3v3 driven from ENA; output ena_3v3 is a propagated enable control net |
| x2 | subckt | — | — | — | — | — | — | logic | CTRL_SEL | — | 0.82 | auto | digital/level-shift subcircuit sky130_fd_sc_hvl__lsbuflv2hv_1; output sel_ext_3v3 driven from SEL_EXT; output sel_ext_3v3 is a propagated select control net |

## 待确认队列

| 类型 | 名称 | role | group | 原因 | 备选 |
| --- | --- | --- | --- | --- | --- |
| device | XM60 | current_mirror | OUT | ambiguous: margin 0.10 below 0.10; confidence 0.50 below 0.70; mirror vs bias-fan-out ambiguity | bias (0.40) |
| device | XC1 | decap | PASSIVE | confidence 0.50 below 0.70; capacitance value not stated; model W/L was not converted | compensation (0.35) |
| device | XM70 | bias | START | confidence 0.55 below 0.70 | current_mirror (0.35) |
| device | XC3 | decap | PASSIVE | confidence 0.50 below 0.70; capacitance value not stated; model W/L was not converted | compensation (0.35) |
| device | XM79 | current_mirror | REF | ambiguous: margin 0.10 below 0.10; confidence 0.50 below 0.70; mirror vs bias-fan-out ambiguity | bias (0.40) |
| device | XM82 | bias | REF | confidence 0.55 below 0.70 | current_mirror (0.35) |
| net | VERR | signal | AMP | confidence 0.65 below 0.70 | gain_node (0.65) |

## 限制

- 只读拓扑，不读仿真波形、不计算小信号参数。
- 不展开层次子电路；未展开的 subckt 应标为黑盒，当前版本尚未完全实现。
- 不把 model/W/L 换算成电容或电阻值；缺省值会标为 value_known: false。
- 功能块边界是提案；边界器件（如第二级偏置二极管）可能落在相邻块。
- 规范名是可选建议；原始名字永远是下游身份。
- a2l_role 是显式映射；pass_device→output_stage，feedback/logic 无 a2l 对应。
