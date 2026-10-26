# White-line layout plan — SKY130 two-stage OP

![SKY130 white-line layout plan](../../../docs/targets/sky130-opamp/white-line.png)

布局细节：

![SKY130 white-line layout detail](../../../docs/targets/sky130-opamp/white-line-detail.png)

## 这是什么

这是**版图结构的白线草图**：左边是 block-level circuit reference，右边是器件/ring/dummy 的摆放和排列方式。完整晶体管拓扑在 netlist 里，这里只保留和布局相关的电路关系。
它和电路图放在同一个视图里，但不是“在 schematic 符号上画注释框”，也不是合法版图。

- 白色实线：器件阵列、源漏条、ring、keepout；
- 白色虚线：proposed dummy / proposed ring；
- 彩色标签：功能组和 net；
- 短注释：这个组为什么这样摆、哪里不能动。

## 图上怎么读

| 区域 | 版图结构 | 说明 |
| --- | --- | --- |
| `CM` | `M3_CM` / `M4_CM` 各 4 指，左右分开 | 同 source/well，边界 `DM`；ring 包住 |
| `DP` | `M1_DP` / `M2_DP` 各 4 指 | common-centroid / ABBA，symmetric gate；ring 包住 |
| `TAIL/BIAS` | `M5_TAIL` / `M8_BIAS` 各 2 指 | M5/M8 镜像比例；single tail 是否加 dummy tail 待确认 |
| `EN` | `M9_EN` / `M10_EN_PD` 各 2 指 | EN=0：M9 off，M10 把 `nbias` 拉高 |
| `CC` | `C1_CC` 大电容阵列 | 3 pF，面积大头；靠近输出节点 |
| `OUT` | `M6_OUT` 2 指宽管 / `M7_OUT` 长管 | 宽金属、多过孔、EM/IR；不是 ESD 的 SAB 画法 |
| `I0` | 虚线理想电流源 | 30 µA，真实 bias 生成器待补 |
| `VOUT` | 右侧输出端口 | 外部 10 pF 负载是 testbench，不算 core 面积 |

## 这版故意做的选择

- 每个 MOS **单独画成阵列块**，不合并成一个“group 矩形”；
- `DP/CM` 各 4 指，先表达“可做共质心/同环境”的量级；
- `M6_OUT` 画成 2 指宽管，`M7_OUT` 画成长管，先表达输出级的宽度/长度差异；
- 这个 OP 目标没有 IO/ESD 的 SAB；如果目标是 GPIO/ESD，输出 MOS 会画得更粗更长并标 SAB；
- `C1_CC` 画成大阵列，因为当前 generic-180 下它占 device area 的 95.8%；
- `RING` 先包 `DP/CM`，`TAIL/BIAS/OUT` 的 ring 还没画。

## 当前未决

- `ASK` `RING` 只包 `DP/CM`，还是也要包 `TAIL/BIAS` / `OUT`？
- `ASK` `DP` 的 4+4 指是否按 ABBA 画，还是需要更细的交叉指状？
- `ASK` `CM` 的 4+4 指是否同 well、共享 source，边界 `DM` 是否左右各 1？
- `ASK` `M6_OUT` 的 2 指宽度/长度是否要按真实 W/L 比例画？
- `ASK` `TAIL` 单器件是否需要 dummy tail？
- `ASK` `EN` 的 M9/M10 放在左下是否合适，还是靠近 `nbias`？
- `UNKNOWN` SKY130 的 WPE/STI/ring/dummy 具体间距。

## 相关

- [Layout Card](layout-card.md)
- [SVG 源文件](../../../docs/targets/sky130-opamp/white-line.svg)
- [生成脚本](../../../docs/targets/sky130-opamp/make_white_line_layout.py)
- [Netlist](../../../examples/sky130_two_stage_opamp/opamp.sp)
