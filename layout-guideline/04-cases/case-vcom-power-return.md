# Case — VCOM 大功率电源与 OP 前级

> 合成/脱敏案例，用于展示 `Case → Pattern` 的结构，不对应真实项目。

## 现象

VCOM 在负载跳变/大电流输出时出现 droop、ringing 或恢复慢；OP 前级/参考同时受扰。

## 机制（候选）

- 输出级大电流与 OP 前级共用电源/地/回流；
- 输出/电源走线只用最小线宽或单点过孔；
- 电阻串/trim 走线环境不一致，trim 后在负载下偏差；
- 补偿电容远离输出，后仿稳定性与预期不同；
- sense/反馈共享大电流路径。

## 当时动作

- 大功率输出电源/地与 OP 前级分开；
- 输出/电源/地按电流密度加宽、多打孔；
- 电阻串同 unit/同走线环境，trim 开关环境一致；
- 补偿电容靠近输出；
- 反馈/sense 从输出端单独取；
- 检查 ESD/过流/回流。

## 为什么可能有效

输出级的瞬态和精度取决于“大电流回路”和“参考/反馈回路”是否分离。共享回流会把 IR/EM/开关噪声注入前级；只做 DRC 不检查回路，容易在负载下失效。

## 证据

- 需要：负载瞬态/相位裕度/trim 精度；
- 需要：输出/电源 IR/EM；
- 需要：修改前后后仿/测试对比；
- 当前：`ASK` 具体项目数据与关闭记录。

## 反例 / 不适用

- 不是所有 VCOM 都必须分电源；要看电流/负载/系统；
- 加宽走线会增加面积/耦合，需和稳定性/布局一起权衡；
- 只加补偿电容、不改回流，可能掩盖问题。

## 关联

- Principle: [power-and-ground](../01-principles/power-and-ground.md)、[signal-flow-and-parasitics](../01-principles/signal-flow-and-parasitics.md)
- Module: [VCOM](../02-modules/vcom/layout-card.md)
- Pattern: [output stage](../03-patterns/output-stage.md)、[resistor array](../03-patterns/resistor-array.md)
