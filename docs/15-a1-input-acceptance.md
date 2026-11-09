# A1 — 输入验收固定流程

状态：**draft v0.1；2026-11-09 讨论归档；目标 `examples/sky130_ldo_01v8`**。

A1 是 A0 准备阶段之后、任何白线几何生成之前的硬门。它回答：

> 这份标注网表和配套输入，是否足够完整、可追溯、可批准，可以进入结构/几何阶段？

A1 **不生成白线图**。`make_white_line.py`、`make_bank_library.py` 等几何生成器
在 A1 通过前不得运行。

## 1. 定位

旧流程是：

```text
overlay
→ make_white_line_input.py
→ white-line-input.json
→ make_white_line.py
```

A1 在中间插入：

```text
source lock
→ parse + coverage
→ decision / unknown ledger
→ contract build
→ independent checks
→ HTML review packet
→ owner acceptance
→ 才允许 A2/A3 几何
```

## 2. 入口条件

- A0 已接受：`docs/14-sky130-rule-check.md`、D-029/D-030、decision/kernel/review 模板。
- 目标明确：`examples/sky130_ldo_01v8`。
- 输入齐全：raw netlist、overlay、`white-line-input.json`、bank map、rule pack。
- 没有生成任何 A1 阶段的白线几何。
- owner 可参加 A1 阶段门。

缺任何一项：A1 状态 `BLOCKED`。

## 3. 固定步骤

| 步骤 | 目的 | 产物 | 门 |
| --- | --- | --- | --- |
| **A1.1 Source lock** | 锁定来源与版本 | `input-lock.json` | 所有源文件/hash/版本已记录 |
| **A1.2 解析与结构校验** | 网表可解析、参数合法 | parse report | 0 error |
| **A1.3 语义覆盖** | role/match/group/bank/passive/blackbox 完整 | coverage matrix | 100% 覆盖，或 owner 批准的 unknown |
| **A1.4 决策/假设/未知** | 非事实选择显式化 | D/A/U 记录 | 无 blocking unknown |
| **A1.5 输入契约归一化** | 生成/刷新 `white-line-input.json` | schema-valid input | schema PASS |
| **A1.6 独立验收检查** | 不依赖生成器重新核对 | `annotation-acceptance.json` | 无 FAIL |
| **A1.7 一页 HTML packet** | owner 一次看完 | `a1-review-packet.html` | owner 可评审 |
| **A1.8 Owner acceptance** | 阶段门 | `input_status=accepted_for_geometry` | owner 签字 |
| **A1.9 变更控制** | 输入变了就重跑 | 新 lock/version | 不允许静默改输入 |

### A1.1 Source lock

记录：

- raw netlist：`ldo.sp` 路径 + sha256；
- overlay：`netlistlabel-overlay/ldo.annotated.sp` 路径 + sha256 + status；
- `white-line-input.json` hash；
- bank map / owner decision IDs；
- rule pack：路径、版本、hash；
- PDK facts：`pdk/sky130/facts.json` + hash；
- owner、date、A1 status。

### A1.2 解析与结构校验

- 网表可解析，器件名唯一；
- W/L/nf/m 为正数，`fingers = nf × m`；
- 单位统一为 µm；
- device type 来自 model（`pfet`/`nfet`），不是名字；
- passives/blackboxes 可识别；
- ideal source、testbench load、supply 等非布局器件被排除或标记；
- 不支持的语法显式报错。

### A1.3 语义覆盖

- 每个器件有 role；`unknown` 必须显式且 owner 接受；
- match group 与 functional group 分开；
- 每个器件属于且只属于一个 group；
- 每个 MOS 属于且只属于一个 bank；
- 单器件 bank 必须显式标 singleton；
- edge switch、dummy sides、`sd_mode`、well、ring、DNW class 明确；
- passive 的 type/footprint/ring/DNW/status 明确；
- blackbox 的 footprint/status/ports 明确，或标 placeholder；
- bank map 与 owner decision 一致。

