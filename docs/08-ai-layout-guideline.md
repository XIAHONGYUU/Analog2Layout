# AI-native Layout Guideline

> 这是一个**展示型参考工作区**，不打算做成生产规则库或落地工具。  
> 目标是把“模拟与版图之间最难传下去的东西”做成一个可展示、可讨论、可复用的工作流和文件夹结构。

## 1. 为什么 Layout Guideline 最难

Layout guideline 通常不是“没有内容”，而是内容以三种形式散落：

1. **只有结论，没有原因**：例如“这里要加 dummy”“电源线要加粗”，但没说清是为了匹配环境、电流回路、ESD 还是寄生。
2. **只有通用原则，没有模块特性**：BGR、LDO、VCOM、SADC、AFE_CH 的“匹配”和“电源”看起来一样，实际优先级完全不同。
3. **只有画法，没有边界**：某个项目的一条线宽、一个 via 数、一种 cell 拼法被当成通用规则，换工艺/换模块就失效。

AI 的价值不是再生成一份更长的 guideline，而是把这三层**拆开、对齐、可追溯**：

```text
Principle（为什么）
    ↓
Module（这个模块最怕什么）
    ↓
Pattern（这类电路怎么画）
    ↓
Case（以前哪里错过 / 怎么验证）
```

版图工程师先看 **一页 Layout Card**，需要时再下钻到 Principle / Pattern / Case。

## 2. 四层结构

| 层 | 回答的问题 | 例子 | 不应该放什么 |
| --- | --- | --- | --- |
| **Principle** | 为什么需要这个动作？ | 匹配 = 制造环境一致；电源 = 完整电流回路；寄生 = 端点/回流/后仿证据 | 具体项目数值 |
| **Module** | 这个模块最怕什么？ | BGR 的温漂/启动/匹配；LDO 的功率管/补偿/过流；VCOM 的瞬态/电源线 | 与模块无关的通用套话 |
| **Pattern** | 这类电路通常怎么画？ | 差分对、电流镜、cascode、电阻阵列、电容阵列、ESD clamp、电源网格 | 未经验证的具体尺寸 |
| **Case** | 以前哪里错过？怎么验证？ | 参考线阻导致 INL、屏蔽反而增加寄生、VSSA 断连 | 未经脱敏的原始记录 |

四层的关系不是目录堆叠，而是**同一张卡片的四个下钻入口**。

## 3. 一页 Layout Card

Layout Card 是版图工程师第一眼看到的东西。它必须能在 **2 分钟内**回答：

1. 这个模块是干什么的？
2. 最危险的 3 个物理风险是什么？
3. 哪些器件/网络必须保持匹配、对称、隔离？
4. 哪些动作是禁止的？
5. 哪些地方可以改，哪些必须回来问模拟？
6. 画完后用什么证据关闭？

建议固定为 7 个区块：

```text
1. 模块一句话 + 信号链
2. Top 3 risks
3. Must preserve（匹配/对称/隔离/电源/关键 net）
4. Forbidden（禁止跨线、禁止共用电源、禁止最小线宽...）
5. Device / match / group 表
6. Floorplan 缩略图 + 关键区域
7. Evidence / open questions / owner / version
```

模板见 [`layout-guideline/05-templates/layout-card.md`](../layout-guideline/05-templates/layout-card.md)，示例见 [`layout-guideline/02-modules/two-stage-ota/layout-card.md`](../layout-guideline/02-modules/two-stage-ota/layout-card.md)。

## 4. 正确的工作流

```text
模拟工程师
  ├─ 写 module-intent（模块功能、器件角色、匹配组、节点属性、物理意图）
  ├─ 标注 role/match/group/layout
  └─ 给出前仿假设 / 后仿目标
          ↓
AI 编译
  ├─ 从 Principle / Pattern / Case 找对应内容
  ├─ 生成一页 Layout Card
  ├─ 标出缺失信息（不是替人猜）
  └─ 链接到 floorplan / area report / delta
          ↓
版图工程师
  ├─ 读 Layout Card（2 分钟）
  ├─ 在 floorplan 上标注偏差/问题
  └─ 把“为什么这样画”写回 change log
          ↓
模拟 + 版图
  ├─ 解决 open questions
  ├─ 更新 module-intent / card / case
  └─ 版本 +1
```

