# 第一个真实目标：SKY130 两级 Miller OP

## 1. 目标

用一张**真实的、开源的、经典的两级 Miller 运放**网表跑通：

- 名字优先的角色解析；
- 五层面积 + 三值面积门；
- floorplan 草图；
- layout delta / HANDOFF；
- 后续的 Layout Card 和 guideline。

## 2. 来源与许可

- 基线工程：
  [chennakeshavadasa/Miller-Compensated-Two-stage-OPAMP-using-SKY130PDK](https://github.com/chennakeshavadasa/Miller-Compensated-Two-stage-OPAMP-using-SKY130PDK)
- 许可：MIT，Copyright (c) 2024 Nithin P
- 原始设计：SKY130，7 管两级 Miller OP + 理想 30 µA bias。
- 本工作区版本：[`examples/sky130_two_stage_opamp/opamp.sp`](../examples/sky130_two_stage_opamp/opamp.sp)

> 这是**派生教学网表**，不是原工程本身。核心尺寸来自原工程；为演示
> bias/enable，额外加了 3 个 MOS（见下）。10 pF 负载是 testbench 元件，
> 没放进 core 网表，避免把外部负载算进芯片面积。

## 3. 器件表

| 器件 | 类型 | W/L (µm) | 作用 |
| --- | --- | ---: | --- |
| `M1_DP`, `M2_DP` | NMOS | 0.75/0.5 | 差分输入对 |
| `M3_CM`, `M4_CM` | PMOS | 0.75/0.5 | 电流镜负载 |
| `M5_TAIL` | NMOS | 0.75/0.5 | 尾电流源 |
| `M6_OUT` | PMOS | 8.5/0.5, nf=2 | 第二级输出 |
| `M7_OUT` | NMOS | 6.5/0.5 | 输出电流 sink |
| `M8_BIAS` | NMOS | 0.75/0.5 | bias 镜像二极管 |
| `M9_EN` | NMOS | 2/0.5 | bias 支路使能开关 |
| `M10_EN_PD` | PMOS | 1/0.5 | EN=0 时把 bias 节点拉高，确保关断 |
| `C1_CC` | cap | 3 pF | Miller 补偿 |

## 4. 名字推断结果

| 名字 token | role | match/group |
| --- | --- | --- |
| `DP` | `input_pair` | `DP` |
| `CM` | `current_mirror` | `CM` |
| `TAIL` | `tail_current` | `TAIL` |
| `OUT` | `output_stage` | `OUT` |
| `BIAS` | `bias` | `BIAS` |
| `EN` | `enable_switch` | `EN` |
| `CC` | `compensation` | `CC` |

`a2l validate --require-known-roles` 通过；11 个器件全部有已知 role。

## 5. 当前输出

用 `generic-180` 教育规则包跑：

```text
Devices:   11 (10 MOS, 1 cap) in 7 groups
Device:    2048 µm² (device core)
Block:     3526 µm²
Envelope:  3809 µm²
Range:     2821 – 4761 µm²
Gate:      PASS @ 6000 µm², headroom 1239 µm²
Dummies:   6 proposed
Deltas:    11 proposed
```

注意：`C1_CC` 的 3 pF 在 generic 规则下占了 device area 的 95.8%，所以面积大头是
补偿电容，不是 MOS。这是教育规则包的结果，不是 SKY130 的真实电容密度。

## 6. 这次暴露的模型问题

1. **真实 SKY130 器件很小**（0.75 µm 级），floorplan 里长名字放不下；现在用
   短 ID + 组标签，后续应加“编号 + 图例”模式。
2. **ideal I0 仍是理想源**；下一步应换成真实的 bias 生成支路（beta multiplier
   或 resistor-based），否则 bias 面积/噪声/启动都没有被评估。
3. **10 pF 负载**是 testbench，不是 core；面积报告不应包含它。
4. **generic-180 规则**只能做流程演示，不能把 3526 µm² 当成 SKY130 签核面积。
5. **敏感区/复用**还没在这个真实目标上展开；下一步把 input pair、mirror、
   bias、enable 的 ring/WPE/dummy/routing reserve 单独列出来。

## 7. 下一步

- 为这个目标生成一页 Layout Card；
- 把 `sensitive_core` / `flexible_area` 用到这个 netlist；
- 生成 square / wide / tall 三个 bbox 变体；
- 用这个目标补一条真实问题记录到 `07-problems/`。

## 8. 相关

- [Layout Card](../layout-guideline/02-modules/sky130-two-stage-opamp/layout-card.md)
- [网表](../examples/sky130_two_stage_opamp/opamp.sp)
- [示例说明](../examples/sky130_two_stage_opamp/README.md)
- [MIT LICENSE](../examples/sky130_two_stage_opamp/LICENSE)
- [原始工程](https://github.com/chennakeshavadasa/Miller-Compensated-Two-stage-OPAMP-using-SKY130PDK)
