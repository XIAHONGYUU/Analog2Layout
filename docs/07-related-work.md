# 相关方向与差异

> 这里只做方向性对比，不声称覆盖所有工作。引用以链接为准。

## AnalogLoop

[AnalogLoop](https://github.com/XIAHONGYUU/AnalogLoop) 是一个以仿真预算为中心、可复现的模拟电路设计 agent 架构：LLM 负责策略/诊断/停止，确定性工具链负责执行，代理模型做快速筛选，真实 SPICE 守住签核。它的 `roles.yaml` / manifest / validator、`area_low / nominal / high` 与三值 area gate、`export_layout_intent` 与 layout delta，和 a2l 的问题域直接相邻。

**a2l 的差异**：

- AnalogLoop 的重心是 **sizing 闭环和仿真预算**；a2l 的重心是 **schematic → layout 的交接物**；
- a2l 把面积进一步拆成 **core / active / matched / block / envelope**，并输出形状/排列指标；
- a2l 的布局草图是可直接评审的 SVG/JSON，强调版图工程师的第一版 floorplan；
- 两者的角色词表、面积 gate、layout delta 语义可以对齐，后续可以共享 manifest。

## GLayout

[GLayout](https://available-inventions.umich.edu/product/glayout/print) 是密歇根大学方向的 AI-assisted analog/custom circuit design 工作，强调从电路到版图的自动化生成。

**a2l 的差异**：

- a2l 不试图直接生成合法版图，而是生成**人可评审的布局草图意图**；
- a2l 把“器件角色/匹配/面积/后期改动”作为一等数据，而不是只关注几何生成；
- a2l 的目标是**沟通层**，可以接在 GLayout/OpenROAD 之前或之后。

## AnalogAgent

[AnalogAgent](https://dl.acm.org/doi/pdf/10.1145/3770855.3818993) 用 LLM agent 做模拟电路设计自动化，强调 self-improving / agent workflow。

**a2l 的差异**：

- a2l 不做电路尺寸优化或拓扑搜索；
- a2l 的“AI”主要用在语义标注、评审解释、delta 归纳；几何和面积由确定性引擎算；
- a2l 的产物是给**模拟+版图+AI** 共用的 handoff artifact。

## cascode-ai/analog-canvas

[analog-canvas](https://github.com/cascode-ai/analog-canvas) 提供 circuit design assets、SPICE fixtures 和可审计的 agent workflow。

**a2l 的差异**：

- a2l 在“可审计 agent workflow”之上，增加了 role taxonomy、面积模型、floorplan 草案 和 PEX 前 delta；
- a2l 更强调“模拟与版图之间的交接物”，而不是单纯的 circuit design agent。

## 传统 EDA flow

| 工具/阶段 | 作用 | a2l 的关系 |
| --- | --- | --- |
| Virtuoso / schematic editor | 原理图、器件属性 | a2l 消费导出的网表/属性 |
| Spectre / HSPICE | 仿真 | a2l 不跑仿真；delta 里列出需要复测的范围 |
| Virtuoso Layout / Innovus | 版图/布局 | a2l 输出 floorplan intent，可作为输入 |
| Calibre / PVS | DRC/LVS | a2l 不做，明确不替代 |
| StarRC / QRC | 寄生提取 | a2l 不做，但接收 PEX 后的反馈（roadmap） |
| KLayout | 版图查看/脚本 | v0.3 计划做 intent vs actual 对比 |

## 为什么不是“让 LLM 直接画版图”

- 几何/DRC 需要确定性、可复现、可审计；
- 版图规则是公司资产，不能被模型“猜”；
- 工程师需要能在图上标注、否决、修改；
- 早期最有价值的是**意图对齐**，不是像素级生成。

所以 a2l 的架构是：

```text
LLM/agent  → 语义标注、解释、评审
确定性引擎 → 面积、坐标、dummy 数量、规则检查
人         → 决策、accept/reject、ECO
```
