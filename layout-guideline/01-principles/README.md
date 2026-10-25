# Principles

这里放“为什么”，不放具体项目数值。

| 文件 | 主题 | 一句话 |
| --- | --- | --- |
| [`matching-and-dummy.md`](matching-and-dummy.md) | 匹配与 dummy | 匹配的目标是制造环境一致，不是“加两个 dummy” |
| [`power-and-ground.md`](power-and-ground.md) | 电源与地 | 供电是完整电流回路，不是“图上连上了” |
| [`signal-flow-and-parasitics.md`](signal-flow-and-parasitics.md) | 信号流与寄生 | 先问谁驱动、谁接收、从哪里回来 |
| [`esd-and-high-voltage.md`](esd-and-high-voltage.md) | ESD 与高压 | 器件存在不等于保护路径成立 |
| [`sensitive-region-reuse.md`](sensitive-region-reuse.md) | 敏感区/复用 | 面积 = 敏感区 + 非敏感区，不是纯器件 |

新增原则时：

- 一句话能说清；
- 有适用条件和反例；
- 不写具体线宽/间距/via 数；
- 数值放到 rule pack，不放到 principle。
