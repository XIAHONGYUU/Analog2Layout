# Sources

## 公开层

- 通用原理、结构模板、合成示例；
- 可公开的方法论；
- 不包含公司/项目/PDK 具体内容。

## 私有层

建议单独存放：

```text
private-layout-guideline/
  rules/       # 公司 rule pack / PDK 数值
  modules/     # 真实模块 card
  cases/       # 脱敏前案例
  sources/     # 会议/评审/问题单索引
```

## 证据等级

每条知识/规则/案例建议记录：

| 字段 | 含义 |
| --- | --- |
| `source_id` | 来源/会议/问题单 ID |
| `evidence_level` | A/B/C 或等价 |
| `applicability` | 工艺/项目/模块/条件 |
| `owner` | 谁确认 |
| `status` | draft/reviewed/active/superseded |
| `counterexample` | 反例/不适用条件 |

## 关联方式

公开层与私有层用 ID 关联，不复制内容：

```text
layout-card.md  → source_id: KB-xxx
principle       → source_id: KN-xxx
case            → source_id: CASE-xxx
rule pack       → rule_key: mos.sd_ext_um
```
