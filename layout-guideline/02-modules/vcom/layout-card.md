# Layout Card — VCOM

**版本**：v0.1 · **owner**：analog + layout · **状态**：draft  
**产物**：floorplan（待生成）· area report（待生成）· case（见文末）

## 1. 一句话 + 信号链

产生面板公共电极电压，能 source/sink 较大电流、可 trim、稳定，并处理输出级 ESD/过流。

```text
VREF → error amp → output stage → VCOM
          ↑             ↑
     resistor string   compensation
          ↑
        trim switches
```

## 2. Top 3 risks

1. **输出级大电流/瞬态/ESD** → 线宽、过孔、电流密度、输出管 ESD、过流/短路。
2. **电阻串/trim 开关匹配** → 比例、开关导通电阻、走线环境、trim 步长。
3. **OP 稳定性 + 电源/地分离** → 大功率电源与 OP 前级共用、补偿电容/寄生、负载瞬态。

## 3. Must preserve

- 输出 PMOS/NMOS 的电源/输出走线按电流密度和 EM 设计，不能用最小线宽。
- 大功率输出电源与 OP 前级电源分开；输出回流路径短、宽、独立。
- 电阻串同 unit、同方向、同走线层/宽度/过孔；trim 开关环境一致。
- 输入对/浮动 bias 器件匹配并加 dummy；输入/参考走线短、对称。
- 补偿电容靠近输出级，远离时钟/数字/大电流开关线。
- 输出/电源 ESD 器件的放电路径完整，latch-up 检查覆盖。
- 反馈/sense 线从输出端单独取，不要共享大电流路径。

## 4. Forbidden

- 禁止大功率输出电源与 OP 前级电源共用细线。
- 禁止用最小线宽走输出/电源/地。
- 禁止时钟/数字/开关线跨电阻串或补偿电容。
- 禁止 trim 电阻/开关单侧不同环境。
- 禁止为了过 LVS 用细线临时跨接电源/地。
- 禁止只检查 DRC，不检查输出级 ESD/过流/回流。

## 5. Device / match / group

| 组 | 器件 | role | match | 关键要求 |
| --- | --- | --- | --- | --- |
| AMP | M1/M2, floating bias | input_pair/bias | AMP | 匹配、dummy、低噪声 |
| OUT | MP/ MN | output_stage | OUT | 电流密度、EM、ESD |
| RES | R1...Rn | bias | RES | 同 unit、同环境 |
| TRIM | M7... | adj_switch | TRIM | 导通电阻、环境 |
| COMP | C1 | compensation | — | 靠近输出、远离噪声 |
| ESD | 输出/电源 ESD | esd | — | 放电路径、latch-up |

## 6. Floorplan

```text
┌─────────────────────────────────────┐
│  AMP / bias        RES + TRIM       │
│  ┌──────────┐      ┌────────────┐   │
│  │ M1/M2    │      │ R1...Rn    │   │
│  │ floating │      │ M7...      │   │
│  └──────────┘      └────────────┘   │
│  COMP                OUT stage      │
│  ┌──────┐            ┌──────────┐   │
│  │ C1   │            │ MP/MN    │   │
│  └──────┘            │ ESD      │   │
│                      └──────────┘   │
│   separate power rails / returns    │
└─────────────────────────────────────┘
```

- 输出级放边缘，靠近 PAD/输出；
- 大功率电源/地单独走，宽、短、回流明确；
- 电阻串独立成行/列，trim 靠近；
- OP 远离输出大电流/开关；
- 补偿电容靠近输出，但远离噪声；
- ESD 靠近 PAD/输出，路径完整。

## 7. Evidence / open questions

**已有证据**：

- 原理图/角色/匹配组（待补）；
- 负载瞬态/稳定性/trim/IR/EM/ESD（待补）；
- 版图截图：输出级、电阻串、电源/地、ESD（待补）。

**待确认**：

- `ASK` 最大 source/sink 电流、负载电容、瞬态要求？
- `ASK` 输出级结构（ClassAB/推挽）与补偿方式？
- `ASK` trim 范围/步长/开关导通电阻比例？
- `ASK` 大功率电源与 OP 电源的具体域划分？
- `ASK` ESD 等级/放电路径/latch-up 要求？
- `UNKNOWN` 具体 PDK 的线宽/过孔/ESD 规则。

**关闭证据**：

- 负载瞬态/稳定性/相位裕度；
- trim 精度/步长；
- 输出级 IR/EM；
- ESD/latch-up；
- 输出噪声/PSRR；
- 版图后仿（含输出/电源寄生）。
