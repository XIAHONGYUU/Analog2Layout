# Cases

这里放**脱敏后的案例**，不是原始会议记录/项目档案。

## Case 卡格式

```text
id: CASE-YYYY-NNN
title: 一句话
type: failure | near_miss | verification | tradeoff
module: BGR / LDO / VCOM / SADC / AFE_CH / ...
symptom: 现象
mechanism: 机制（可确认/待确认）
layout_action: 当时做了什么
why_it_worked_or_failed: 为什么
evidence: 仿真/后仿/测试/问题单
counterexample: 反例/不适用条件
owner: analog/layout
status: draft | reviewed
```

## Case 选择标准

- 能说明一个**可迁移的判断结构**；
- 有明确的现象和至少一条验证证据；
- 能写出适用边界/反例；
- 不依赖具体项目名和人名。

## 不要把

- 原始会议逐字稿直接放进来；
- 真实 PDK 数值、公司规则、客户信息放进来；
- 没有验证的“猜测”写成“根因”。