LDO 预期基线：

```text
41 MOS
12 bank clusters
5 passives
2 blackboxes
9 groups
```

### A1.4 决策 / 假设 / 未知

- 每个非事实选择 → `D-xxx` 决策卡；
- 每个暂时假设 → `A-xxx`；
- 每个未定项 → `U-xxx`，带 owner、blocking 标志、验证计划；
- 特别检查 `make_white_line_input.py` 中的硬编码 owner 决策（bank map、
  no-dummy、edge switch、sd_mode、电阻折叠等）是否能追溯到 D-xxx。
- 生成器里有、账本里没有的选择，A1 不能通过。

### A1.5 输入契约归一化

生成/刷新 `white-line-input.json`，但不生成几何。至少包含：

- `devices`、`groups`、`passives`、`blackboxes`；
- `rules`（source/version）；
- `constraints`、`priorities`；
- `semantic_source`（overlay、hash、status、review）；
- `unknowns`、`assumptions`。

### A1.6 独立验收检查

A1 checker 不能复用 `make_white_line_input.py` 的推导逻辑。至少检查：

- 器件数量、bank 数量、passive/blackbox 数量；
- group 覆盖唯一性；
- bank map 完整性；
- W/L/nf/m/fingers 一致性；
- model type vs well；
- passive/blackbox 状态；
- unknown/assumption 是否在账本；
- rule pack 与 heuristic 是否分开；
- source hash 匹配；
- 是否误把 testbench/ideal source 放进布局。

输出 `annotation-acceptance.json`：

```json
{
  "stage": "A1",
  "input_status": "accepted_for_geometry | rejected",
  "checks": [
    {"id": "coverage.devices", "status": "PASS | FAIL | WARN | WAIVED", "evidence": "..."}
  ],
  "unknowns": ["U-001"],
  "waivers": []
}
```

### A1.7 一页 HTML packet

内容固定：

- A1、目标、日期、owner；
- 待决：accept / conditional accept / reject；
- 推荐结论；
- source identity + hashes；
- 覆盖表（41 MOS / 12 banks / 5 passives / 2 blackboxes / 9 groups）；
- 状态表（proposal / sampled / confirmed / placeholder）；
- blocking / non-blocking 清单；
- decision cards（D-xxx）；
- unknowns/assumptions（U/A-xxx）；
- 签字区。

模板：`layout-guideline/05-templates/review-packet.md`。

### A1.8 Owner acceptance

- `input_status = accepted_for_geometry`；
- 记录 owner、日期、hash、open items；
- 写入 `ARTIFACTS.md` 或 input registry；
- 只有这个状态，A2/A3 才能开始。

拒绝则记录原因，回 A1.2–A1.5，新版本，不覆盖旧 lock。

### A1.9 变更控制

以下任一变化触发 A1 重跑：

- raw netlist；
- overlay/annotation；
- bank map / owner decision；
- rule pack / PDK facts；
- passive/blackbox footprint；
- port/connectivity 约定。

几何不能用来补输入的洞。

## 4. 阶段状态

| 状态 | 含义 | 下一步 |
| --- | --- | --- |
| `PASS` | 所有 blocking 检查通过，无 blocking unknown | owner 签字后进 A2 |
| `CONDITIONAL_PASS` | blocking 通过，但有非 blocking unknown/waiver | owner 明确接受条件后进 A2 |
| `FAIL` | 有 blocking 检查失败 | 修输入，重跑 A1 |
| `BLOCKED` | 缺源文件、缺 owner 决策、无法检查 | 补输入/补决策 |

## 5. 出口条件

