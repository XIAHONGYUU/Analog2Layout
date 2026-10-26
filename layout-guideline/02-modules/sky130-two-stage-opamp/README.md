# SKY130 two-stage Miller OP

第一个真实目标的模块页。

- [Layout Card](layout-card.md)
- [Netlist](../../../examples/sky130_two_stage_opamp/opamp.sp)
- [目标说明](../../../docs/11-target-sky130-opamp.md)
- [来源与许可](../../../examples/sky130_two_stage_opamp/README.md)

10 MOS + 1 个 3 pF 补偿电容，包含真实的 bias 镜像和 enable 辅助管：
`M8_BIAS`、`M9_EN`、`M10_EN_PD`。`I0` 仍是理想 30 µA bias，10 pF 负载是外部
testbench，不算 core 面积。

## 当前快照

- block 3526 µm²，envelope 3809 µm²，PASS @ 6000 µm²
- 7 组，6 个 proposed dummies，11 个 proposed deltas
- reserve shortfall 1545 µm²（见 Card 的 Top 3 risks）
