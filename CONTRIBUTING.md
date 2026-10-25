# Contributing

## 先读什么

1. [`CURRENT_TASK.md`](CURRENT_TASK.md) — 当前目标和下一步；
2. [`AGENTS.md`](AGENTS.md) — 仓库边界和验证命令；
3. [`docs/01-problem.md`](docs/01-problem.md) — 为什么做这个项目。

## 本地开发

```bash
python3 -m unittest discover -s tests -v
python3 -m a2l build examples/two_stage/two_stage.sp --out examples/two_stage/out
```

无需安装依赖。若要看 SVG 预览，可在本地安装 `cairosvg` 到 `.tools/`（不要提交）：

```bash
python3 -m pip install --target .tools cairosvg
make preview
```

## 适合贡献的方向

- **角色/规则**：你们团队的 role taxonomy 与 generic 规则的差异；
- **面积模型**：更准确的 finger/contact/well/guard-ring 公式，附最小网表和推导；
- **floorplan**：新的 band/template、约束式布局、可读性改进；
- **delta**：更多可预测的 PEX 前改动，附真实（脱敏）案例；
- **适配器**：KLayout、Cadence SKILL、OpenROAD、GLayout；
- **文档/示例**：更接近真实模块的合成网表。

## 提交前检查

- [ ] `python3 -m unittest discover -s tests -v` 通过；
- [ ] `python3 -m a2l build ...` 通过，SVG 没有明显标签重叠；
- [ ] 新增面积项有 rule key、文档和测试；
- [ ] 新增 role 已加入 `a2l/roles.py` 和 `docs/02-annotation.md`；
- [ ] 没有提交 PDK、公司规则、真实原理图/版图、密钥；
- [ ] JSON 结构变化已更新 `schemas/` 和文档。

## 规则包贡献

- 公开仓库只接受**脱敏、可公开**的规则包；
- 真实公司规则请走内部 registry / private submodule；
- 规则包必须包含 `name`、`description`、`confidence` 和 `schema_version`；
- 如果规则来自历史版图校准，请附样本数量、校准方法和误差范围。

## 文档语言

- 中文为主，代码标识符、JSON key、命令行保持英文；
- 公式用 fenced code block，避免截图；
- 引用外部工作时给链接，不复制受版权保护的内容。

## Commit / PR

- 一个 PR 聚焦一件事；
- 说明“改了什么、为什么、怎么验证”；
- 面积/规则改动请附 before/after 数字；
- 不要自动修改用户原理图；delta 只能是 proposal。
