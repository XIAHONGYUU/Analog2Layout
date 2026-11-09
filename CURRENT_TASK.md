# CURRENT_TASK

## 当前目标与授权

保持 Analog2Layout 为模拟/版图技术交互与早期图形规划工作区。
当前方向：把 bank 图形与规则结构化，让算法求坐标，再由程序检查、AI 解释和人工验收。
不扩展为 GDS 生成、DRC/LVS/PEX signoff 或自动修改原理图的工具。

2026-11-08 授权：整理讨论和实验、更新顶层文档、提交并推送 GitHub。
2026-11-09 授权：完成 11-08 批次收尾并提交；评估 OR-Tools 与项目的结合方式。
2026-11-09 方向确认：目标 LDO 为 `examples/sky130_ldo_01v8`；接受 SKY130 规则分级/waiver；
A0–A5 暂定；review packet 用 HTML；检查文档可进入公开仓库。
未授权接入 CLI/运行依赖、恢复正式 DNW1 装配或修改 bank/rule 数值。

## 当前入口

- [AI + 约束求解讨论与实验总结](docs/13-constraint-packing.md)
- [SKY130 白线检查规则（draft v0.1）](docs/14-sky130-rule-check.md)
- [F-001 AA/poly 非预期重叠](layout-guideline/07-problems/F-001-aa-poly-overlap.md)
- [A0–A5 验收流程](WORKFLOW.md)
- [Decision card](layout-guideline/05-templates/decision-card.md) ·
  [Kernel card](layout-guideline/05-templates/kernel-card.md) ·
  [Review packet](layout-guideline/05-templates/review-packet.md)
- [实测结果与证据](docs/experiments/2026-11-08-packing/RESULTS.md)
- [架构](ARCHITECTURE.md)、[阶段门](WORKFLOW.md)
- [LDO 产物状态](examples/sky130_ldo_01v8/ARTIFACTS.md)
- [完整前序任务入口](docs/history/current-task-2026-11-08-before-packing.md)

## 最新验收状态

- 2026-11-08 文档/实验批次已提交为 30ca477；2026-11-09 收尾提交补齐打包、决策与文档状态。
- 2026-11-09 建立 A0 准备包：SKY130 检查文档 v0.1、F-001、decision/kernel/review 模板；
  owner 接受规则分级/waiver，A0–A5 暂定；不替代 DRC。
- 仅完成独立合成实验：8 矩形、关系约束、阶梯形三个案例。
- OR-Tools 9.15.6755 单线程；每个案例分别运行 1 秒和 5 秒预算。
- 面积从 392/418/160 改善为 360/360/100；模型范围内最优。
- 所有有效结果通过独立检查；重叠篡改与过小外框负例通过。
- 未测真实 LDO、共享 ring、旋转、可变行列或布线；不宣称实际项目收益。
- OR-Tools 尚未接入 a2l CLI，也未加入项目依赖；实验环境独立。
- 本轮发布检查：85 个 unittest 通过，AGENTS.md 的七条 CLI 验证/构建/比较命令全部通过；
  文档本地链接及实验归档哈希检查通过。

## 仍生效的项目事实与边界

- LDO 是主目标；SKY130 OP 和 16-MOS class-A 是参考案例。
- NetlistLabel overlay 仍是 PROPOSAL，局部抽样不等于全部批准。
- 12 个 MOS bank 的映射及既有 dummy/ring 选择已记录 owner 确认；
  这不等于全部几何产物已冻结。见 DECISIONS.md D-024 和 LDO matching-review.md。
- DNW1 poly 方向竖直，禁止单个 bank 旋转；sd_mode=shared 有既有确认，
  不自动推广到所有未来阵列。端口及 S/D 连接细节仍待完成。
- XR_GROUP 已结构冻结：40×17、阶梯轮廓、10 个长边 dummy、周边 AA；
  见 [冻结记录](examples/sky130_ldo_01v8/passive-banks/XR_GROUP_FROZEN.md)。
- MOS 库、XC1/XC3 仍为草稿；XC1 单元拆分待确认。
- DNW1 studies 是 exploratory；正式装配继续暂停。
- 先批准 golden primitive，再批准单个 bank，之后批量生成。
- contracts.py 已存在，但旧 LDO 脚本尚未迁移；不可宣称已全面遵守契约。
- 不发明 PDK 值；heuristic 与工艺事实分开；不改变原始证据或批准状态。
- 保留既有用户文件。本轮开始已有四张 white-line-v20261104-*.png 未跟踪，
  不纳入本次讨论/实验提交。

## 下一步

1. Owner review A0 包：`docs/14-sky130-rule-check.md`、F-001、decision/kernel/review 模板、
   `WORKFLOW.md` §6。
2. A1 输入验收：`examples/sky130_ldo_01v8` 的 annotation 覆盖、role/match/group、
   unknowns/assumptions。
3. 做 A1 的一页 HTML review packet；阶段内可由 subagent 准备，阶段门由 owner 推进。
4. OR-Tools/placement 仍后置；先完成 A1/A2 与 canonical geometry。

## 待解决

- `docs/14` §9 的剩余规则问题：difftap.2、MIM cap、metal/density、NE、owner/reviewer。
- F-001 的具体现象/根因/验证证据，由项目运行中补充。
- A0 包待 owner 最终 review；A1 输入验收尚未开始。
- OR-Tools 接入的 canonical geometry、gap 表、目标函数与 optional 依赖策略待评估。
- 当前排布输入采用哪一份 canonical geometry？XR_GROUP 应作为整体消费。
- 阶梯凹口可否容纳其他对象、各类间距及可接触边界，需要明确规则。
- local-empty 的 any-dimension/area 解释尚未闭合。
- 端口、共享边界、可变阵列只在允许的自由度内建模。
- 候选图输出策略、下一面积 benchmark、shared 模式是否推广等旧问题保留在归档；
  不属于当前实验的完成条件。

## 复现

实验命令见 [实验 README](docs/experiments/2026-11-08-packing/README.md)。
完整项目验证命令仍以 AGENTS.md 为准；历史面积和测试计数见归档，不作为本轮新测值。