关键原则：**AI 只编译和检查缺口，不替模拟工程师发明规则，也不替版图工程师做签核。**

## 5. 文件夹结构

```text
layout-guideline/
  README.md                     # 入口 + 一眼看懂的使用顺序
  00-workflow/                  # 工作流、角色、交付物、版本
  01-principles/                # 为什么：匹配、电源、寄生、ESD、密度
  02-modules/                   # 这个模块：特性、风险、card
    two-stage-ota/              # 一个合成示例
      README.md
      layout-card.md
      intent.yaml
  03-patterns/                  # 这类电路怎么画：diff pair、mirror、...
  04-cases/                     # 错误/验证案例（脱敏）
  05-templates/                 # card / intent / change-log 模板
  06-sources/                   # 来源、证据等级、公开/私有边界
```

每个目录都有一个 `README.md`，说明“这里放什么、不放什么、怎么新增”。

## 6. AI 应该做什么 / 不应该做什么

**应该做：**

- 把 `module-intent.yaml` + 已有 principle/pattern/case 编译成 Layout Card；
- 检查 card 是否缺少：关键 net、匹配组、电源域、ESD/高压、验证方式；
- 把模拟的“口头意图”转成结构化字段，并标 `unknown`；
- 把版图反馈转成 change log / case candidate；
- 交叉链接：这个模块对应哪些 principle、哪些 pattern、哪些历史 case。

**不应该做：**

- 发明具体线宽、via 数、间距、dummy 数量；
- 把某个项目的数值写成通用规则；
- 替版图工程师做 DRC/LVS/PEX 签核；
- 把“评审意见”变成自动判决；
- 生成没有来源/适用范围的“最佳实践”。

## 7. 公开仓库与公司私有层

这个 public repo 只放：

- 结构、模板、通用原则、合成示例；
- 不包含真实 PDK、公司规则、项目数值、人员信息、原始会议记录。

真实公司内容建议放在：

```text
private-layout-guideline/
  rules/           # 公司 rule pack / PDK 数值
  modules/         # 真实模块 card
  cases/           # 脱敏前的案例
  sources/         # 会议/评审/问题单索引
```

公开层与私有层通过 `source_id` / `rule_key` / `case_id` 关联，不复制内容。

## 8. 成功标准

- 版图工程师能在 **2 分钟**内说出这个模块的 Top 3 风险和 3 个 must-preserve；
- 模拟工程师填 `module-intent` 不超过 **10 分钟**；
- 每一条“必须这样做”的背后都有一个 Principle 或 Case，不是孤立的经验；
- 每一条具体数值都能回到 rule pack / PDK / 项目证据；
- 新模块可以从模板开始，而不是从零写一份 guideline。

## 9. 反模式

- 把 Layout Card 写成 20 页 PDF；
- 把 Principle 写成口号（“注意匹配”“注意寄生”）；
- 把 Pattern 写成万能画法，不写适用条件；
- 把 Case 写成故事，不写验证和反例；
- 让 AI 直接生成“最终 guideline”，没有人确认；
- 把公开仓库当公司知识库。

## 10. 与当前 Analog2Layout demo 的关系

当前仓库里的 `examples/two_stage/` 已经能生成：

- role/area 报告；
- 白线 floorplan；
- layout delta。

`layout-guideline/` 是在这些产物之上增加一层**人可读、可下钻的 guideline**：

```text
schematic annotations
  → area/floorplan/delta（机器可读）
  → Layout Card（人第一眼看的）
  → Principle / Pattern / Case（下钻）
```

这一步不追求“自动生成合法版图”，而是让模拟和版图在同一个技术结构上对话。
