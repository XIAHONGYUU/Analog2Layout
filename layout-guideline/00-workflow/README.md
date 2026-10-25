# 工作流

## 角色

| 角色 | 负责 | 不负责 |
| --- | --- | --- |
| 模拟工程师 | 模块意图、器件角色、匹配组、节点属性、物理优先级、验证目标 | 不写具体版图画法 |
| AI / agent | 编译 card、检查缺口、交叉链接 principle/pattern/case | 不发明规则、不做签核 |
| 版图工程师 | 读 card、floorplan、标注偏差、写回 change log | 不替模拟改电路意图 |
| 模拟 + 版图 | 解决 open questions、确认 must-preserve、关闭证据 | — |

## 五步

### Step 1 — 模拟写 intent

产物：`module-intent.yaml` + schematic annotations。

必须包含：

- 模块一句话、信号链、端口/电源域；
- role / match / group / layout；
- 节点属性：驱动、电平、速度、噪声、匹配、电流、ESD/隔离、寄生；
- 面积目标/目标 bbox/长宽比（200×200、100×400 等）；
- 敏感区/非敏感区，以及敏感区是否复用；
- 物理意图：对称、dummy、guard ring、屏蔽、keepout、floorplan bands；
- 前仿假设、后仿目标、已知风险；
- 哪些可以改、哪些必须回来问。

模板：[`../05-templates/module-intent.yaml`](../05-templates/module-intent.yaml)

### Step 2 — AI 编译 card

产物：`layout-card.md`。

AI 做：

- 从 principle/pattern/case 找对应内容；
- 生成 7 个区块；
- 把缺失信息标成 `UNKNOWN` / `ASK`；
- 链接 floorplan、area report、delta；
- 如果已有多个目标 bbox，引用候选变体；当前 demo 只有一个默认变体。

AI 不做：

- 填具体数值；
- 把“可能”写成“必须”；
- 跳过 source/owner。

### Step 3 — 版图读 card

产物：card 上的批注 + floorplan 偏差。

版图工程师应能回答：

- 这个模块的 Top 3 风险是什么？
- 哪些器件必须一起匹配？
- 哪些电源/地/参考路径不能动？
- 哪些区域是 keepout？
- 目标长宽比是否合适？敏感区能否复用？
- 画完后用什么证据关闭？

### Step 4 — 技术对话

产物：`open-questions.md` 或 card 的 Q&A 区。

只讨论技术：

- 这个 dummy 是匹配需要还是密度需要？
- 这个电源线是 IR drop、EM 还是噪声？
- 这个屏蔽的参考是什么？回流在哪？
- 这个修改会不会改变匹配环境/寄生？

> 同一总面积的不同长宽比，会得到不同摆放；见 [`docs/10-layout-variants.md`](../../docs/10-layout-variants.md)。

### Step 5 — 更新与版本

产物：card 新版本 + case candidate + change log。

- 每次修改记录：谁、为什么、改了什么、验证方式；
- 可复用内容进入 principle/pattern；
- 项目特定内容留在 private layer；
- 版本号：`v0.1` → `v0.2`。

### Step 6 — 问题回流

产物：`07-problems/<id>.md` + guideline patch。

- 每个真实问题记录现象/机制/版图动作/guideline 缺口；
- 先查 `07-problems/` 和 `04-cases/`，避免重复条目；
- 同一机制出现 ≥2 次，必须产生一条 principle/pattern/module/card/rule 变更；
- 项目特定数值留在 private rule pack。

## 交付物

| 文件 | 谁写 | 用途 |
| --- | --- | --- |
| `intent.yaml` | 模拟 | 结构化意图 |
| `layout-card.md` | AI + 模拟确认 | 版图第一眼看的 |
| `floorplan.svg/json` | 工具/AI | 布局意图 |
| `change-log.md` | 版图/模拟 | 修改与验证记录 |
| `cases/*.md` | 双方 | 脱敏案例 |

## 完成标准

- card 能在 2 分钟内读完；
- 每个 must-preserve 都有原因；
- 每个 forbidden 都有边界；
- 每个 open question 都有 owner；
- 每个数值都能回到 rule pack/PDK/项目证据。
