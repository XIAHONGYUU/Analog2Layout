# 白线图：布局意图，而不是合法版图

## 1. 白线图要回答什么

版图工程师拿到一张白线图时，应该能快速回答：

1. 这个模块有哪些功能组？
2. 输入对在哪、对称轴在哪？
3. 电流镜、尾电流、输出级、补偿电容的相对位置？
4. 哪些器件必须 matching，哪些只是功能分组？
5. 哪些 dummy/decap 是提议的，哪些已经存在？
6. 电源/地/输入/输出/控制信号从哪里进出？
7. 哪些区域是 routing channel，哪些是 PEX-fix reserve？
8. 哪些地方需要 guard ring / shielding / 特殊方向？

它不回答：

- 具体的金属走线；
- DRC 合法的间距；
- 精确的器件方向；
- 寄生参数；
- 是否 LVS clean。

## 2. 当前布局策略

v0.1 使用可解释的 band/template，而不是黑盒优化：

| band | 放置 | 角色 |
| --- | --- | --- |
| `top` | 上方 | `current_mirror`（居中）、`cascode`（右侧） |
| `mid` | 中间 | `input_pair`（跨对称轴）、`output_stage`、`compensation`、`sense` |
| `bottom` | 下方 | `tail_current`（居中）、`bias`、`enable_switch`、`adj_switch` |
| `periphery` | 外围 | `decap`、`dummy`、`esd` |

规则：

- 输入对的两个有源器件分列对称轴两侧；
- 电流镜默认在输入对上方、居中；
- 尾电流在输入对下方、居中；
- 输出级和补偿电容在右侧；
- 偏置和开关在左下；
- 关键匹配组加 boundary dummy（虚线框）；
- 每个 band 之间留 routing channel；
- 右侧留出 `reserve_fraction` 的 PEX-fix reserve。

这些是**默认意图**，不是物理约束。模拟工程师可以在 SVG/JSON 上直接改，或者用后续的 constraint editor。

## 3. 坐标与输出

`floorplan.json`：

```json
{
  "design": "two_stage",
  "units": "um",
  "canvas": {"width": 156.5, "height": 115.8},
  "symmetry_axis_x": 39.5,
  "groups": [
    {
      "key": "DP",
      "role": "input_pair",
      "band": "mid",
      "x": 28.2, "y": 42.7, "w": 22.7, "h": 5.5,
      "devices": ["M1", "M2", "DM_DP_L", "DM_DP_R"],
      "symmetry": "vertical"
    }
  ],
  "devices": [
    {"name": "M1", "x": 33.7, "y": 42.7, "w": 5.3, "h": 5.5, "proposed": false}
  ],
  "ports": [
    {"name": "VDD", "x": 39.5, "y": 27.0, "side": "top"}
  ],
  "channels": [
    {"orientation": "horizontal", "y1": 30.3, "label": "routing channel"}
  ],
  "reserve": {"x": 128.5, "y": 34.0, "w": 8.5, "h": 51.8, "fraction": 0.08}
}
```

坐标原点在画布左上角，单位 µm，y 向下。这样 SVG 和大多数版图/绘图工具的坐标习惯一致（版图工具通常 y 向上，转换时注意）。

## 4. 形状与排列指标

`floorplan.json` 的 `stats` 不只看面积，还记录“是否方正、怎么排”：

| 指标 | 含义 | 两阶段 OTA 示例 |
| --- | --- | --- |
| `block_width_um` | 模块 bbox 宽 | 107.0 µm |
| `block_height_um` | 模块 bbox 高 | 51.8 µm |
| `aspect_ratio` | W/H | 2.07 |
| `squareness` | `min(W,H)/max(W,H)` | 0.48 |
| `orientation` | landscape / portrait / square-ish | landscape |
| `rows` | band 行数 | 3 |
| `groups_by_band` | 每行几个组 | top=1, mid=3, bottom=3 |
| `arrangement` | 行数/组数/对称轴摘要 | 3 rows; sym axis x=40.1 |
| `core_utilization` | core / bbox | 25.4% |
| `whitespace_fraction` | 空白率 | 71.3% |

为什么要在意这些：

- **面积相同，形状不同**：长条形和正方形的可布线性、电源网络、ir-drop 完全不同；
- **squareness 低**：可能意味着某个大电容/输出级把模块拉长，需要 early floorplan review；
- **core_utilization 低**：大量面积被 periphery/routing/reserve 吃掉，值得问“规则是否过保守”；
- **rows/groups_by_band**：让版图工程师一眼知道“这是三行结构”，而不是从 SVG 里数。

这些指标会进入 `HANDOFF.md` 和 `index.html`，也会出现在 `compare` 的后续版本里。

## 5. SVG 图例

| 视觉 | 含义 |
| --- | --- |
| 实线矩形 | 已存在的器件 |
| 虚线矩形 | 提议的 dummy / decap，尚未插入原理图 |
| 斜线填充 | PEX-fix reserve，不分配给具体器件 |
| 红色虚线 | 对称轴 |
| 灰色虚线横线 | routing channel |
| 小方块 | 端口/引脚 |
| `M1` / `M2` | 器件编号，和网表一致 |
| `DP` / `CM` / `TAIL` | 功能/匹配组标签 |

## 6. 评审问题清单

在 floorplan review 上，建议逐条确认：

- [ ] 输入对是否跨对称轴？dummy 是否两侧对称？
- [ ] 电流镜的 diode 和 mirror 是否同环境？是否需要 dummy branch？
- [ ] cascode stack 的源漏方向是否一致？是否需要 dummy stack？
- [ ] 尾电流是否在输入对正下方？common source 路径是否短？
- [ ] 输出级是否在右侧？金属宽度/过孔是否预留？
- [ ] 补偿电容是否靠近输出？是否远离噪声/时钟？
- [ ] 开关/偏置是否在左下？控制线是否远离输入对？
- [ ] decap 位置是否靠近电源入口？
- [ ] routing channel 是否足够？是否被器件挤占？
- [ ] PEX-fix reserve 是否足够？谁负责看管？
- [ ] 所有 `unknown` role 是否已经补标？
- [ ] 提议的 delta 是否逐条 accept/reject？

## 7. 当前实现的限制

- 只支持单层 `.subckt`，不展开层次；
- 不支持器件旋转/镜像的显式建模；
- 电容按面积生成矩形，不区分 MOM/MIM/ fringe；
- 不检查 DRC/LVS；
- 不优化线长/寄生；
- floorplan 的 band 策略是固定的，不能自动探索所有拓扑；
- 没有交互式编辑器（v0.1 输出 SVG/JSON，后续可接 KLayout/浏览器编辑器）；
- shape/aspect/squareness 来自当前生成的白线图，不是最终版图；用户改布局后需要重新生成；
- `core_utilization` 使用器件视觉矩形面积，不是最终 OD/金属密度。

## 8. 后续方向

1. **约束式布局**：把 `symmetry`、`alignment`、`left_of`、`above` 变成可编辑约束，用简单 solver 生成多个候选。
2. **模板库**：为 diff pair、current mirror、cascode、output stage 建立可复用模板。
3. **GDS/KLayout 回读**：比较“意图 vs 实际”，把偏差变成 review 项。
4. **多目标评分**：面积、线长、对称性、寄生风险、拥塞。
5. **交互式白线图**：在浏览器里拖动组、改 dummy 数量、导出 JSON。
