# 教科书里的 class-AB，和这个电路为什么不是

参考：P. E. Allen, D. R. Holberg, *CMOS Analog Circuit Design*, 3rd ed.,
Oxford University Press, 2012, **Sec. 7.6 / Fig. 7.6-17**（class-AB output stage）。

> 说明：我手头能取到的是该书的 2nd-ed PDF；3rd-ed 的 Fig. 7.6-17 编号来自
> 上游 README。下面先讲教科书的 class-AB 原则，再用它检查本网表。结论是：
> **本网表不满足 class-AB 的基本条件，实际是 class A。**

## 1. 教科书怎么定义 class A / B / AB

- **Class A**：输出管一直导通，线性好，但静态电流大、效率低。
- **Class B**：每只管子只导通半周期，效率高，但交越附近有死区，失真大。
- **Class AB**：静态时两只输出管都微微导通，信号来到时一只电流增大、另一只
  减小；兼顾效率和交越失真。

关键点：**class AB 至少要有两只由信号驱动的互补输出管**。如果一只输出管的
栅极只是固定偏置，它就是 current-source load，不是 push-pull 输出管。

## 2. 教科书里的 class-AB 输出级

典型结构是两只互补 common-source 管：

```text
VDD ── MP(PMOS) ── VOUT ── MN(NMOS) ── VSS
```

- MP、MN 的栅极都要被信号驱动；
- 静态时两只都微导通；
- 偏置网络建立一个固定的栅-栅电压差，决定静态电流 `IQ`；
- 信号使两个栅极向相反方向变化：一边 |VGS| 增大，另一边 VGS 减小；
- 大信号时一边提供大电流，另一边接近关断，但交越点仍由 `IQ` 保持平滑。

教科书强调：class AB 的关键是**偏置电路**，`IQ` 太小会交越失真，太大会变成
class A、功耗上升。

## 3. 用这个标准检查本网表

本网表：

```text
M13: VDD ── M13(PMOS) ── VOUT
     gate n003

M14: VOUT ── M14(NMOS) ── VSS
     gate n012
```

问题在于 **M13 的栅极 n003**：

- n003 接 M11 漏极、M12 栅极、R1；
- n003 没有接 n012，也没有接第一级输出；
- n003 是 M11/M12/R1 偏置环路产生的**偏置节点**；
- 所以 M13 是 **PMOS 电流源负载**，不是由信号驱动的 push-pull 输出管。

只有 M14 的栅极 n012 由第二级信号驱动。输出级实际是：

```text
VDD ── M13(PMOS current source) ── VOUT ── M14(NMOS common-source) ── VSS
```

这是 **class A**：M13 提供直流/有限拉高电流，M14 负责信号电流。
它不是 class-AB push-pull。

## 4. 那 M11/M12/R1 是什么

它们是 M13 的 **PMOS 偏置电流源**：

```text
VDD ── M12 ── n004 ── M11 ── n003
                     gate n006
n003 ── R1 ── n006
```

- R1 设定 M11/M12 支路电流；
- M12 的栅极 n003 接 M13 的栅极；
- M13 镜像 M12 的电流；
- n004 是 floating bias node；
- 但这只建立 M13 的**静态电流**，没有把信号送到 M13 栅极。

所以它不能被称为 class-AB 的 floating current source；它只是 M13 的偏置电流源。

## 5. M6–M9 是什么

```text
n007 ── M6(PMOS) ── n011 ── M8(NMOS diode) ── VSS
n005 ── M7(PMOS) ── n012 ── M9(NMOS mirror) ── VSS
```

- M6/M7 是 PMOS common-gate；
- 栅极 n006 是偏置，信号从源极 n007/n005 进来；
- M8 二极管连接，M9 镜像；
- 两支路电流差在 n012 汇总，驱动 M14；
- 这是第二级增益/电平转换，不是 class-AB 输出级。

## 6. 教科书 class-AB 和本电路的差别

| 条件 | 教科书 class AB | 本网表 |
| --- | --- | --- |
| 两个互补输出管 | 需要 | M13 + M14 |
| 两个输出管栅极都由信号驱动 | 需要 | **只有 M14 栅极 n012 是信号** |
| M13 栅极 | 信号/浮动偏置 | **n003 固定偏置** |
| 输出级类型 | push-pull class AB | **class A** |
| 静态电流控制 | 浮动偏置 | M11/M12/R1 设 M13 电流 |
| 大信号 | 双向大电流 | 只有 M14 能主动拉低；拉高受 M13 电流源限制 |

## 7. 结论

- 教科书 Fig. 7.6-17 讲的是 **真正的 class-AB push-pull 输出级**；
- 本网表的 M13 栅极没有信号路径，只有 M14 被信号驱动；
- 所以 **这个 OP 不是 class AB，而是 class A（NMOS 输出 + PMOS 电流源负载）**；
- 上游 README 的 "class AB" 说法和实际网表不一致，应该以网表为准；
- 如果目标是真正的 class AB，需要换一个 **两个输出管栅极都被信号驱动** 的电路，
  或者重新设计 M13 的栅极驱动/浮动偏置网络。

## 8. R1 的争议

上游 README 把 R1 说成 “zero-cancellation resistor ≈ 1/gm6”。但从实际网表：

```text
Cc: VOUT ── n012   5 pF
R1: n003 ── n006   3.33 kΩ
```

R1 **不在 Cc 的串联支路**。按连接，R1 是 M11/M12 偏置电流源的设定电阻；
它是否还通过这个环路影响零点，需要看报告/仿真，不能直接把它当成和 Cc 串联的
nulling resistor。