- [ ] `input-lock.json` 完整，source hash 匹配；
- [ ] 网表解析 0 error；
- [ ] 器件 role 覆盖 100%，或 unknown 已 owner 明确接受；
- [ ] 每个器件属于且只属于一个 group；
- [ ] 每个 MOS 属于且只属于一个 bank；
- [ ] bank map 与 owner decision 一致；
- [ ] passive/blackbox footprint/status 明确；
- [ ] 无 blocking unknown；
- [ ] `white-line-input.json` schema PASS；
- [ ] 独立 A1 checker 无 FAIL；
- [ ] 一页 HTML packet 已生成；
- [ ] owner 已签字；
- [ ] 写入 registry，状态 `accepted_for_geometry`。

## 6. Blocking / non-blocking

### 6.1 LDO 首轮 blocking

- 网表无法解析；
- 器件名重复；
- W/L/nf/m 非法，或 `fingers != nf × m`；
- 器件没有 role，且 owner 没有明确接受 `unknown`；
- 器件不在任何 group；
- MOS 不在任何 bank，或 bank map 与 owner decision 冲突；
- passive/blackbox 完全没有 footprint 或 status；
- source hash 不匹配；
- rule pack / PDK facts 缺失。

### 6.2 LDO 首轮 non-blocking（需记录）

- overlay 仍是 `PROPOSAL`、sampled review；
- ports / S-D 连接仍 pending；
- x1/x2 是 5×5 placeholder；
- passive 值未知；
- XC1/XC3 仍是 draft；
- `output_outer` 是 soft；
- local-empty 解释未闭合。

这些不阻止 A1，但必须在 packet 里出现，并在 A3/A4/A5 继续跟踪。

## 7. 固定记录

```text
examples/sky130_ldo_01v8/input-lock.json
examples/sky130_ldo_01v8/annotation-acceptance.json
examples/sky130_ldo_01v8/annotation-acceptance.md
out/a1-review-packet.html
examples/sky130_ldo_01v8/white-line-input.json   （刷新，但不是几何）
```

## 8. 角色

| 角色 | 做什么 | 不能做什么 |
| --- | --- | --- |
| Subagent | source lock、解析、覆盖检查、报告/packet | 不能批准阶段门 |
| Independent checker | 独立核对，不复用 builder | 不能改输入 |
| Owner | 批 role/match/group/bank map、blocking unknown、A1 gate | 不能跳过 A1 直接看几何 |
| Geometry generator | A1 通过后运行 | A1 阶段不得运行 |

## 9. LDO 首轮 runbook

1. 锁定 `ldo.sp`、overlay、`white-line-input.json`、`bank-specs.json`、
   `matching-review.md`、rule pack。
2. 跑 `python3 -m a2l validate examples/sky130_ldo_01v8/ldo.annotated.sp --require-known-roles`。
3. 对比 `white-line-input.json` 的预期计数：41 MOS / 12 banks / 5 passives /
   2 blackboxes / 9 groups。
4. 对照 `matching-review.md` 和 D-024，检查 12 个 bank map。
5. 标出所有 status：proposal / sampled / confirmed / placeholder。
6. 列出 unknowns/assumptions，分 blocking / non-blocking。
7. 跑独立 A1 checker。
8. 生成 `annotation-acceptance.json` 和 A1 HTML packet。
9. Owner review；PASS/CONDITIONAL_PASS 后进入 A2。

## 10. 待实现

- `tools/check_a1_input.py`：A1 独立 checker；
- `input-lock` schema；
- A1 HTML packet generator；
- 在 `examples/sky130_ldo_01v8` 上跑第一轮 A1。

## 11. 待确认

- overlay 仍是 PROPOSAL/sampled review 时，A1 是否允许 `accepted_for_geometry`？
  建议：允许，但 `semantic_status` 与 `input_status` 分开记录。
- ports / S-D 在 A1 是否必须完成？
  建议：允许显式 deferred，但标 blocking for routing/assembly。
- A1 的 blocking 清单是否按 §6.1 执行？
- A1 packet 字段是否按 §A1.7 固定？
