# Case — BGR 参考回流

> 合成/脱敏案例，用于展示 `Case → Principle` 的结构，不对应真实项目。

## 现象

VREF 在数字活动/负载跳变时出现漂移或毛刺；DC 测试正常，动态/系统场景才明显。

## 机制（候选）

- VREF 滤波电容的地回到数字/噪声地，而不是参考地；
- VSSA_REF 的 PAD/主干连接不完整，参考随回流波动；
- VP/VN/VBG 的屏蔽线接到错误参考，或只在一端接地；
- CORE 附近有数字/时钟/大电流走线。

## 当时动作

- 把 VREF 滤波电容的地改为 VSSA_REF；
- 检查 VSSA_REF 从 CORE 到 PAD 的完整通路；
- 关键节点屏蔽线接 VSSA_REF，并在模块内分布接地；
- 重新检查 CORE 附近的噪声源。

## 为什么可能有效

参考电压的精度取决于“参考点”和“回流点”是否同一电位。把滤波/屏蔽接到噪声地，会把数字活动注入参考；只检查图上连通，不检查端点/回流，容易漏。

## 证据

- 需要：负载跳变/数字活动下的 VREF 波形；
- 需要：VSSA_REF 路径/电阻；
- 需要：修改前后后仿/测试对比；
- 当前：`ASK` 具体项目数据与关闭记录。

## 反例 / 不适用

- 不是所有 BGR 都必须独立参考地；要看电流、回流和系统地结构；
- 独立地如果处理不好，可能引入新的 IR/ESD 问题；
- 只加屏蔽、不接对参考，可能更糟。

## 关联

- Principle: [power-and-ground](../01-principles/power-and-ground.md)
- Module: [BGR](../02-modules/bgr/layout-card.md)
- Pattern: [resistor array](../03-patterns/resistor-array.md)
