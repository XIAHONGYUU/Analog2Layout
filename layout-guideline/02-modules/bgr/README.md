# BGR（Bandgap Reference）— 合成示例

> 用于展示 Layout Card 结构，不对应真实项目/PDK；NPN / MOS 两种 core 只作为讨论分支。

## 一句话

产生低温度漂移、低噪声、可 trim 的参考电压/电流，并保证上电/断电/异常电源下都能稳定启动。

## 信号链

```text
startup/bias → BGR core (VBE/ΔVBE 或 MOS) → VBG → trim/output buffer → VREF
                         ↑
                    current mirror / resistor array
```

## 这个模块最怕什么

1. **core 匹配与环境**：输入对/电流镜/电阻/三极管/dummy/ring 的环境不一致 → 中心值、温漂、offset、噪声。
2. **启动与电源顺序**：startup 失效、PSUB 注入、断电/上电顺序 → VBG 不建立或建立到错误状态。
3. **参考回流与屏蔽**：VSSA_REF/PAD 地/共享地/屏蔽参考 → VBG 随负载、Ground Bounce、数字活动漂移。

## 关键器件

| 组 | 器件 | 角色 | 为什么关键 |
| --- | --- | --- | --- |
| CORE | M1/M2 + Q1/Q2 或 resistor pair | bias / core | VBE/ΔVBE、匹配、温漂 |
| MIRROR | M3/M4 | current_mirror | 比例、环境、电源抑制 |
| RES | R1/R2/Rtrim | bias / trim | 比例、温漂、匹配、走线寄生 |
| START | M5/M6 | bias / enable_switch | 启动、断电、PSUB |
| TRIM | M7... | adj_switch | trim 步长、开关电阻、匹配 |
| OUT | buffer / C1 | output_stage / decap | 驱动、噪声、稳定性 |

> NPN vs MOS、是否用 chopper、trim 方式、输出 buffer 结构均标 `ASK`。

## 相关

- [Layout Card](layout-card.md)
- [Intent](intent.yaml)
- [BGR vs VCOM](../bgr-vcom-comparison.md)
- [Case: 参考地/回流](../../04-cases/case-bgr-reference-return.md)
- Patterns：[current mirror](../../03-patterns/current-mirror.md)、[resistor array](../../03-patterns/resistor-array.md)、[trim network](../../03-patterns/trim-network.md)
