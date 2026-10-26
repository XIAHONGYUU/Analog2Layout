# White-line layout plan — SKY130 two-stage OP (v0.3, strict scale)

> **v0.3 按真实 `w_layout/h_layout` 严格缩放，带 10 µm 比例尺。**
> DP/CM/TAIL 的 W 方向两端各一个 dummy，源漏共用；每个匹配组独立 ring；C1 改成 MOSCAP（3 pF @ 2 fF/µm² = 1500 µm²）。
> ring 宽度/间距仍是 educational placeholder，不是 PDK 数值。

![SKY130 white-line layout plan](../../../docs/targets/sky130-opamp/white-line.png)

布局细节：

![SKY130 white-line layout detail](../../../docs/targets/sky130-opamp/white-line-detail.png)

## 图上怎么读

- 小方块里的数字 `1..10` 是 MOS 编号，对应右侧 `DEVICE LEGEND`；
- `d` 是 dummy，和同组 MOS 同 W/L，源漏共用；
- 白色实线框是器件；白色双框是 ring；
- 左下角是 **10 µm 比例尺**；所有器件框按 `area_report.json` 的 `w_layout/h_layout` 绘制；
- 因为尺寸严格，0.75/0.5 的管子只有约 1.3×1.25 µm，放不下文字，所以用编号 + 图例，不用文字硬塞。

## 已落实的规则

| 项 | 当前做法 |
| --- | --- |
| dummy 位置 | DP/CM/TAIL 的 W 方向两端各 1 个 |
| dummy 连接 | 源漏共用；不同端接不同电位（电位由 schematic 决定） |
| dummy W/L | 默认同正常 MOS；`W/L<0.5` 时同 W、最小 L |
| dummy gate | 和布局无关，不画 gate tie |
| ring | CM、DP、TAIL/BIAS、EN、OUT 各自独立 ring，不共享 |
| ring 间距 | `1.0 µm width / 1.5 µm gap`，educational placeholder |
| C1 | MOSCAP，3 pF @ 2 fF/µm² → 1500 µm² core |
| 比例 | `w_layout/h_layout` 严格缩放；10 µm scale bar |

## 当前仍待确认

- `ASK` ring 的 contact / ring-to-ring / well 间距：现在只是 educational placeholder。
- `ASK` MOSCAP 的电压系数、线性度、底板寄生：面积按 2 fF/µm² 算，电学边界未确认。
- `ASK` `TAIL` 单器件是否真的需要 dummy tail；当前按“两端各 1 个 dummy”画了。
- `ASK` output 组是否也需要 DM；当前 OUT 只围 ring，没加 DM。

## current density / size class

- **bias 电流是模拟设计给的**，不是版图自己决定的；版图只接收 W/L、电流/EM 约束，不在这里重新选工作点。
- **current density** 是模拟 sizing 的指标（单位宽度电流，例如 µA/µm），用来决定 W/finger/金属宽度；没有 analog 给的 bias 电流时，版图不应自己编。
- **size class** 只是白线图的可读性档位；v0.3 已经改成严格比例，不再用 `small/medium/large` 代替真实尺寸。

## 相关

- [Layout Card](layout-card.md)
- [Layout constraints](constraints.yaml)
- [SVG 源文件](../../../docs/targets/sky130-opamp/white-line.svg)
- [生成脚本](../../../docs/targets/sky130-opamp/make_white_line_layout.py)
- [Netlist](../../../examples/sky130_two_stage_opamp/opamp.sp)
