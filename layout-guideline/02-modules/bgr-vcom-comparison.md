# BGR vs VCOM：同一原则，不同优先级

> 这是“Module 层”存在的理由：同一个“匹配/电源”原则，在 BGR 和 VCOM 里不是同一件事。

| 维度 | BGR | VCOM |
| --- | --- | --- |
| 首要目标 | 中心值/温漂/噪声/PSRR | 输出驱动/瞬态/稳定性/ESD |
| 最大风险 | core 匹配 + 参考回流 + 启动 | 输出级电流/EM + 大功率电源回流 + ESD |
| 匹配重点 | core pair、mirror、resistor、trim | input pair、resistor string、trim、输出管 |
| 电源重点 | 低噪声、参考地、PSUB/启动 | 大电流、宽线、多孔、与 OP 前级分离 |
| 寄生重点 | VBG/VREF 的 R/C、参考回流 | 输出/电源/补偿/反馈路径 |
| ESD 重点 | 相对低（但 PAD/参考仍要） | 输出/电源 ESD、latch-up、过流 |
| Floorplan 重心 | CORE 居中、RES 独立、START 靠近 | 输出级靠边、RES 独立、COMP 靠输出 |
| Trim 重点 | 温漂/中心值/步长/单调性 | 输出精度/步长/开关电阻 |
| 关闭证据 | 温度/启动/噪声/PSRR/MC | 负载瞬态/稳定性/IR/EM/ESD |
| 常见错误 | 只加 dummy、不管回流/启动 | 只过 DRC、不管大电流/ESD/回流 |

## 结论

- **BGR 的“匹配”更偏制造环境 + 温漂 + 参考回流**；
- **VCOM 的“匹配”更偏输出/反馈路径 + trim 比例，但首要矛盾是功率/瞬态/ESD**；
- 所以 Layout Card 不能只写“注意匹配、注意电源”，必须写清 **这个模块的 Top 3 risks**。

## 相关

- [BGR Layout Card](bgr/layout-card.md)
- [VCOM Layout Card](vcom/layout-card.md)
- [Principle: matching](../01-principles/matching-and-dummy.md)
- [Principle: power](../01-principles/power-and-ground.md)
