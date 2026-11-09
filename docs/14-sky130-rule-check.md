# SKY130 白线检查规则（项目内）

状态：**draft v0.1；2026-11-09 owner 接受分级/waiver 政策；当前目标
`examples/sky130_ldo_01v8`。不是 DRC/LVS/PEX signoff**。

这份文档把 SKY130 的 DRC/periphery 规则，转换成这个 workspace 能执行的
**白线检查规则**。它不是完整 DRC deck，也不替代 KLayout/Calibre。

## 1. 目的

回答三个问题：

1. 哪些 SKY130 规则是硬约束，白线几何必须满足？
2. 哪些是 recommended / guideline，可以带理由 waiver？
3. 哪些是本项目自己的 layout heuristic，不能被写成 PDK fact？

## 2. 来源与证据

| 来源 | 用途 | 说明 |
| --- | --- | --- |
| `pdk/sky130/facts.json` | 已核对的 fact seed（21 条） | 每条带 `drc_rule`、`source_line`、`source_sha256` |
| `out/refs/sky130.lydrc` | 本地参考 deck | sha256 `81cf4f998fc6fb6925ccc8618afba3dc8530058db1d0e31dc1f6ad5299e52372`，不提交完整 deck |
| [SKY130 periphery rules](https://skywater-pdk.readthedocs.io/en/main/rules/periphery.html) | 规则值、flag、recommended 说明 | 公开文档，2026-11-09 核对 |
| `rules/generic_180.json` | 项目规则/启发式 | 仅 educational；不是 SKY130 PDK |
| owner decision | ring/dummy/gap 等项目选择 | 必须标 `heuristic`，不能伪装成 PDK |

## 3. 规则分级

| 等级 | 含义 | 检查失败时 |
| --- | --- | --- |
| `HARD` | SKY130 DRC 硬规则；白线几何必须满足 | 失败，不能进入下一阶段 |
| `REQUIRED_AT_IP` | PDK flag 为 `RC`，在 IP/module 级是 required | 失败；chip 级可另议 |
| `RECOMMENDED` | PDK flag 为 `RR` / `NC`，或 owner 建议 | 可 waiver，但必须记录理由和 owner |
| `HEURISTIC` | 本项目/版图经验选择，不是 PDK fact | 可调整；必须标来源和适用范围 |
| `NOT_CHECKED` | 明确不在当前白线检查范围 | 必须显式列出，不能默认 PASS |
| `N/A` | 规则不适用于当前结构/流程 | 记录原因 |

### PDK flag 到项目等级的映射

| PDK flag | 含义 | 项目处理 |
| --- | --- | --- |
| 无 | DRC 检查规则 | `HARD` |
| `P` | 仅 periphery 适用 | 当前模块按 periphery 处理；否则 `N/A` |
| `NE` | 不检查 `esd_nwell_tap` | 非 ESD 结构按 `HARD`；ESD 结构标 `N/A` |
| `NC` | DRC 不检查，仅 guideline | `RECOMMENDED` |
| `RR` | 任意 IP 级 recommended | `RECOMMENDED` |
| `RC` | chip 级 recommended，IP 级 required | IP/module 级 `REQUIRED_AT_IP`；chip 级 `RECOMMENDED` |
| `TC` | 特定 cell 名不检查 | 当前结构按 `HARD`；例外需记录 |
| `DE` | drain-extended source 不检查 | 当前结构不适用则 `N/A` |
| `F` | 仅 frame | `N/A` |
| `AL` / `CU` | 仅 Al/Cu 后端流程 | 当前白线不涉及后端，`N/A` |
| `LVS` | 由 LVS 处理 | `NOT_CHECKED`（本流程不做 LVS） |
| `A` / `AD` | CL 算法/DRC 检查 | 当前不实现，`NOT_CHECKED` |
| `DNF` | drawn not final | 记录，不用 drawn 值推断最终值 |
| `IR` | IR drop 专用 | `NOT_CHECKED` |

## 4. 当前白线检查范围

**In scope**

- MOS：diff/tap 宽度与间距、poly 宽度/间距/延伸、licon 尺寸/间距/enclosure、
  nwell/dnwell enclosure 与间距、gate/channel 相关几何。
- Passive：poly resistor 宽度/间距；MIM cap 的 DRC 规则暂列 `NOT_CHECKED`。
- Layout intent：ring/dummy 几何、阵列间距、DNW margin、block 不重叠、
  对象包含关系、所有器件已放置。
- 结构检查：数量、bank/group 成员、DNW1/DNW2 包含关系、无 fake fill。

**Out of scope（当前明确不检查）**

- 完整 DRC signoff、LVS、PEX；
- metal/via 布线、密度、EM/IR、antenna；
- ESD 结构、seal ring、chip-level density；
- MIM cap 的完整 DRC（capm.* 多数值在公开文档中为 N/A，待确认）；
- 任何“看起来像 DRC clean”的宣称。

## 5. 规则表（seed）

> 值来自 `pdk/sky130/facts.json` 或公开 SKY130 periphery 文档。  
> 不在 `facts.json` 的规则标 `docs`，后续应补 `source_line` / deck hash。

### 5.1 diff / tap / well

| 规则 | 值 | 单位 | 等级 | 适用/备注 | 来源 |
| --- | ---: | --- | --- | --- | --- |
| `difftap.1` | 0.150 | µm | `HARD` | diff/tap 最小宽度（P） | facts |
| `difftap.2` | 0.420 | µm | `HARD` | 最小 channel width（P） | docs |
| `difftap.3` | 0.270 | µm | `HARD` | diff-diff / tap-tap / 非贴合 diff-tap 间距 | facts |
| `difftap.4` | 0.290 | µm | `HARD` | tap 由一侧 diffusion 限定 | docs |
| `difftap.5` | 0.400 | µm | `HARD` | tap 由两侧 diffusion 限定（P） | docs |
| `difftap.6` | — | — | `HARD` | diff/tap 不得越过贴合边 | docs |
| `difftap.7` | 0.130 | µm | `HARD` | 非重合 diff/tap 边间距（NE） | facts |
| `difftap.8` | 0.180 | µm | `HARD` | nwell 包 p+ diff（DE/NE/P） | facts |
| `difftap.9` | 0.340 | µm | `HARD` | n+ diff 到 nwell 间距（DE/NE/P） | facts |
| `difftap.10` | 0.180 | µm | `HARD` | nwell 包 n+ tap（NE/P） | facts |
| `difftap.11` | 0.130 | µm | `HARD` | p+ tap 到 nwell 间距 | facts |
| `nwell.1` | 0.840 | µm | `HARD` | nwell 最小宽度 | facts |
| `nwell.2a` | 1.270 | µm | `HARD` | nwell 间距 | facts |
| `nwell.5` | 0.400 | µm | `HARD` | nwell 包 dnwell（TC） | facts |
| `nwell.6` | 1.030 | µm | `HARD` | dnwell 包 nwell hole（TC） | facts |
| `nwell.7` | 4.500 | µm | `HARD` | 不同 net 的 nwell/dnwell 间距（TC） | docs |
| `dnwell.2` | 3.000 | µm | `HARD` | dnwell 最小宽度 | facts |
| `dnwell.3` | 6.300 | µm | `HARD` | dnwell 间距 | facts |

### 5.2 poly / gate

| 规则 | 值 | 单位 | 等级 | 适用/备注 | 来源 |
| --- | ---: | --- | --- | --- | --- |
| `poly.1a` | 0.150 | µm | `HARD` | poly 最小宽度 | facts |
| `poly.1b` | 0.350 | µm | `HARD` | pfet with lvtn 最小 channel length | docs |
| `poly.2` | 0.210 | µm | `HARD` | poly-poly 间距 | facts |
| `poly.3` | 0.330 | µm | `HARD` | poly resistor 最小宽度 | facts |
| `poly.4` | 0.075 | µm | `HARD` | field poly 到 diff（平行边，P） | docs |
| `poly.5` | 0.055 | µm | `HARD` | field poly 到 tap（P） | docs |
| `poly.6` | 0.300 | µm | `HARD` | diff 上 poly 到贴合 tap（P） | docs |
| `poly.7` | 0.250 | µm | `HARD` | diff 超出 poly 的最小 S/D 长度（P） | facts |
| `poly.8` | 0.130 | µm | `HARD` | poly 超出 diff 的 endcap（P） | facts |
| `poly.9` | 0.480 | µm | `HARD` | poly resistor 到 poly/diff/tap 间距 | facts |
| `poly.10` | — | — | `HARD` | poly 不得覆盖 diff 内角 | docs |
| `poly.11` | — | — | `HARD` | diff 上 poly 不得 90° 转弯 | docs |
| `poly.12` | — | — | `HARD` | poly 与 tap 不得重叠（P） | docs |

### 5.3 licon / contact

| 规则 | 值 | 单位 | 等级 | 适用/备注 | 来源 |
| --- | ---: | --- | --- | --- | --- |
| `licon.1` | 0.170 | µm | `HARD` | licon min/max L/W | facts |
| `licon.2` | 0.170 | µm | `HARD` | licon 间距（P） | docs |
| `licon.5` | 0.040 | µm | `HARD` | diff 包 licon（P） | facts |
| `licon.7` | 0.120 | µm | `HARD` | 孤立 tap 相邻边包 licon（P） | facts |
| `licon.8` | 0.050 | µm | `HARD` | poly 包 poly_licon（P） | docs |
| `licon.11` | 0.055 | µm | `HARD` | diff/tap 上 licon 到 poly（P） | facts |
| `licon.16` | — | — | `HARD` | 每个 source_diff / tap 至少一个 licon（P） | docs |

### 5.4 recommended / guideline（示例）

| 规则 | 值/说明 | 等级 | 备注 | 来源 |
| --- | --- | --- | --- | --- |
| `x.18` | redundant mcon/via | `RECOMMENDED` | RR；当前白线无 metal/via，暂 `N/A` | docs |
| `x.22` | floating interconnect 检查 | `REQUIRED_AT_IP` | RC；当前白线无 metal，后续 routing 再启用 | docs |
| `m1.pd.1` | metal1 pattern density 0.7 | `RECOMMENDED` | RR；chip/module density，当前不查 | docs |
| `m2.pd.1` | metal2 pattern density 0.7 | `RECOMMENDED` | RR；当前不查 | docs |
| `m1.-` / `m2.-` | waffle density 规则 | `RECOMMENDED` | RC，chip 级 recommended / IP 级 required；当前不查 | docs |

### 5.5 项目 heuristic（不是 PDK）

| 项目 | 当前值/选择 | 等级 | 来源 |
| --- | --- | --- | --- |
| MOS bank ring width/gap | 0.5 / 0.8 µm | `HEURISTIC` | owner/layout choice |
| XM61 body ring | 2.0 / 2.0 µm | `HEURISTIC` | owner/layout choice |
| Passive ring | 1.0 / 0.8 µm | `HEURISTIC` | owner/layout choice |
| DNW margin | 2.0 µm | `HEURISTIC` | owner/layout choice |
| Group gap | 2.0 µm | `HEURISTIC` | rule pack / owner |
| Dummy L | 0.5 µm | `HEURISTIC` | owner decision |
| Resistor segment gap | 0.5 µm | `HEURISTIC` | 高于 `poly.9` 0.48 µm 的项目选择 |

这些值必须继续标 `pdk_defined=false`，不能写进 PDK fact 表。

## 6. 检查器映射（拟议）

当前 checker 还没实现；建议放在 `a2l/layout/checks_sky130.py`，按以下函数组织：

```text
check_diff_tap_geometry(...)       # difftap.1/2/3/4/5/6/7
check_well_enclosure(...)          # difftap.8/9/10/11, nwell.1/2a/5/6/7
check_dnwell(...)                  # dnwell.2/3
check_poly_gate(...)               # poly.1a/1b/2/3/4/5/6/7/8/9/10/11/12
check_licon(...)                   # licon.1/2/5/7/8/11/16
check_ring_dummy_heuristics(...)   # heuristic 表
check_placement_invariants(...)    # overlap/containment/count/DNW gap
```

每个检查返回：

```json
{
  "rule": "difftap.3",
  "severity": "HARD",
  "status": "PASS | FAIL | WAIVED | NOT_CHECKED | N/A",
  "objects": ["..."],
  "measured_um": 0.27,
  "required_um": 0.27,
  "source": "pdk/sky130/facts.json"
}
```

## 7. 推荐规则与 waiver

- `RR` / `NC`：默认 `RECOMMENDED`，失败不阻塞，但必须记录 waiver。
- `RC`：本项目按 IP/module 处理，默认 `REQUIRED_AT_IP`；chip-level 规则
  （如 metal density）标 `N/A` 或 `NOT_CHECKED`，不能假装已满足。
- waiver 需要：rule、原因、owner、适用对象、有效期、替代措施。
- waiver 不在规则层面逐条批准；统一在阶段验收时一起看（D-030）。
- `NOT_CHECKED` 必须出现在报告里；不能因为没实现就默认 PASS。

## 8. 与验收门的关系

| 阶段 | 检查 |
| --- | --- |
| A0 准备 | 本文件、规则表、heuristic 表、checker 覆盖清单 |
| A1 输入 | annotation 覆盖、role/match/group、unknown/assumption |
| A2 结构 | bank/block 成员、层级、ID |
| A3 primitive / bank | diff/poly/licon/well/dnwell、ring/dummy、尺寸 |
| A4 整模块白线 | 所有器件、DNW、overlap/containment、预期 metrics |
| A5 freeze | hash、manifest、registry、open items、waiver |

`HARD` 失败不能进入下一阶段；`RECOMMENDED` 失败可 waiver；`NOT_CHECKED`
必须显式保留。验收流程见 `WORKFLOW.md` §6；A1 输入验收细节见
`docs/15-a1-input-acceptance.md`；阶段门由 owner 推进。

## 9. 已确认与未决

**已确认（2026-11-09）**

- 当前目标 netlist：`examples/sky130_ldo_01v8`。
- 接受本文件的规则分级与 waiver 政策；waiver 统一在阶段验收时看。
- `RC` 按 IP 级 required；`RR`/`NC` 按 recommended/guideline。
- A0–A5 暂按 `WORKFLOW.md` §6 执行；分模块时再细化。
- review packet 使用 HTML 一页包。
- 本文件允许进入公开仓库。

**仍未决**

1. `difftap.2` 最小 channel width 是否对所有 MOS bank 启用？
2. MIM cap（`capm.*`）哪些规则适用？公开文档中多数为 N/A，需确认。
3. 是否把 metal/via/density 规则全部标 `NOT_CHECKED`，等 routing 阶段再启用？
4. `NE` 规则对当前 non-ESD 结构是否全部按 `HARD`？
5. F-001 的具体现象/根因/验证证据，由项目运行中补充。
6. 本文件的 owner/reviewer、版本号和 review 周期。

## 10. 变更控制

- 本文件是 draft；任何规则值变更必须更新来源和 hash。
- `pdk/sky130/facts.json` 是机器可读 seed；本文件是人工检查说明。
- 新增 `HARD` 规则必须同时加 checker 或明确标 `NOT_CHECKED`。
- 新增 `HEURISTIC` 必须写来源、适用范围、owner。
- 不能把 heuristic 写成 PDK fact，也不能用本文件替代实际 DRC。
