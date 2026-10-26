# White-line layout plan — SKY130 two-stage OP (v0.2)

> **v0.2 已按约束重画：DP/CM/TAIL 的 W 方向两端各一个 dummy，源漏共用；每个匹配组独立 ring；C1 改成 MOSCAP。**
> 仍不是 rule-valid layout：相对尺寸是 size class，ring 间距是 educational placeholder，MOSCAP 密度单位待确认。

![SKY130 white-line layout plan](../../../docs/targets/sky130-opamp/white-line.png)

布局细节：

![SKY130 white-line layout detail](../../../docs/targets/sky130-opamp/white-line-detail.png)

## 这是什么

这是**版图结构的白线草图**：左边是 block-level circuit reference，右边是器件/ring/dummy 的摆放和排列方式。
它和电路图放在同一个视图里，但不是“在 schematic 符号上画注释框”，也不是合法版图。

## 图上怎么读

| 区域 | 版图结构 | 说明 |
| --- | --- | --- |
| `CM` | `DM / M3_CM / M4_CM / DM`，各 4 指 | 两端各 1 个 dummy；源漏共用；同 well；独立 ring |
| `DP` | `DM / M1_DP / M2_DP / DM`，各 4 指 | common-centroid / ABBA；两端各 1 个 dummy；独立 ring |
| `TAIL/BIAS` | `DM / M5_TAIL / M8_BIAS / DM`，各 2 指 | M5/M8 镜像比例；两端各 1 个 dummy；独立 ring |
| `EN` | `M9_EN / M10_EN_PD`，各 2 指 | EN=0：M9 off，M10 把 `nbias` 拉高；独立 ring |
| `C1_CC` | MOSCAP 块 | 非高精度 OP 首选；密度按你说的 2 pF/µm² 暂记，但 **unit check pending** |
| `OUT` | `M6_OUT` 2 指 / `M7_OUT` 1 指 | 宽金属、多过孔、EM/IR；输出组独立 ring |
| `I0` | 虚线理想电流源 | 30 µA，真实 bias 生成器待补 |

## dummy 规则（已按你的定义）

- 位置：MOS 的 **W 方向外侧两端各一个**；
- 连接：**源漏共用**；
- W/L：默认与正常 MOS 相同；如果 `W/L < 0.5`，用**相同 W、最小 L**；
- gate 连接：和布局无关，先不画 gate tie；
- 当前图：CM/DP 各 2 个 DM，TAIL 2 个 DM，共 6 个。

## ring / 紧凑度

- 每个匹配组**独立围环**：CM、DP、TAIL/BIAS、EN、OUT 各自一个 ring；不共享 ring。
- 当前 ring 间距是 **educational placeholder**：`ring width 1.0 µm / ring-to-device 1.5 µm`，不是 PDK 数值。
- 组间比 v0.1 紧凑，但仍是“可读性摆放”；真正的 abutment / 共用源漏 / VDD/VSS 主干还要继续定。

## 仍待确认

- `ASK` MOSCAP 密度：你写的是 **2 pF/µm²**；1×1 µm 的 MOSCAP 若真是 2 pF，会比典型 180nm MOSCAP 高约 2–3 个数量级。请确认是 **2 pF/µm²** 还是 **2 fF/µm²**。
- `ASK` current density / 各支路 bias 电流：现在只有 `I0=30 µA` 和镜像比例，不能推出每个管子的真实电流密度。
- `ASK` MOS 相对尺寸：当前用 `small/medium/large` 档位，不是严格按 W/L/area 比例。
- `ASK` ring 的 contact/ring-to-ring/well 间距：先用 educational placeholder，等 PDK/公司规则。
- `ASK` VDD/VSS 主干、哪些组 abut、哪些 source/drain 真正共用。

## current density / size class 是什么

- **current density**：单位沟道宽度承载的电流（例如 µA/µm），用来决定 W、finger 数、金属宽度和 EM 余量。它需要 bias 电流和工作点，不能只从网表名字推出。
- **size class**：为了白线图可读，把器件按总 W/L 和电流粗分为 `small / medium / large`。它不是电气规则，只是画图时的相对尺寸档位；真实版图仍要按 W/L/area 比例。

## 相关

- [Layout Card](layout-card.md)
- [Layout constraints](constraints.yaml)
- [SVG 源文件](../../../docs/targets/sky130-opamp/white-line.svg)
- [生成脚本](../../../docs/targets/sky130-opamp/make_white_line_layout.py)
- [Netlist](../../../examples/sky130_two_stage_opamp/opamp.sp)
