# Virtuoso white line、white-line layout plan、floorplan sketch

> 三者相关，但不是同一个 artifact。混用会让“白线图”这个说法失去工程含义。

## Virtuoso white line

在 Virtuoso 里，white line 是一种**辅助线/标志线**，可以画在 schematic 同一张图上。
它本身不是版图，也不是自动 floorplan；它的价值是让版图工程师在电路旁边直接看到：

- 器件/功能组怎么摆；
- ring / SAB / keepout 在哪里；
- 哪些尺寸/排列方式需要特别说明；
- 哪些地方不能动。

照片里的 IO 例子就是这种用法：上面 LS 是一整排阵列，中间 input/output 中压管放一起，下面是做了 SAB 的输出 MOS，旁边是 ESD 阵列；白线直接把版图结构画在电路图空间里。

## 本工作区的 white-line layout plan

`docs/targets/sky130-opamp/white-line.svg/png` 是这一类图：

- 左边是电路参考；
- 右边是版图结构：每个 MOS 单独成阵列块，DP/CM 有 ring，dummy 用虚线；
- 标注尺寸/排列/keepout/短注释；
- 它不是 schematic 符号上的注释框，也不是合法版图。

## 本工作区的 floorplan sketch

`floorplan.svg/json` 是另一类东西：

- 从 role / match / area 自动推导出的**块级布局草图**；
- 有 group 位置、对称轴、routing channel、PEX-fix reserve；
- 用来比较面积/形状/组间关系，不是手工 white-line 结构图；
- 它不是合法版图，也不是 DRC/LVS/PEX 签核结果。

## 怎么配合

```text
schematic + white-line layout plan
        ↓ 手工/半自动细化
真实版图
        ↓ 提取
floorplan sketch / area report / delta
```

- white-line 回答“这个模块在版图上大概长什么样、ring/SAB/keepout 在哪”；
- floorplan sketch 回答“组和组之间怎么摆、面积/形状/通道是否合理”；
- 两者可以共享 role / match / group / sensitive-region 数据，但图形语义不同。

## 当前示例

SKY130 两级 OP 的 white-line **layout plan**：

- [white-line.png](targets/sky130-opamp/white-line.png)
- [white-line.svg](targets/sky130-opamp/white-line.svg)
- [说明](../layout-guideline/02-modules/sky130-two-stage-opamp/white-line.md)

## 相关

- [Floorplan sketch 说明](04-floorplan.md)
- [Layout Card 模板](../layout-guideline/05-templates/layout-card.md)
- [Sensitive region / reuse](../layout-guideline/01-principles/sensitive-region-reuse.md)
