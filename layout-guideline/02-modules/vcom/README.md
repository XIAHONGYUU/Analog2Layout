# VCOM（公共电极电压）— 合成示例

> 用于展示 Layout Card 结构，不对应真实项目/PDK。

## 一句话

产生面板公共电极电压 VCOM，能 source/sink 较大电流、可 trim、稳定，并处理输出级 ESD/过流。

## 信号链

```text
VREF → error amp → output stage → VCOM
          ↑             ↑
     resistor string   compensation
          ↑
        trim switches
```

## 这个模块最怕什么

1. **输出级大电流/瞬态/ESD**：线宽、过孔、电流密度、输出管 ESD、过流/短路。
2. **电阻串/trim 开关匹配**：比例、开关导通电阻、走线环境、trim 步长。
3. **OP 稳定性 + 电源/地分离**：大功率电源与 OP 前级电源共用、补偿电容/寄生、负载瞬态。

## 关键器件

| 组 | 器件 | 角色 | 为什么关键 |
| --- | --- | --- | --- |
| AMP | 输入对/浮动 bias | input_pair / bias | offset、噪声、稳定性 |
| OUT | 输出 PMOS/NMOS | output_stage | 电流密度、EM、ESD、摆幅 |
| RES | 电阻串 | bias | 比例、匹配、走线 |
| TRIM | 开关阵列 | adj_switch | 导通电阻、trim 步长 |
| COMP | 补偿电容 | compensation | 稳定性、耦合 |
| ESD | 输出/电源 ESD | esd | 放电路径、latch-up |

## 相关

- [Layout Card](layout-card.md)
- [Intent](intent.yaml)
- [BGR vs VCOM](../bgr-vcom-comparison.md)
- [Case: 大功率电源与 OP 前级共用](../../04-cases/case-vcom-power-return.md)
- Patterns：[resistor array](../../03-patterns/resistor-array.md)、[output stage](../../03-patterns/output-stage.md)、[trim network](../../03-patterns/trim-network.md)
