# 面积模型：早期、可解释、带区间

## 1. 目标与边界

a2l 的面积模型回答的是：

- 这个模块大概多大？
- 哪一类器件/哪一组占大头？
- dummy、guard ring、matching overhead、decap 各占多少？
- 不同架构之间谁更省面积？
- 这个估计的不确定度是多少？

它**不**回答：

- 签核面积是多少；
- DRC 是否干净；
- 金属/well/封环/test structure 的精确面积；
- 寄生参数。

因此报告里始终出现 “nominal + range”，并且明确 `confidence: educational`。

## 2. 面积口径：五层

早期面积最容易犯的错，是把“核心器件面积”“加 dummy 后的面积”“模块总面积”混成一个数。a2l 明确拆成五层：

| 层级 | 英文 key | 定义 |
| --- | --- | --- |
| 器件核心（当前实现） | `area_core_um2` | MOS 的 OD footprint + 电容极板面积；不含 ring/routing/dummy/periphery。注意：这是 **device core**，不是下面说的 sensitive core |
| 有效区 | `area_active_um2` | core + guard ring + 器件级 routing |
| 匹配区 | `area_matched_um2` | active + boundary dummy + matching overhead |
| 模块区 | `area_block_um2` | matched + periphery + block routing |
| 总占地 | `area_envelope_um2` | block + PEX-fix reserve |

同时单列：

- `area_dummy_um2`：dummy 面积；
- `area_ring_um2`：guard ring 面积；
- `area_device_routing_um2`：器件级 routing；
- `area_matching_overhead_um2`：匹配组 overhead；
- `area_periphery_um2`：模块边界/block routing；
- `area_reserved_um2`：PEX-fix reserve。

所有 fraction 默认相对 **block area**，所以：

```text
core_fraction + ring_fraction + device_routing_fraction
+ dummy_fraction + matching_fraction + periphery_fraction
= 100%
```

reserve 是 block 之外的单独 8%，所以 `envelope / block = 108%`。

### 器件核心 vs 敏感核心

上面表中的 `core` 是 **device core**（OD/极板面积），只是为了面积分解。实际版图里说的“core”更接近：

```text
sensitive_core = device core
               + guard ring / 独立围环
               + WPE / STI / well / 扩散强制间距
               + boundary dummy / density dummy
               + 屏蔽 / 参考地
               + 关键走线预留（线宽/通道/过孔）
```

版图里通常同时存在：

- **敏感区**：输入对、参考、电流镜、trim、采样、ESD/高压、关键电源路径；需要强制画法和 keepout，**可能可以复用以前项目**；
- **非敏感区**：普通偏置、数字、非关键走线、普通 decap；可以更自由地布置。

因此面积评估还要回答：

1. 敏感区/非敏感区各占多少？
2. 敏感区里 ring/WPE/dummy/屏蔽/走线预留各占多少？
3. 敏感区能否复用？复用的工艺/电压/温度/频率/模块边界是否可比？
4. 复用带来的版本债/验证债是什么？

当前代码还没有 `sensitive_core` / `flexible_area` / `reuse_candidate` 这些 key；这是下一版面积模型要补的。原则和判断问题见 [`layout-guideline/01-principles/sensitive-region-reuse.md`](../layout-guideline/01-principles/sensitive-region-reuse.md)。

### 形状与排列

面积不是一个标量。两个模块面积相同，一个接近正方形、一个长条形，布局难度和可布线性完全不同。`floorplan.json` 的 `stats` 记录：

| 指标 | 含义 |
| --- | --- |
| `block_width_um`, `block_height_um` | 模块 bbox |
| `aspect_ratio` | W/H |
| `squareness` | `min(W,H)/max(W,H)`，1.0 = 正方形 |
| `orientation` | landscape / portrait / square-ish |
| `rows`, `groups_by_band` | 几行、每行几个组 |
| `arrangement` | 一行描述：行数、组数、对称轴 |
| `core_utilization` | core / bbox |
| `whitespace_fraction` | 1 - 器件视觉面积 / bbox |

这些指标随 `HANDOFF.md` 和 `index.html` 一起输出，方便模拟工程师在“面积差不多”的方案之间判断形状是否合适。

### 面积门：三值逻辑

给定 `--area-budget-mm2` 时，a2l 不拿 nominal 去比 budget，而是用区间：

```text
if area_high <= budget:   PASS
elif area_low > budget:   REJECT
else:                     UNCERTAIN -> refine / layout check
```

| 状态 | 含义 | 输出 |
| --- | --- | --- |
| `PASS` | 最悲观估计都不超预算 | `headroom_um2` |
| `REJECT` | 最乐观估计都超预算 | `shortfall_um2` |
| `UNCERTAIN` | 区间跨过预算 | `overlap_um2`，建议 refine |
| `UNSET` | 没给 budget | 不判断 |

示例：budget 5000 µm²，range 2701–4558 µm² → PASS，headroom 442 µm²。

这个门和 AnalogLoop 的 area gate 思路一致：**面积不是标量，先用区间做三值判断，再决定是否值得花仿真/版图时间。**

在 CI 里使用 `--fail-on-gate`，只有 `PASS` 才返回 0；`REJECT` 和 `UNCERTAIN` 都会阻止构建，避免面积回归被忽略。

## 3. 基本公式

### 3.1 MOS

```text
W_total   = w × nf × m                 (默认 w 是单 finger 宽度)
W_finger  = W_total / (nf × m)
finger_pitch = L + 2×SD_ext + contact_spacing
W_layout  = n_fingers × finger_pitch
H_layout  = W_finger + 2×OD_ext
OD_area   = W_layout × H_layout
ring_area = 2×(W_layout + H_layout)×ring_width + 4×ring_width²
routing   = (OD_area + ring_area) × routing_overhead
area      = OD_area + ring_area + routing
```

