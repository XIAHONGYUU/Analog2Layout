# 同一总面积，不同摆放：floorplan variants

> 面积不是唯一的约束。同样的总面积，200×200 和 100×400 是两种不同的版图问题。

![同一总面积，三种摆放](diagrams/variants.png)

## 1. 为什么不能只给一个 floorplan

版图布局不是“把器件随机摆进去”。它受：

- 器件类型/参数：输入对、电流镜、cascode、输出管、电阻/电容阵列；
- 匹配/对称：哪些组不能拆、哪些必须共质心；
- 敏感区：ring、WPE/STI 间距、dummy、屏蔽、走线预留；
- 电源/地/ESD：主干、回流、PAD、keepout；
- 目标 bbox：总图给出 200×200、100×400、400×100，摆放策略不同。

所以一个模块应该能给出**多个候选 floorplan**，而不是一个固定模板。

## 2. 例子：同样的面积，不同的长宽比

假设目标面积相同（仅作示意，不对应真实项目）：

| 目标 | 可能的摆放 | 代价 |
| --- | --- | --- |
| 200 × 200 | 3 行、输入对居中、电源/输出在边缘 | 接近正方形，电源/地回流短，但宽度可能不够 |
| 100 × 400 | 更少的行、更多组并排/上下堆叠 | 长条形，电源/地/走线更长，匹配组可能被拉长 |
| 400 × 100 | 更多列、输入对/输出分居左右 | 很宽，横向走线多，边缘器件环境差异大 |

“总面积一样”不代表“难度一样”。面积相同，**形状、利用率、寄生、匹配、电源回流**都会变。

## 3. 变体生成的基本约束

1. 匹配组不能拆散；共质心/交叉指状的组必须保持内部结构。
2. 敏感区优先：先放 sensitive core，再放非敏感区。
3. 电源/地/ESD 路径优先：输出级、PAD、主干位置决定可摆范围。
4. 走线预留：通道、线宽、过孔、屏蔽都要计入，不是“摆完再说”。
5. 目标 bbox：给定 W×H 后，行数/列数/组顺序是约束求解，不是随意拉伸。

## 4. 输出应该是什么

一个变体至少包含：

- `target_width_um` / `target_height_um` / `aspect_ratio`；
- 每个 group 的位置/尺寸；
- 敏感区/非敏感区/预留通道；
- 面积利用率、空白率、最大长宽比；
- 风险：哪些组被拉长、哪些电源/地路径变长、哪些匹配环境变差；
- 选择的理由。

最终不是“AI 选一个”，而是给模拟/版图工程师**可比较的候选**。

## 5. 当前实现与下一步

当前 demo 只生成一个默认 band 布局（`floorplan.svg/json`）。下一步可以：

- 增加 `--target-aspect` / `--target-width` / `--target-height`；
- 生成 square / wide / tall 三个候选；
- 用同一套 role/match/area 数据比较利用率、walk length、电源回流、匹配组拉长风险；
- 把选中的变体写回 `Layout Card` 的 floorplan 区块。

> 这一步还没有实现；先把“多候选”的概念和输入/输出定义清楚。

## 6. 与敏感区的关系

- 敏感区（输入对、参考、trim、ESD/高压）应优先复用/固定形状；
- 非敏感区可以在目标 bbox 内自由填充；
- 不同长宽比下，敏感区可以保持不变，非敏感区重新排；
- 复用敏感区时，必须带工艺/电压/模块边界/版本条件。

## 相关

- [Floorplan sketch](04-floorplan.md)
- [Sensitive region / reuse](../layout-guideline/01-principles/sensitive-region-reuse.md)
- [Area target template](../layout-guideline/05-templates/area-target.yaml)
- [Layout Card template](../layout-guideline/05-templates/layout-card.md)
