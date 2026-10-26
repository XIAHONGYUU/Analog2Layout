# Virtuoso white line 与 floorplan sketch

> 这两个东西不是一回事。混用会让“白线图”这个说法失去工程含义。

## Virtuoso white line

在 Virtuoso 的 schematic 语境里，white line 是一种**标志辅助线**：

- 可以画在电路图同一张 schematic 上；
- 用来标记/分组/提示某个区域、器件组或设计意图；
- 它服务于“看电路图时快速识别”，不是版图 floorplan；
- 它的价值在于把设计意图留在 schematic 旁边，而不是另开一张版图规划图。

## 本工作区的 floorplan sketch

本工作区生成的 `floorplan.svg/json` 是另一类东西：

- 从 role / match / area 推导出的**版图规划草图**；
- 有器件编号、相对位置、对称轴、routing channel、PEX-fix reserve；
- 用来和版图工程师讨论“第一版怎么摆”，不是 schematic 上的辅助线；
- 它不是合法版图，也不是 DRC/LVS/PEX 签核结果。

## 为什么改称呼

之前把 `floorplan.svg` 叫作“白线图”是不准确的。现在统一叫：

- **布局草图 / floorplan sketch**：本工作区生成的版图规划图；
- **Virtuoso white line**：schematic 里的标志辅助线。

## 未来可以做什么

这两者可以互相配合，但不是同一个 artifact：

1. **schematic overlay**：把匹配组、敏感区域、keepout 以 white-line marker 的形式导出到 schematic，方便模拟工程师在同一张图上看到意图；
2. **floorplan sketch**：把同样的意图映射到版图规划图，方便版图工程师讨论摆放；
3. 两者共享 role / match / group / sensitive-region 数据，但不共享“图形语义”。

## 当前示例

SKY130 两级 OP 的 white-line schematic 标注：

- [white-line.png](targets/sky130-opamp/white-line.png)
- [white-line.svg](targets/sky130-opamp/white-line.svg)

## 相关

- [Floorplan sketch 说明](04-floorplan.md)
- [Layout Card 模板](../layout-guideline/05-templates/layout-card.md)
- [Sensitive region / reuse](../layout-guideline/01-principles/sensitive-region-reuse.md)