其中：

- `n_fingers = max(nf×m, ceil(W_total / max_w_per_finger))`，用于处理单 finger 过宽；
- `ring_area` 只对关键器件（输入对、电流镜、cascode、尾电流、sense）计算；
- `routing_overhead` 是金属/接触/局部互连的粗估。

如果公司的 SPICE 约定是 `w` 已经包含所有 finger，把 rule pack 里的 `width_convention` 改成 `"total"`。

### 3.2 电容

```text
area = C / cap_density
```

`cap_density` 单位是 `fF/µm²`。generic 规则用 1.5 fF/µm²，仅用于演示；真实 MOM/MIM 密度必须来自工艺厂或公司规则。

### 3.3 匹配组

```text
group = (Σ device_area + dummy_count × dummy_area) × (1 + matching_overhead)
```

- `dummy_count`：关键匹配组默认 2 个边界 dummy；
- `matching_overhead`：common-centroid 12%，普通匹配 6%（generic 规则）；
- 如果组里已有 `role=dummy` 的器件，会从提议数量中扣除。

### 3.4 模块与总占地

```text
active   = Σ device_area
matched  = Σ group_area              （含 dummy + matching overhead）
block    = (√matched + 2×periphery)² × (1 + global_routing)
reserve  = block × reserve_fraction
envelope = block + reserve
range    = block × [low_factor, high_factor]
```

`periphery` 是模块边界、well 间距、封环、电源环等的粗估。模块形状被近似为正方形；真实 floorplan 的宽高比会影响这个值，所以 `floorplan.json` 里的 bbox 也可以作为交叉检查。

## 4. 一个实际例子：M1

输入对 M1：`w=5u, l=0.5u, nf=4, m=1`，generic 规则：

```text
W_total = 5 × 4 × 1 = 20 µm
W_finger = 5 µm
finger_pitch = 0.5 + 2×0.3 + 0.22 = 1.32 µm
W_layout = 4 × 1.32 = 5.28 µm
H_layout = 5 + 2×0.25 = 5.5 µm
OD_area = 5.28 × 5.5 = 29.04 µm²
ring = 2×(5.28+5.5)×0.8 + 4×0.8² = 19.81 µm²
routing = (29.04 + 19.81) × 0.18 = 8.79 µm²
total = 57.64 µm²
```

这个数字不是“M1 的版图面积”，而是“M1 加上它应分摊的 guard ring 和局部布线后的规划面积”。这种口径更适合早期比较。

## 5. 规则包结构

```json
{
  "name": "generic-180",
  "confidence": "educational",
  "owner": "analog design engineer",
  "approval": "example only; analog owner must approve production rules",
  "width_convention": "per_finger",
  "mos": {
    "min_l_um": 0.18,
    "max_w_per_finger_um": 10.0,
    "sd_ext_um": 0.30,
    "od_ext_um": 0.25,
    "contact_spacing_um": 0.22,
    "routing_overhead": 0.18,
    "guard_ring_width_um": 0.80
  },
  "matching": {
    "dummy_per_group": 2,
    "common_centroid_overhead": 0.12,
    "matching_overhead": 0.06,
    "guard_ring_for_critical": true
  },
  "cap": {
    "density_ff_per_um2": 1.5,
    "routing_overhead": 0.10
  },
  "block": {
    "periphery_um": 4.0,
    "routing_overhead": 0.10,
    "reserve_fraction": 0.08
  },
  "estimate": {
    "low_factor": 0.80,
    "high_factor": 1.35
  }
}
```

完整的 key 见 [`rules/generic_180.json`](../rules/generic_180.json)。

## 6. 校准（roadmap）

真实落地不能直接用 generic 规则。建议的校准流程：

1. 收集 10–30 个已完成模块：网表 + 实际版图面积 + 关键 rule 参数；
2. 用 a2l 跑同一套规则，记录 `estimated / actual`；
3. 按 role/模块类型分组，拟合 `routing_overhead`、`periphery`、`common_centroid_overhead`；
4. 把校准后的系数写入公司规则包，保留版本号和样本数量；
5. 每季度用新项目回测，更新 `low_factor/high_factor`。

v0.1 还没有自动校准命令；这是 v0.2 的重点。

## 7. 已知误差来源

| 来源 | 影响 | 缓解 |
| --- | --- | --- |
| 模块形状不是正方形 | periphery 估计偏差 | 用 floorplan bbox 交叉检查 |
| 大电流输出级金属 | 面积被低估 | 单独的输出级 rule / EM 规则 |
| MOM/MIM 密度 | 电容面积偏差大 | 用公司工艺的真实密度 |
| 多层金属/well | OD 面积不是全部 | 引入 metal/well overhead |
| 共享 S/D、折叠 | 多 finger 面积被高估 | 用 `shared_diffusion` 因子校准 |
| 封环/test structure | 模块面积被低估 | 在 block rule 里单列 |
| 规则版本变化 | 历史比较失真 | 规则包版本化 + 报告里记录 |

## 8. 使用建议

- 用 nominal 做架构比较，用 range 做风险沟通；
- 不要把 `area_report.json` 的数字写进签核报告；
- 先让团队对“面积口径”达成一致（是否含 dummy/guard ring/periphery），再谈精度；
- 每次规则改动都要跑 `examples/` 回归，避免“修一个模块、坏一片比较”。
