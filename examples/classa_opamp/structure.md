# M6/M7/R1/M11/M12/M13 的结构（实际是 class A）

![第二级和输出级](second-stage.png)

> **先纠正：这不是 class-AB push-pull。**
> M13 的栅极 `n003` 是偏置节点，只有 M14 的栅极 `n012` 由信号驱动；
> M13 是 PMOS 电流源负载，M14 是唯一的信号输出管。输出级是 **class A**。
> 之前把 M13/M14 说成 class-AB 互补输出是错的。

## 节点

| 节点 | 作用 |
| --- | --- |
| `n007`, `n005` | 第一级差分输出（M1/M2 漏极） |
| `n006` | M6/M7/M11 的 PMOS 栅偏置 |
| `n011` | M6/M8 支路中间点；M8 二极管连接 |
| `n012` | 第二级单端输出；M14 栅极；Cc 一端 |
| `n003` | M11 漏极、M12/M13 栅极、R1 上端；**M13 的偏置** |
| `n004` | M11 源极、M12 漏极（floating bias node） |
| `VOUT` | M13/M14 漏极相连的输出 |

## 1. M6/M7：第二级 common-gate

```text
n007 ── M6(PMOS) ── n011 ── M8(NMOS diode) ── VSS
n005 ── M7(PMOS) ── n012 ── M9(NMOS mirror) ── VSS
```

- M6/M7 的栅极都接 `n006`（偏置），不是信号输入；
- 信号从源极 `n007/n005` 进来，所以是 **PMOS common-gate**；
- M8 二极管连接，M9 镜像；
- 两支路电流差在 `n012` 汇总，得到单端输出。

M6/M7/M8/M9 是第二级增益/电平转换，不是 class-AB 输出级。

## 2. M10：n006 的偏置电流源

```text
n006 ── M10(NMOS) ── VSS
```

- M10 栅极接 `ibias`，源极 VSS，漏极 `n006`；
- 它从 `n006` 拉电流，设定 M6/M7/M11 的栅偏置；
- 不直接传送信号。

## 3. M11/M12/R1：M13 的 PMOS 偏置电流源

```text
VDD ── M12(PMOS) ── n004 ── M11(PMOS) ── n003
                              │ gate n006
n003 ── R1(3.33 kΩ) ── n006
```

- M12：源极 VDD，漏极 `n004`，栅极 `n003`；
- M11：源极 `n004`，漏极 `n003`，栅极 `n006`；
- R1 跨在 `n003` 和 `n006` 之间；
- `n004` 没有直接接电源/地，是 floating bias node。

关键关系：

```text
I_M12 = I_M11
I_M11 = I_R1 = (V(n003) - V(n006)) / R1
```

R1 的压降设定 M11/M12 支路电流；M12 的栅极 `n003` 又接到 M13 的栅极，
所以 **M13 镜像 M12 的电流**。M11/M12/R1 是 M13 的偏置电流源，不是
class-AB 的互补输出偏置。

## 4. M13：PMOS 电流源负载

```text
VDD ── M13(PMOS) ── VOUT
        gate n003 (bias)
```

- M13 栅极 `n003` 来自 M11/M12/R1 的偏置，没有信号路径；
- 它给 VOUT 提供直流拉高电流；
- 它是 **current-source load**，不是由信号驱动的 push-pull 输出管；
- 因此不能把 M13/M14 叫做互补 class-AB 输出对。

## 5. M14：唯一的信号输出管

```text
VOUT ── M14(NMOS) ── VSS
        gate n012 (signal)
```

- M14 栅极 `n012` 是第二级单端输出；
- 信号只驱动 M14；
- M14 是 common-source；
- 输出级是 **NMOS common-source + PMOS current-source load**，即 **class A**。

## 6. Cc 和 R1

网表：

```text
Cc:  VOUT ── n012   5 pF
R1:  n003 ── n006   3.33 kΩ
```

- `Cc` 是 VOUT 到 n012 的 Miller 补偿；
- `R1` 不在 Cc 的串联支路；
- `R1` 是 M11/M12 偏置电流源的设定电阻，不是 Cc 的 nulling resistor。

## 一句话总结

- **M6/M7**：第二级 PMOS common-gate；
- **M8/M9**：NMOS 镜像负载，合成单端 n012；
- **M10**：n006 偏置电流源；
- **M11/M12/R1**：M13 的 PMOS 偏置电流源，R1 设定电流；
- **M13**：PMOS 电流源负载，栅极是偏置，不是信号；
- **M14**：唯一的信号输出管，class-A common-source；
- **Cc**：VOUT 到 n012 的 Miller 补偿。

所以：**这不是 class-AB OP，本质上只有 N 管输出。**
