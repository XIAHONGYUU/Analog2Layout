# Analog2Layout (`a2l`)

[![ci](https://github.com/XIAHONGYUU/Analog2Layout/actions/workflows/ci.yml/badge.svg)](https://github.com/XIAHONGYUU/Analog2Layout/actions/workflows/ci.yml)
[![GitHub](https://img.shields.io/badge/GitHub-XIAHONGYUU%2FAnalog2Layout-181717?logo=github)](https://github.com/XIAHONGYUU/Analog2Layout)

> **定位：展示型参考工作区**，不是要落地的规则库或生产工具。它用可运行的 demo 展示“模拟意图 → 面积 → 白线图 → Layout Guideline”应该怎么串起来。

> 把模拟设计师脑中的“这个管子是干什么的、哪里必须匹配、面积大概多少、版图该怎么摆”变成可版本化的数据，让 AI、模拟工程师和版图工程师围着同一张白线图讨论。

模拟与版图之间最难沟通的，往往不是“能不能画”，而是**意图没有被结构化**：哪些管子是一对、哪些是电流镜、哪些是 cascode、哪些只是 dummy；哪些面积是必须预留的；哪些改动会在 PEX 之后才冒出来。这个工作区想把这些问题前移，做成一套**可运行、可追溯、可展示工作流**的参考原型；不追求生产落地，也不包含真实 PDK/公司规则。

> 当前版本是 **v0.1 参考实现**，不是签核工具。`rules/generic_180.json` 是教学用的通用规则，不包含任何真实 PDK 参数。

![two-stage white-line floorplan](examples/two_stage/out/floorplan.png)

---

## 1. 它解决什么

| 痛点 | a2l 的做法 | 产物 |
| --- | --- | --- |
| 早期只能凭经验估面积，无法按面积选架构 | 用 `role=` / `match=` / `group=` 标注器件语义，规则引擎按版图规则估算面积，并给出范围 | `area_report.md/json` |
| 模拟和版图对“怎么摆”反复口头沟通 | 从器件角色和匹配关系生成 **白线图（floorplan intent）**，带器件编号、对称轴、匹配组、预留通道 | `floorplan.svg/json` |
| PEX 之后才发现要加 dummy、补电容、改 finger，导致重新验证 | 在布局阶段就生成 **layout-induced schematic delta** 清单，标出 owner、原因、面积影响和 PEX 复测范围 | `layout_delta.json` / `HANDOFF.md` |
| Layout guideline 散落在会议、经验、项目里，版图工程师抓不住重点 | 把 guideline 变成 **Principle → Module → Pattern → Case** 四层，先给一页 Layout Card | `layout-guideline/` |

一句话：**先让 AI 读懂“管子是干什么的”，再把模拟意图编译成版图工程师一眼能用的 Layout Card。**

---

## 2. 快速开始

要求：Python 3.10+，无第三方运行时依赖。

```bash
# 在仓库根目录
python3 -m a2l build examples/two_stage/two_stage.sp --out examples/two_stage/out --area-budget-mm2 0.005 --fail-on-gate

# 打开一页式交接包
xdg-open examples/two_stage/out/index.html
```

也可以直接看：

- [白线图 SVG](examples/two_stage/out/floorplan.svg)
- [交接单 HANDOFF.md](examples/two_stage/out/HANDOFF.md)
- [面积报告](examples/two_stage/out/area_report.md)
- [后期改动清单](examples/two_stage/out/layout_delta.json)
- [AI-native Layout Guideline](layout-guideline/README.md)
- [two-stage OTA 的一页 Layout Card](layout-guideline/02-modules/two-stage-ota/layout-card.md)

常用命令：

```bash
python3 -m a2l analyze   examples/two_stage/two_stage.sp
python3 -m a2l floorplan examples/two_stage/two_stage.sp --out out/fp
python3 -m a2l build     examples/two_stage/two_stage.sp --out out/two_stage --area-budget-mm2 0.005 --fail-on-gate
python3 -m a2l compare   examples/ota5/ota5.sp examples/ota5_cascode/ota5_cascode.sp
python3 -m a2l validate  examples/two_stage/two_stage.sp
python3 -m a2l validate  examples/two_stage/two_stage.sp --require-explicit-roles
python3 -m a2l roles
```

`build` 会生成：

```text
index.html          一页式交接包（内嵌 SVG + 表格）
floorplan.svg       白线图
floorplan.json      坐标、端口、通道、分组
area_report.md      人类可读的面积报告
area_report.json    机器可读的面积明细
layout_delta.json   后期改动清单（dummy/decap/reserve/...）
HANDOFF.md          给模拟/版图评审用的交接单
```

---

## 3. 核心约定：给管子一个“角色”

推荐在原理图器件属性里写 `role`，导出网表时保留；名字只作为 fallback。

> **职责边界**：角色表（role taxonomy）和规则包（rule pack）的 owner 是**模拟工程师/模拟团队**。AI/agent 可以提出候选、检查覆盖、解释结果，但不能自行批准新增 role 或修改 rule 数值。`a2l validate --require-explicit-roles` 可以在 CI 里强制要求显式 `role=`，把 name fallback 只当作提醒。相关决定记录在 [`DECISIONS.md`](DECISIONS.md)。

```spice
M1 n1 vinp ntail vss nmos w=5u l=0.5u nf=4 m=1 \
   role=input_pair match=DP group=IN layout=common_centroid
```

| 字段 | 含义 | 例子 |
| --- | --- | --- |
| `role` | 器件在电路中的功能 | `input_pair`, `current_mirror`, `cascode`, `tail_current`, `output_stage`, `enable_switch`, `adj_switch`, `compensation`, `decap`, `dummy` |
| `match` | 必须电气匹配的器件组 | `DP`, `CM`, `CAS`, `TAIL` |
| `group` | 功能/布局分组，可与 `match` 不同 | `IN`, `LOAD`, `OUT`, `BIAS` |
| `layout` | 期望的版图模式 | `common_centroid`, `interdigitated`, `stacked`, `minimal` |
| `ratio` / `tunable` / `constraints` | 可选，和 AnalogLoop manifest 对齐 | `ratio=1`, `tunable=true`, `constraints=[same_wl]` |

完整角色表见 [`docs/02-annotation.md`](docs/02-annotation.md)，或运行 `python3 -m a2l roles`。

### 为什么不用名字硬编码？

名字很直观，例如 `M1_DP`、`M3_CM`、`M8_EN`。但名字在改图、复制、后端导出时很容易丢或变。a2l 的策略是：

1. **属性优先**：`role=` 是 source of truth；
2. **名字兜底**：没有属性时，用 `_dp`、`_cm`、`_cas` 等后缀推断；
3. **AI 补全**：agent 可以读网表拓扑和注释，给出带置信度的 role 建议，但必须经过 `validate` 和人工确认。

---

## 4. 面积模型：可解释，而不是“拍脑袋”

对每个 MOS：

```text
W_total   = w × nf × m                 （默认 w 为单 finger 宽度，可配置）
W_finger  = W_total / (nf × m)
finger_pitch = L + 2×SD_ext + contact_spacing
OD_area   = (nf × finger_pitch) × (W_finger + 2×OD_ext)
ring_area = 2×(W_layout + H_layout)×ring_width + 4×ring_width²   （关键器件）
routing   = (OD_area + ring_area) × routing_overhead
device    = OD_area + ring_area + routing
```

对电容：

```text
area = C / cap_density
```

对匹配组和模块：

```text
group = (Σ device + dummy×dummy_area) × (1 + matching_overhead)
block = (√(Σ group) + 2×periphery)² × (1 + global_routing)
range = block × [low_factor, high_factor]
reserve = block × reserve_fraction
```

### 面积口径：五层，而不是一个数

| 层级 | 定义 | 包含 | 不包含 |
| --- | --- | --- | --- |
| **Core** | 纯器件核心区 | MOS 的 OD footprint、电容极板面积 | ring、routing、dummy、periphery |
| **Active** | 核心区 + 器件环境 | core + guard ring + 器件级 routing | dummy、matching overhead、periphery |
| **Matched** | 可匹配的器件区 | active + boundary dummy + matching overhead | 模块 periphery、block routing |
| **Block** | 模块 committed area | matched + periphery + block routing | PEX-fix reserve |
| **Envelope** | 模块总占地 | block + PEX-fix reserve | 模块外的封环/测试结构 |

报告里同时给出 **dummy 面积、ring、device routing、matching overhead、periphery、reserve**，所以“加 dummy 后多少”“核心区占比多少”“是不是方正”都能拆开看。

### 形状与排列

`floorplan.json` 的 `stats` 会给出：

- `block_width_um` / `block_height_um`：模块 bbox；
- `aspect_ratio`：W/H；
- `squareness`：`min(W,H)/max(W,H)`，1.0 表示正方形；
- `orientation`：`landscape` / `portrait` / `square-ish`；
- `rows`、`groups_by_band`：怎么排的；
- `arrangement`：一句话描述行数、每行组数、对称轴；
- `core_utilization` / `whitespace_fraction`：核心区占比和空白率。

示例：两阶段 OTA 的 block 是 **107 × 51.8 µm，aspect 2.07，squareness 0.48，landscape**；`HANDOFF.md` 会直接写出这个结论，方便模拟工程师判断“这个形状是否适合目标模块”。

### 面积门：PASS / REJECT / UNCERTAIN

给定 `--area-budget-mm2 0.005` 时，a2l 用 `area_low/high` 做三值判断：

```text
area_high <= budget      → PASS
area_low  >  budget      → REJECT
otherwise                → UNCERTAIN（区间跨过 budget，需要 refine 或 layout check）
```

示例：budget 5000 µm²，range 2701–4558 µm² → **PASS，headroom 442 µm²**。CI 里加 `--fail-on-gate` 后，REJECT/UNCERTAIN 会直接让构建失败，而不是只打印一行警告。

所有系数都来自 [`rules/generic_180.json`](rules/generic_180.json)，报告里能追溯到具体 rule key；公司规则包的创建/校准约定见 [`rules/README.md`](rules/README.md)。**它的价值是比较架构、暴露面积大头、提前发现 dummy/decap 的成本，而不是替代签核提取。**

> 真实落地时，规则包必须替换为公司/工艺厂的规则，并用历史已完成版图做校准（见 roadmap 的 calibration）。

---

## 5. 白线图：给版图工程师一张能直接讨论的图

`floorplan.svg` 不是合法版图，而是**布局意图**：

- 输入对跨对称轴摆放；
- 电流镜在上、尾电流在下；
- 输出级和补偿电容在右；
- 偏置/开关在左下；
- 每个器件有编号（`M1`、`M2`、…）；
- 匹配组用虚线框住，并标出 `DP`、`CM` 等；
- dummy 用虚线框表示“提议，不是已插入”；
- 右侧斜线区域是 **PEX-fix reserve**；
- 底部标出 routing channel、对称轴和规则包版本。

版图工程师可以在这张图上直接标“这里要加 guard ring”“这个 dummy 不要”“输出要换方向”，模拟工程师也可以用它比较不同架构的面积。

---

## 6. AI-native Layout Guideline

> 这是本工作区现在最想展示的部分：不是再写一份更长的 Layout Guideline，而是把 guideline 变成一个**可编译、可下钻、可版本化**的文件夹和工作流。

### 为什么 guideline 最难

- 只有结论、没有原因：“这里加 dummy”说不出是为了匹配、密度还是 ESD；
- 只有通用原则、没有模块特性：BGR 的匹配和 VCOM 的匹配不是同一优先级；
- 只有画法、没有边界：某项目的线宽/via 数被当成通用规则。

### 四层结构

```text
Principle（为什么）
    ↓
Module（这个模块最怕什么）
    ↓
Pattern（这类电路怎么画）
    ↓
Case（以前哪里错过 / 怎么验证）
```

版图工程师先看 **一页 Layout Card**，需要时再下钻。

### 一页 Card 的 7 个区块

1. 模块一句话 + 信号链
2. Top 3 risks
3. Must preserve
4. Forbidden
5. Device / match / group 表
6. Floorplan + 关键区域
7. Evidence / open questions / owner / version

### 工作流

```text
模拟填 intent + role 标注
  → AI 编译 Layout Card（标出 ASK/UNKNOWN，不发明规则）
  → 版图读 Card，标偏差
  → 双方解决 open questions
  → 更新 card / case，版本 +1
```

### 入口

- [layout-guideline/README.md](layout-guideline/README.md)
- [docs/08-ai-layout-guideline.md](docs/08-ai-layout-guideline.md)
- [two-stage OTA Layout Card](layout-guideline/02-modules/two-stage-ota/layout-card.md)
- [Layout Card 模板](layout-guideline/05-templates/layout-card.md)

> 这个工作区只体现**技术交互**：intent、card、floorplan、delta、change log。
>
> 不做培训助手、主审、审计这类服务型功能。

---

## 7. 把 PEX 后的“小改动”提前变成清单

`layout_delta.json` 里的每一条都有：

```json
{
  "id": "D001",
  "kind": "dummy",
  "target": "DP (M1, M2)",
  "action": "Add 2 boundary dummy device(s); see the dashed DM blocks in the floorplan",
  "reason": "Preserve edge matching for input_pair",
  "owner": "layout",
  "status": "proposed",
  "area_delta_um2": 42.0,
  "confidence": "rule",
  "rule": "matching.dummy_per_group"
}
```

当所有提议的 delta 面积超过 reserve 时，`HANDOFF.md` 和 `index.html` 会直接报出 shortfall，避免“预留了 8%，结果 decap 一个人就吃掉 44%”这种假预留。

这样做的目的不是“消灭 PEX 迭代”，而是把**可预测的迭代**变成：

- 模拟工程师提前决定要不要加 dummy switch / decap；
- 版图工程师提前预留面积和通道；
- 评审时只讨论例外，不用每次从零解释；
- PEX 后如果仍要改，能明确是“清单之外的意外”，而不是“早就知道但没人说”。

当前会检查：匹配组边界 dummy、输入对 guard ring、电流镜 dummy 分支、cascode dummy、尾电流 dummy、输出 finger/EM、使能与 trim 开关的 dummy、decap 提议、PEX-fix reserve。

---

## 8. 为什么是“确定性引擎 + AI agent”，而不是纯 LLM

- **几何和规则必须可追溯**：面积、坐标、dummy 数量不能由模型“感觉”出来；
- **AI 适合做语义层**：从拓扑/注释推断 role、把 module intent 编译成 Layout Card、解释某条 delta 的原因；
- **agent 不能发明规则**：所有 rule key 必须来自规则包；不确定时标 `unknown`/`ASK`；
- **角色/规则归模拟工程师**：AI 只提议 role、检查覆盖、解释结果，不批准 taxonomy 或 rule 数值；
- **不做服务型功能**：不提供培训助手、主审、审计；只输出技术交互所需的 intent/card/floorplan/delta/change log。

仓库里的 [`agent/prompts/`](agent/prompts/) 提供了 role 标注和 Layout Card 编译的 prompt 模板；[`AGENTS.md`](AGENTS.md) 规定了在这个仓库里工作的 AI agent 的边界。

---

## 9. 仓库结构

```text
a2l/                    确定性核心
  netlist.py            SPICE-like 解析、role/match/group/layout
  roles.py              角色 taxonomy + 名字 fallback
  rules.py              规则包加载
  area.py               面积模型
  floorplan.py          分组、band、对称、坐标
  svg.py                白线图渲染
  delta.py              layout-induced schematic delta
  report.py             Markdown / JSON / HTML 交接包
  cli.py                命令行
rules/
  generic_180.json      教学用规则包（非 PDK）
  README.md             规则包字段、校准和公司 pack 约定
examples/
  two_stage/            两阶段 Miller OTA（完整演示）
  ota5/                 5T OTA（最小例子）
  ota5_cascode/         cascode 版本（面积对比）
layout-guideline/       AI-native Layout Guideline 展示层
  00-workflow/          角色、步骤、交付物、版本
  01-principles/        匹配、电源、寄生、ESD
  02-modules/           模块 card（含 two-stage-ota 示例）
  03-patterns/          diff pair、current mirror、resistor/cap array
  04-cases/             脱敏案例
  05-templates/         card / intent / change-log 模板
  06-sources/           公开/私有边界与证据等级
docs/                   问题、标注、面积、floorplan、delta、guideline、roadmap
agent/prompts/          role 标注 + Layout Card 编译 prompt
schemas/                annotation / area_report / floorplan / delta 的 JSON Schema
DECISIONS.md            角色归属、面积口径、形状指标等 durable decisions
CITATION.cff / DISCLAIMER.md  引用信息与边界声明
tests/                  unittest，无第三方依赖
```

---

## 10. 路线图

**v0.1（当前）**
- role 标注 + 名字 fallback（fallback 仅提示，CI 可强制显式 role）
- 五层面积口径：core / active / matched / block / envelope
- 形状/排列指标：bbox、aspect、squareness、rows、groups/band
- 三值面积门 PASS / REJECT / UNCERTAIN + `--fail-on-gate`
- 规则驱动面积 + 区间 + dummy/ring/routing/periphery 分解
- 白线图 SVG/JSON + 端口/通道/对称轴 + reserve
- layout delta + HANDOFF + HTML 交接包
- role/rule ownership + `--require-explicit-roles`
- AI-native Layout Guideline 文件夹 + 工作流 + 一页 Layout Card 示例
- 三个示例 + 测试 + CI

**v0.2**
- 拓扑辅助的 role 建议（diode-connected、mirror、cascode、switch、output）
- 增加 3–5 个模块 card（BGR / LDO / VCOM / SADC / AFE_CH，均为脱敏/合成）
- 增加 5–8 个 pattern card（cascode、guard ring、power grid、ESD clamp 等）
- card 完整性检查：缺 `ASK`/`UNKNOWN`/owner/证据时给出提示（不是主审）
- 从 case 回流：把“返工原因”整理成 pattern/principle 候选

**v0.3**
- KLayout / GDS 导入，对比“意图 vs 实际”
- Cadence SKILL / OpenROAD / GLayout 适配层
- 私有 guideline overlay 的目录约定（不含真实数据）

**v1.0**
- 一条完整展示链：schematic → area → floorplan → Layout Card → 版图反馈 → change log
- 3 个模块的 card 可在 2 分钟内读完
- 公开层只保留通用/合成内容，私有层可替换

---

## 11. 明确不做什么（v0.1）

- 不做 DRC/LVS，不生成合法版图；
- 不做寄生提取，不替代 PEX；
- 不做电路综合或尺寸优化；
- 不支持完整 SPICE 语法、层次展开、`.param` 表达式；
- 不内置任何真实 PDK 规则；
- 不承诺生产落地或公司规则库；
- 不做培训助手、主审、审计服务；
- 不自动修改原理图——delta 只是 proposal，必须由人确认。

如果你的目标是签核，请继续用 Virtuoso / Spectre / Calibre / StarRC 等成熟工具；a2l 只负责把“意图”和“早期决策”结构化。

---

## 12. 相关方向

- [GLayout](https://available-inventions.umich.edu/product/glayout/print) — AI-assisted analog/custom circuit design and layout.
- [AnalogAgent](https://dl.acm.org/doi/pdf/10.1145/3770855.3818993) — LLM agents for analog circuit design automation.
- [cascode-ai/analog-canvas](https://github.com/cascode-ai/analog-canvas) — circuit assets, SPICE fixtures, auditable agent workflow.

### 与 AnalogLoop 的关系

[AnalogLoop](https://github.com/XIAHONGYUU/AnalogLoop) 关注的是以**仿真预算**为中心的 sizing agent 架构：LLM 选策略、确定性工具链执行、代理模型和真实 SPICE 两层验证。a2l 是它在 **schematic → layout handoff** 方向上的互补实现：

| 维度 | AnalogLoop | a2l |
| --- | --- | --- |
| 角色语义 | `roles.yaml` / manifest / validator | `role=` / `match=` / `group=` + annotation schema |
| 面积 | `area_low / nominal / high` + 三值 area gate | 五层面积（core/active/matched/block/envelope）+ 三值 gate |
| 布局 | `export_layout_intent` | `floorplan.svg/json` + 形状/排列指标 |
| 后期改动 | layout delta | `layout_delta.json` + reserve shortfall |
| 侧重点 | sizing 闭环与仿真预算 | 面积口径、白线图、模拟/版图评审 |

a2l 的差异点是把**器件角色、面积、白线布局、PEX 前改动**放在同一条可追溯的数据链上，而不是只做其中一段。

---

## 13. 参与

仓库地址：<https://github.com/XIAHONGYUU/Analog2Layout>

- 有真实 PDK/公司规则包？请先脱敏，再以 `rules/<name>.json` 的形式贡献 schema 和校准方法，不要提交工艺厂机密。
- 想接 Cadence / KLayout / OpenROAD / GLayout？从 `a2l/floorplan.py` 的 `Floorplan.to_dict()` 和 `schemas/floorplan.schema.json` 开始。
- 发现面积公式不对？请附一个最小网表 + 期望值 + 规则来源，开 issue。

```bash
make test
make demo
```

## 14. 决策记录

关键决定（展示型定位、角色归属、五层面积、Layout Guideline、只做技术交互）记录在 [`DECISIONS.md`](DECISIONS.md)。

## License

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE). This is a research
prototype; see [DISCLAIMER.md](DISCLAIMER.md).
