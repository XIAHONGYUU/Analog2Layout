# Roadmap

## v0.1 — 可运行的参考实现（当前）

**目标**：验证“role → area → floorplan → delta”这条链是否成立。

- [x] SPICE-like 解析 + role/match/group/layout
- [x] 角色 taxonomy + 名字 fallback
- [x] 规则包 + 可解释面积 + 区间
- [x] 五层面积口径（core / active / matched / block / envelope）+ 形状/排列指标
- [x] role/rule ownership + `--require-explicit-roles`
- [x] 三值面积门（PASS / REJECT / UNCERTAIN）+ `--fail-on-gate`
- [x] 白线图 SVG/JSON + 对称轴 + 端口 + 通道 + reserve
- [x] layout delta + HANDOFF + HTML 评审包
- [x] 三个示例 + unittest + GitHub Actions
- [x] agent prompt / schema 草案

**验收**：

```bash
python3 -m unittest discover -s tests -v
python3 -m a2l build examples/two_stage/two_stage.sp --out examples/two_stage/out
```

## v0.2 — 让输入更可信

**目标**：减少“标注靠人、规则靠猜”的问题。

- [ ] 拓扑辅助 role 建议：diode-connected、mirror、cascode、diff pair、switch、output
- [ ] annotation JSON Schema 校验 + `a2l annotate --check`
- [ ] 规则包 schema 校验 + 版本迁移
- [ ] 历史版图校准命令：`a2l calibrate rules.json actual.csv`
- [ ] 面积基线回归（对比上一版 committed block area）
- [ ] 更细的匹配模式：common-centroid / interdigitated / stacked / dummy count
- [ ] 多 subckt / 层次化面积汇总

**验收**：

- 对 3 个以上真实（脱敏）模块，面积误差在 ±30% 内；
- 校准后误差在 ±20% 内；
- `a2l validate` 能拦住 90% 的 annotation 错误。

## v0.3 — 接工具

**目标**：从“独立原型”变成“工作流的一部分”。

- [ ] KLayout/GDS 导入，比较 floorplan intent vs actual
- [ ] Cadence SKILL 导出/导入（device property、floorplan JSON）
- [ ] OpenROAD / GLayout 适配层
- [ ] 从 Spectre/Calibre 报告回流 PEX 结果
- [ ] delta 状态文件 + ECO draft
- [ ] 浏览器交互式白线图（拖动组、改 dummy、导出 JSON）

**验收**：

- 在一个真实模块上完成“schematic → a2l → Virtuoso/KLayout → PEX → delta 回填”的闭环；
- 版图工程师不再需要口头解释即可开始第一版 floorplan。

## v1.0 — 团队级工作区

**目标**：可审计、可复用、可治理。

- [ ] 公司规则包插件 + 权限/审计
- [ ] 多模块层级面积汇总
- [ ] 设计意图版本化 + diff
- [ ] 与 schematic ECO 闭环（人工确认）
- [ ] 指标 dashboard：delta coverage、acceptance、late surprises
- [ ] 公开 benchmark（不含 PDK 机密）

## 技术债 / 待决问题

1. **面积口径**：dummy/guard ring/periphery 是否计入“模块面积”？需要团队统一。
2. **width convention**：`w` 是 per-finger 还是 total？必须在规则包里显式声明并校验。
3. **role taxonomy 的粒度**：`output_stage` 是否要拆成 `output_nmos`/`output_pmos`？`bias` 是否要拆成 `bias_diode`/`bias_branch`？
4. **floorplan 评价**：如何量化“这张白线图好不好”？面积利用率、线长、对称性、拥塞、可布线性。
5. **AI 边界**：哪些 role 可以由 AI 自动确认，哪些必须人工？建议按风险分级。
6. **公司规则保密**：公开仓库只放 schema 和 generic 规则，真实规则包走私有 submodule/内部 registry。

## 非目标（至少 v1.0 前）

- 自动生成合法版图；
- 替代 PEX/DRC/LVS；
- 自动做电路拓扑/尺寸优化；
- 自动修改原理图并提交；
- 支持完整 SPICE 语义。
