# Problem Record — P-0001 BGR reference return

**模块**：BGR（合成/脱敏示例）
**状态**：reviewed
**Owner**：analog + layout
**来源**：合成案例，用于说明问题回流格式

## 1. 现象

VREF 在数字活动/负载跳变时出现漂移或毛刺；DC 测试正常。

## 2. 机制

- 已确认：无（合成案例）
- 候选：VREF 滤波电容/屏蔽线接到噪声地，VSSA_REF 端点不完整
- 未知：具体项目波形、版图路径、关闭记录

## 3. 版图动作

- 把 VREF 滤波电容的地改为 VSSA_REF；
- 检查 VSSA_REF 从 CORE 到 PAD 的完整通路；
- 关键节点屏蔽接 VSSA_REF，并在模块内分布接地。

## 4. 为什么有效/无效

参考电压取决于“参考点”和“回流点”是否同一电位。接错地会把数字活动注入参考；只检查图上连通，不检查端点/回流，容易漏。

## 5. Guideline 缺口

- 缺的是：principle
- 具体缺什么：`power-and-ground` 里“参考/回流端点”检查不够显式
- 应该怎么写：在 BGR/VCOM/SADC 的 card 里增加 “VREF/VSSA_REF endpoint” 必问项

## 6. 重复问题

- recurrence_of：none
- 同类问题次数：1（合成示例）
- 如果重复：检查是否已有 reference-return principle；若已有，升级原条目而不是新建

## 7. Patch

| 文件 | 改什么 | 版本 |
| --- | --- | --- |
| `01-principles/power-and-ground.md` | 增加“参考/回流端点”检查项 | v0.1 |
| `02-modules/bgr/layout-card.md` | 增加 VSSA_REF endpoint 必问项 | v0.1 |
| `04-cases/case-bgr-reference-return.md` | 保留脱敏案例 | v0.1 |

## 8. 验证

- 合成案例：不声称真实项目关闭；
- 需要真实项目时补：波形、版图截图、后仿/测试对比、适用边界。
