# Layout Card — BGR

**版本**：v0.1 · **owner**：analog + layout · **状态**：draft
**产物**：floorplan（待生成）· area report（待生成）· case（见文末）

## 1. 一句话 + 信号链

低温度漂移、低噪声、可 trim 的参考源；从 startup/bias 建立 core，再由 trim/output 送到 VREF。

```text
START/BIAS → CORE (VBE/ΔVBE or MOS) → VBG → TRIM → VREF
                    ↑
              MIRROR / RES
```

## 2. Top 3 risks

1. **Core 匹配环境不一致** → 中心值、温漂、offset、噪声。
2. **Startup / 电源顺序 / PSUB 注入** → VBG 不建立或建立到错误状态。
3. **参考回流/屏蔽参考不对** → VBG 随负载、Ground Bounce、数字活动漂移。

## 3. Must preserve

- CORE 的 M1/M2、Q1/Q2（如有）、M3/M4 必须同方向、同 unit、同 finger 环境。
- 电阻阵列同 unit、同方向、同走线层/宽度/过孔；两端 dummy 对称。
- CORE/MIRROR/RES 外围 guard ring / 独立围环；不要跨电源域。
- START 器件的连接/尺寸/位置必须保证上电可靠、断电不倒灌。
- VP/VN/VBG/VREF 等关键节点用 VSSA_REF（或指定参考）屏蔽；屏蔽要接对参考。
- VREF 输出/滤波电容的地必须回到参考地，不要随手接数字地。
- Trim 电阻/开关的环境一致；开关导通电阻与电阻串比例可解释。

## 4. Forbidden

- 禁止时钟/数字/大电流/开关线跨 CORE 或电阻阵列。
- 禁止把 CORE 的器件拆到不同 well/ring/电源域。
- 禁止只加单侧 dummy 或不对称 ring。
- 禁止用数字 VSS / 噪声地做 VREF 回流。
- 禁止为了过 LVS 用细线把参考地临时连过去。
- 禁止在没有仿真/后仿证据时改 trim 电阻或 startup 尺寸。

## 5. Device / match / group

| 组 | 器件 | role | match | 关键要求 |
| --- | --- | --- | --- | --- |
| CORE | M1/M2, Q1/Q2 | bias | CORE | 同环境、同方向、dummy/ring |
| MIRROR | M3/M4 | current_mirror | CM | 同 unit、同 source/well |
| RES | R1/R2/Rtrim | bias | RES | 同 unit、同走线、dummy |
| START | M5/M6 | bias/enable_switch | — | 上电可靠、断电无倒灌 |
| TRIM | M7... | adj_switch | TRIM | 开关电阻/环境一致 |
| OUT | buffer/C1 | output_stage/decap | — | 噪声、驱动、参考地 |

## 6. Floorplan

```text
┌─────────────────────────────────────┐
│  START/BIAS        CORE             │
│  ┌──────┐      ┌──────────────┐     │
│  │ M5/M6│      │ M1/M2  M3/M4 │     │
│  └──────┘      │  Q1/Q2       │     │
│                └──────────────┘     │
│  RES array          TRIM            │
│  ┌──────────┐      ┌──────┐         │
│  │ R1 R2 ...│      │ M7...│         │
│  └──────────┘      └──────┘         │
│  OUT buffer / C1       VSSA_REF     │
└─────────────────────────────────────┘
```

- CORE 放中心，远离时钟/数字/大电流；
- RES 独立成行/列，走线环境一致；
- START 靠近 CORE，但不要破坏 CORE 边界；
- TRIM 靠近 RES，控制线远离 CORE；
- VSSA_REF/参考地单独走，回到 PAD/参考源。

## 7. Evidence / open questions

**已有证据**：

- 原理图/角色/匹配组（待补）；
- 温度扫描、启动、PSRR/噪声、Monte Carlo（待补）；
- 版图截图：CORE、RES、ring、dummy、VSSA_REF（待补）。

**待确认**：

- `ASK` NPN 还是 MOS core？是否 chopper？
- `ASK` 目标温漂/噪声/PSRR/启动时间？
- `ASK` trim 范围/步长/开关导通电阻比例？
- `ASK` VREF 负载/滤波电容/参考地结构？
- `UNKNOWN` 具体 PDK 的 ring/dummy/间距规则。

**关闭证据**：

- 温度扫描（含 trim 后）；
- 上电/断电/异常电源启动；
- PSRR/噪声/offset Monte Carlo；
- VREF 负载/回流路径；
- 版图后仿（含 VSSA_REF/寄生）。
