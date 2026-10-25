# Roadmap

> 这是一个持续完善中的工作区，当前不是最终生产落地计划。路线图只描述“如何把工作流继续补完整”。

## v0.1 — 可运行 demo + guideline 骨架（当前）

**目标**：证明“role → area → floorplan → Layout Card → delta”这条链能串起来。

- [x] SPICE-like 解析 + role/match/group/layout
- [x] 五层面积口径 + 形状/排列指标
- [x] 三值面积门 + `--fail-on-gate`
- [x] 白线图 SVG/JSON + 对称轴 + 端口 + 通道 + reserve
- [x] layout delta + HANDOFF + HTML 交接包
- [x] role/rule ownership + `--require-explicit-roles`
- [x] `layout-guideline/` 文件夹 + 工作流
- [x] 一页 Layout Card 示例：two-stage OTA / BGR / VCOM
- [x] BGR vs VCOM 模块优先级对比
- [x] Principle / Pattern / Template 骨架
- [x] `agent/prompts/compile_layout_card.md`
- [x] 三个示例 + unittest + GitHub Actions

## v0.2 — 把 guideline 工作层填厚

**目标**：让“一页 card + 下钻”这套结构看起来像一个真实可用的工作区。

- [ ] 2–3 个模块 card（LDO / SADC / AFE_CH，均为合成/脱敏）
- [ ] 5–8 个 pattern card（cascode、guard ring、power grid、ESD clamp 等）
- [ ] 2–3 个 case card（failure / near-miss / tradeoff）
- [ ] card 完整性检查：缺 `ASK`/`UNKNOWN`/owner/evidence 时提示
- [ ] 一个“从 case 回流到 pattern/principle”的示例
- [ ] Layout Card 的 JSON/YAML 形式（可选）

## v0.3 — 接工具（先做接口）

**目标**：说明 guideline 如何与现有工具链衔接，不要求生产集成。

- [ ] KLayout / SVG 叠加：floorplan intent vs actual
- [ ] 从 Spectre/Calibre 报告提取关键 net 的 R/C，回填 card
- [ ] Cadence SKILL / OpenROAD / GLayout 的接口草案
- [ ] 私有 overlay 的目录约定（不含真实数据）

## v1.0 — 完整工作链

**目标**：一个工程师从 README 进入，能在 15 分钟内看懂整套方法。

- [ ] schematic → area → floorplan → Layout Card → 版图反馈 → change log
- [ ] 3 个模块 card 都能在 2 分钟内读完
- [ ] 公开层只含通用/合成内容，私有层可替换
- [ ] 每个 must-preserve 都有 principle/pattern/case 支撑

## 技术债 / 待决问题

1. **Card 的可读性**：一页是否够？哪些内容应该放第二页？
2. **四层边界**：Principle / Pattern / Module / Case 的重复如何避免？
3. **私有 overlay**：如何只靠 ID 关联，不泄露公司规则？
4. **数值归属**：哪些进 rule pack，哪些进 pattern 示例，哪些只留在 private？
5. **AI 边界**：哪些内容 AI 可以编译，哪些必须人工确认？
6. **多模块复用**：BGR/LDO/VCOM 的共性如何抽成 principle，而不变成口号？

## 非目标

- 生产规则库 / 公司部署；
- 自动生成合法版图；
- 替代 PEX/DRC/LVS；
- 自动做电路拓扑/尺寸优化；
- 自动修改原理图并提交；
- 培训助手、主审、审计服务；
- 支持完整 SPICE 语义。
