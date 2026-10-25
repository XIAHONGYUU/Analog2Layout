# Layout Card — two-stage OTA

**版本**：v0.1 · **owner**：analog + layout · **状态**：draft
**产物**：[floorplan.svg](../../../examples/two_stage/out/floorplan.svg) · [area report](../../../examples/two_stage/out/area_report.md)

## 1. 一句话 + 信号链

两级 Miller OTA：差分输入对 + 电流镜负载 → 第二级共源输出 + Miller 补偿。

```text
INP/INN → DP → CM load → OUT stage → VOUT
              ↑            ↑
            TAIL         COMP
```

## 2. Top 3 risks

1. **输入对失配/输入寄生**：offset、噪声、CMRR 直接受影响。
2. **电流镜环境不一致**：第一级增益/工作点偏移。
3. **输出级电流密度 + Miller cap 寄生**：稳定性、摆幅、EM/IR。

## 3. Must preserve

- M1/M2 跨对称轴，尺寸/方向/finger 一致；两侧 dummy 对称。
- M3/M4 同 unit、同方向、同环境；diode 与 mirror 相邻。
- M5 尾电流到 M1/M2 公共源的路径短、对称。
- M6/M7 的电流路径足够宽；输出节点寄生可控。
- C1 靠近输出/第二级，远离时钟/数字/大电流线。
- 输入对周围 guard ring / 衬底接触完整。

## 4. Forbidden

- 禁止输入对走线跨时钟/数字/开关线。
- 禁止 M1/M2 两侧 dummy 不对称或只加一侧。
- 禁止只改 W/L 做镜像比例，破坏 unit cell。
- 禁止用最小线宽走 M6/M7 的输出电流。
- 禁止把 C1 放在噪声源旁边。
- 禁止为了过 LVS 随手改线后不记录。

## 5. Device / match / group

| 组 | 器件 | role | match | 关键要求 |
| --- | --- | --- | --- | --- |
| IN | M1/M2 | input_pair | DP | 对称、dummy、输入走线短 |
| LOAD | M3/M4 | current_mirror | CM | 同 unit、同环境 |
| BIAS | M5 | tail_current | TAIL | 公共源路径短 |
| OUT | M6/M7 | output_stage | — | 电流密度、EM |
| COMP | C1 | compensation | — | 靠近输出、远离噪声 |

## 6. Floorplan

- 输入对在中间，跨对称轴；
- 电流镜在上，尾电流在下；
- 输出级/补偿在右；
- 右侧留 PEX-fix reserve；
- 详见 [floorplan.svg](../../../examples/two_stage/out/floorplan.svg)。

## 7. Evidence / open questions

**已有证据**：

- role/area/floorplan/delta 由 demo 生成；
- 面积范围、dummy 面积、reserve 见 area report。

**待确认**：

- `ASK` 输入对的 offset/noise 目标是多少？
- `ASK` M3/M4 的比例和 unit 尺寸？
- `ASK` 输出级电流/EM 目标？
- `ASK` C1 的值和耦合/屏蔽要求？
- `UNKNOWN` 具体 PDK 的 ring/dummy/间距规则。

**关闭证据**：

- 输入对 offset/noise 后仿；
- 第一级增益/工作点；
- 环路稳定性/相位裕度；
- 输出级 EM/IR；
- PEX 后关键指标复测。
