# Layout-induced schematic delta：把 PEX 后的“小改动”提前

## 1. 为什么会有 PEX 后的改动

典型链路：

```text
schematic → layout → LVS → PEX → re-sim → 发现性能下降
        → 加 dummy / 加 decap / 改 finger / 加 ring
        → 重新 LVS/PEX/re-sim
```

这些改动通常不是拓扑错误，而是**布局环境变化**：

- 边界器件的邻居不同，匹配变差；
- 输入对/电流镜的寄生电容、耦合变大；
- 电源瞬态/IR drop 需要 decap；
- 大电流输出级需要更多 finger/金属；
- 开关的 charge injection 需要 dummy；
- 衬底噪声需要 guard ring。

a2l 的目标不是消除这些物理效应，而是**在 floorplan 阶段就把可预测的改动列出来**，让模拟和版图提前决定。

## 2. Delta item 模型

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
  "rule": "matching.dummy_per_group",
  "notes": "Drawn in the floorplan as proposed; confirm dummy W/L with the analog designer."
}
```

| 字段 | 作用 |
| --- | --- |
| `id` | 稳定编号，便于评审/ECO 引用 |
| `kind` | `dummy` / `dummy_logic` / `guard_ring` / `decap` / `finger_split` / `routing_intent` / `reserve` |
| `target` | 组/器件/网络 |
| `action` | 具体动作，给版图/模拟看 |
| `reason` | 为什么需要；对应哪类风险 |
| `owner` | `analog` / `layout` / `both` |
| `status` | `proposed` / `accepted` / `rejected` / `deferred` |
| `area_delta_um2` | 面积影响，用于预算 |
| `confidence` | `rule` / `heuristic` |
| `rule` | 规则来源，便于审计 |
| `notes` | 例外/待确认 |

## 3. 当前生成规则

| 触发 | delta | owner |
| --- | --- | --- |
| 关键 match 组有 dummy_count | 边界 dummy | layout |
| `input_pair` | guard ring + 对称/屏蔽 routing intent | layout / both |
| `current_mirror` | dummy mirror branch / dummy stack | analog |
| `cascode` | dummy cascode | both |
| `tail_current` | dummy tail | analog |
| `output_stage` 单 finger 过宽 | finger split | analog |
| `output_stage` 正常 | 宽金属/多 via 预留 | layout |
| `enable_switch` / `adj_switch` | dummy switch | analog |
| 没有 decap | 提议 2 pF（按补偿电容比例，有上下限） | both |
| 总是 | PEX-fix reserve（默认 8%） | both |

这些规则都在 `rules/generic_180.json` 的 `layout_delta` / `block` 里，可改。

## 4. 状态流转

```text
proposed ──accept──► accepted ──implemented──► closed
   │                    │
   │                    └──defer──► deferred
   └──reject──► rejected（记录原因）
```

v0.1 只输出 `proposed`。建议的团队流程：

1. floorplan review 前，模拟/版图各自读一遍 delta；
2. review 上逐条 accept/reject，写 owner 和截止时间；
3. accepted 的 analog 项进入 schematic ECO；accepted 的 layout 项进入 floorplan/版图 checklist；
4. PEX 后回填：哪些 delta 真的发生了，哪些是清单外的新问题；
5. 每季度把“清单外问题”反推成新规则或规则修正。

## 5. 与 ECO 的边界

v0.1 **不会**自动改原理图。原因：

- delta 可能是错的（例如 mirror 离边界很远，不需要 dummy）；
- 改原理图涉及版本、review、仿真回归；
- 自动修改容易把“提议”变成“既成事实”。

后续版本可以输出 **ECO draft**：

- 只包含 accepted 的 item；
- 每个 item 关联到具体器件/组；
- 生成 diff 草案，但不自动提交；
- 必须经过人工 review 和仿真。

## 6. 度量

建议跟踪：

| 指标 | 含义 |
| --- | --- |
| delta acceptance rate | 提议中被接受的比例，衡量规则是否靠谱 |
| delta coverage | PEX 后实际改动中，有多少在清单里 |
| late surprise count | 清单外的 PEX 改动数量 |
| reserve consumption | PEX-fix reserve 被用掉多少 |
| re-sim cycles | 每个模块的 PEX 后仿真轮次 |

如果 `delta coverage` 长期低，说明规则需要补充；如果 `acceptance rate` 低，说明规则太激进或缺少上下文。

## 7. 风险与边界

- dummy 不是越多越好：会增加寄生、面积、漏电；必须由模拟确认。
- decap 位置比数量更重要：放在噪声源旁边可能适得其反。
- guard ring 可能引入衬底噪声耦合路径，需要版图/工艺判断。
- 规则包是公司资产，不能把真实 PDK 参数提交到公开仓库。
- 任何 delta 都不能替代 PEX 后的实际仿真。
