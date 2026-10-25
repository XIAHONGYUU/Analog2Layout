# Two-stage OTA（合成示例）

> 这个模块只用于说明 Layout Card 的结构，不对应任何真实项目/PDK。

## 一句话

两级 Miller OTA：第一级差分输入 + 电流镜负载，第二级共源输出 + Miller 补偿。

## 信号链

```text
vinp/vinn → 差分对 → 电流镜负载 → 第二级 → vout
                         ↑              ↑
                       tail bias      Miller cap
```

## 这个模块最怕什么

1. **输入对失配/寄生**：offset、噪声、共模抑制会直接受输入对环境和走线影响。
2. **电流镜比例/环境不一致**：第一级增益和工作点会偏。
3. **输出级/补偿电容的寄生与电流密度**：稳定性、摆幅、EM/IR。

## 关键器件

| 组 | 器件 | 角色 | 为什么关键 |
| --- | --- | --- | --- |
| IN | M1/M2 | input_pair | 匹配、对称、输入寄生 |
| LOAD | M3/M4 | current_mirror | 比例、环境一致 |
| BIAS | M5 | tail_current | 尾电流、共源节点 |
| OUT | M6/M7 | output_stage | 电流密度、摆幅、EM |
| COMP | C1 | compensation | 稳定性、耦合、面积 |

## 相关产物

- [Layout Card](layout-card.md)
- [Intent](intent.yaml)
- [Demo floorplan](../../../examples/two_stage/out/floorplan.svg)
- [Demo HANDOFF](../../../examples/two_stage/out/HANDOFF.md)
