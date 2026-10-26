# 教科书里这个结构怎么解释

参考：P. E. Allen, D. R. Holberg, *CMOS Analog Circuit Design*, 3rd ed.,
Oxford University Press, 2012, **Sec. 7.6 / Fig. 7.6-17**（class-AB output stage）。

> 说明：我手头能取到的是该书的 2nd-ed PDF；3rd-ed 的 Fig. 7.6-17 编号来自
> 上游 README。下面按教科书中 class-AB 输出级/浮动电流源的原文概念，加上
> 本网表的实际连接来解释；没有把受版权保护的 PDF 或图复制进仓库。

## 1. 教科书先讲 class A / B / AB 的区别

- **Class A**：输出管一直导通，线性好，但静态电流大、效率低。
- **Class B**：每只管子只导通半周期，效率高，但交越附近有死区，失真大。
- **Class AB**：静态时两只输出管都微微导通，信号来到时一只电流增大、另一只
  减小；兼顾效率和交越失真。

教科书对 class-AB 输出级的核心问题不是“怎么放大”，而是：

1. 怎样把两只输出管的**静态电流**设得小而稳定；
2. 怎样让大信号时一只管子能提供大电流，而另一只不会完全关死造成交越失真；
3. 怎样在低电源电压下保住输出摆幅和增益。

## 2. 教科书里的 class-AB 输出级

典型结构是两只互补 common-source 管：

```text
VDD ── MP(PMOS) ── VOUT ── MN(NMOS) ── VSS
```

- MP 的栅极偏置在 `VDD - |VGS_P|` 附近；
- MN 的栅极偏置在 `VSS + VGS_N` 附近；
- 静态时两只都微导通，静态电流 `IQ` 由偏置网络决定；
- 信号使两个栅极向相反方向变化：一边 |VGS| 增大，另一边 VGS 减小；
- 大信号时一边提供大电流，另一边接近关断，但交越点仍由 `IQ` 保持平滑。

教科书强调：**class AB 的关键是偏置电路，而不是输出管本身**。`IQ` 太小会
出现交越失真，`IQ` 太大会变成 class A、功耗上升；而且 `IQ` 要随电源/工艺/
温度稳定。

## 3. floating current source 的作用

教科书里的 class-AB 偏置常用一个**浮动电流源**（floating current source）：

- 它不直接接在 VDD 或 VSS 上，而是“浮”在输出管的栅极之间；
- 它给两只输出管建立一个固定的栅-栅电压差；
- 这个电压差决定静态电流 `IQ`；
- 因为它是电流源而不是固定电压源，`IQ` 对电源电压和输出摆幅没那么敏感。

在本电路里，这个角色由 **M11/M12/R1** 承担：

```text
VDD ── M12 ── n004 ── M11 ── n003
                     gate n006
n003 ── R1 ── n006
```

- M12 的栅极接 n003，M13 的栅极也接 n003，所以 M13 镜像 M12；
- M11 的栅极接 n006，源极接 n004，漏极接 n003；
- R1 跨在 n003 和 n006 之间，R1 的压降设定 M11/M12 支路电流；
- n004 是 floating node，所以这是“floating current source”，不是普通
  接地电流源。

静态电流关系可以粗略写成：

```text
I_M12 = I_M11
I_M11 = I_R1 = (V(n003) - V(n006)) / R1
I_M13 / I_M12 ≈ (W/L)13 / (W/L)12 = (640/2) / (240/2) = 2.67
```

所以 R1 不只是“一个电阻”，它是 **class-AB 静态电流的设定元件**。

## 4. 为什么还需要 M6–M9

M11/M12/R1 主要建立 PMOS 输出管 M13 的栅偏置；NMOS 输出管 M14 的栅极
n012 由另一条 class-AB 控制/增益支路建立：

```text
n007 ── M6(PMOS) ── n011 ── M8(NMOS diode) ── VSS
n005 ── M7(PMOS) ── n012 ── M9(NMOS mirror) ── VSS
```

- M6/M7 是 PMOS common-gate，栅极 n006 是偏置，源极接第一级差分输出；
- M8 二极管连接，M9 镜像；
- 两支路电流差在 n012 汇总，n012 驱动 M14 的栅极；
- M10 从 n006 拉电流，给 M6/M7/M11 提供偏置。

所以教科书里的 class-AB 输出级不是“只靠两只输出管”，而是：

```text
第一级差分 → 第二级 common-gate + 镜像 → n012 → M14
                     │
                     └─ M6–M9 的 class-AB 偏置/增益

n006 / R1 / M11 / M12 → n003 → M13
```

两条偏置支路共同保证 M13/M14 在静态时都微导通，在信号时一推一拉。

## 5. 小信号和补偿

- 输出级 M13/M14 都是 common-source，所以有电压增益；
- 输出电阻约为 `rds13 || rds14`，比 source follower 大，因此增益高；
- Cc 从 VOUT 接到 n012（M14 栅极），是跨输出级的 Miller 补偿；
- 教科书在 class-AB 这一节还会讨论：输出摆幅、静态电流、交越失真、
  小信号增益、补偿后极点和 slew rate。

本电路是 2 V 低电源版本，教科书里的很多结论仍然成立，但 headroom 更紧：
输出管不能堆太多 VDS，偏置点要更小心。这也是为什么上游 README 说 slew rate
是它的主要短板。

## 6. R1 的争议

上游 README 把 R1 说成 “zero-cancellation resistor ≈ 1/gm6”。但从实际网表：

```text
Cc: VOUT ── n012   5 pF
R1: n003 ── n006   3.33 kΩ
```

R1 **不在 Cc 的串联支路**。按连接，R1 首先是 class-AB 浮动电流源的偏置电阻，
它通过 M11/M12 的反馈设定静态电流；它是否还通过这个环路影响零点，需要看
报告/仿真，不能直接把它当成和 Cc 串联的 nulling resistor。

## 7. 对应到本电路的器件

| 器件 | 教科书里的角色 |
| --- | --- |
| M13 | PMOS class-AB 输出 pull-up |
| M14 | NMOS class-AB 输出 pull-down |
| M11/M12/R1 | floating class-AB bias current source |
| M13 | M12 的镜像输出 |
| M6/M7 | 第二级 PMOS common-gate |
| M8/M9 | NMOS 镜像负载，合成单端输出 |
| M10 | n006 偏置电流源 |
| Cc | VOUT 到 n012 的 Miller 补偿 |
