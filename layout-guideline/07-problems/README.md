# Problems：问题驱动的 guideline 迭代

> Layout Guideline 最重要的不是“写得多全”，而是**以前项目出现的问题不再重复犯**。

## 记录什么

每个真实问题一条记录，至少包含：

- 现象（symptom）；
- 机制/根因（confirmed / candidate / unknown）；
- 当时的版图动作（layout_action）；
- 为什么有效/无效；
- 暴露出的 guideline 缺口（guideline_gap）；
- 要更新哪一层：principle / pattern / module / card / rule；
- 是否重复问题（recurrence_of）；
- owner、状态、证据、适用边界。

模板：[`../05-templates/problem-record.md`](../05-templates/problem-record.md)

示例：[`example-bgr-reference-return.md`](example-bgr-reference-return.md)

## 闭环

```text
问题出现
  → 记录（问题卡）
  → 去重：查已有 problem/case
  → 判定 guideline 缺口
  → 更新 principle / pattern / module / card / rule
  → 验证（后仿/测试/评审）
  → 发布新版本
```

## 重复问题门

新增问题前先搜 `07-problems/` 和 `04-cases/`：

- 如果 `recurrence_of` 已存在：不要新建重复条目，升级原条目并标 `recurrence`；
- 如果同一机制出现 ≥2 次：必须产生一条 guideline 变更，否则不允许关闭；
- 如果只是项目特定数值：进 private rule pack，不进 public principle。

## 与 04-cases 的区别

| | `04-cases/` | `07-problems/` |
| --- | --- | --- |
| 用途 | 说明一个判断结构 | 跟踪一个真实问题的闭环 |
| 状态 | 稳定后保留 | 有 open/fixing/verified |
| 输出 | case card | guideline patch + case candidate |
| 关注 | 为什么 | 下次怎么不再犯 |
