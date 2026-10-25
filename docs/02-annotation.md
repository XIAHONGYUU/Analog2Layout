# 器件角色标注规范（v0.1）

> **Owner：模拟工程师/模拟团队。** 角色表不是 AI 自由生成的标签体系，而是模拟设计对“这个管子在电路里干什么”的正式约定。AI/agent 可以提出候选、检查覆盖、解释结果，但 role 的新增/删除/改名和 rule 数值必须由 analog owner 确认。

## 1. 核心字段

在原理图器件属性或导出网表的参数里写：

```spice
M1 n1 vinp ntail vss nmos w=5u l=0.5u nf=4 m=1 \
   role=input_pair match=DP group=IN layout=common_centroid
```

| 字段 | 必填 | 作用 | 不影响 |
| --- | --- | --- | --- |
| `role` | 是 | 决定面积模型、dummy 策略、floorplan band、delta 规则 | 不改变 W/L |
| `match` | 关键器件建议 | 电气匹配组；同组器件必须同尺寸/同环境 | 不要求同 group |
| `group` | 可选 | 功能/布局分组；用于 floorplan 的框和报告 | 不表示电气匹配 |
| `layout` | 可选 | 期望版图模式：`common_centroid`、`interdigitated`、`stacked`、`minimal` | 不生成合法版图 |
| `ratio` | 可选 | 电流镜/配对比例（与 AnalogLoop manifest 对齐） | 不改变 W/L |
| `tunable` | 可选 | sizing agent 是否允许改这个器件 | 不影响面积 |
| `constraints` | 可选 | 角色级约束列表，如 `same_wl`、`common_centroid`、`max_current_density` | 作为 review 依据 |

`match` 和 `group` 的区别很重要：

- 输入对 M1/M2：`match=DP`，同时 `group=IN`；
- 输出级 M6/M7：不需要电气匹配，但属于同一个功能组，写 `group=OUT`；
- 一个 group 里可以只有一部分器件属于同一个 match。

## 2. 角色表

| role | 中文 | 典型器件 | 面积/布局关注点 |
| --- | --- | --- | --- |
| `input_pair` | 差分输入对 | 输入对管 | 对称、共质心、输入寄生、噪声、offset |
| `current_mirror` | 电流镜 | 负载/偏置镜像 | 比例精度、Vth 匹配、边界 dummy |
| `cascode` | 共源共栅 | cascode 堆叠 | 源漏寄生、堆叠环境、dummy stack |
| `tail_current` | 尾电流源 | 差分对尾电流 | 对称、电流精度、common source |
| `output_stage` | 输出级 | 推挽/共源输出 | 电流密度、EM、宽金属、finger 数 |
| `compensation` | 补偿电容 | Miller/feed-forward cap | 值、耦合、屏蔽、面积 |
| `bias` | 偏置 | bias 分支 | 噪声、匹配、布线 |
| `enable_switch` | 使能管 | power-down 开关 | 电荷注入、漏电、dummy switch |
| `adj_switch` | 配置/Trim 开关 | trim/select 开关 | 开关匹配、dummy、控制线耦合 |
| `sense` | 检测/采样 | sense FET / 采样管 | 小寄生、开尔文连接 |
| `esd` | ESD 保护 | ESD 器件 | 规则驱动、pad ring |
| `dummy` | Dummy 管 | 边界/匹配 dummy | 电气不活跃、环境平衡 |
| `decap` | 去耦/补偿电容 | decap | 电源瞬态、面积、位置 |
| `unknown` | 未标注 | — | 面积和布局不可靠，必须修 |

运行 `python3 -m a2l roles` 可以打印当前版本的角色表。

## 3. 命名 fallback

没有 `role=` 时，a2l 会按名字推断（仅作为兜底）：

| 名字包含 | 推断 |
| --- | --- |
| `dummy`, `_dm` | `dummy` |
| `decap`, `_dec` | `decap` |
| `input`, `inp`, `inn`, `pair`, `diff`, `_dp` | `input_pair` |
| `mirror`, `mir`, `_cm` | `current_mirror` |
| `cascode`, `_cas` | `cascode` |
| `tail` | `tail_current` |
| `enable`, `_en` | `enable_switch` |
| `adj`, `trim`, `sel`, `_sw` | `adj_switch` |
| `output`, `_out` | `output_stage` |
| `bias`, `nbias`, `pbias`, `vb` | `bias` |
| `comp`, `_cc` | `compensation` |
| `sense`, `sns` | `sense` |
| `esd` | `esd` |

**不要依赖名字做长期契约**。名字在改图、复制、层次展开、后端导出时最容易丢；a2l 只把名字推断当作 suggestion，并在 `validate` 中提示。推荐：

- 原理图里把 `role` 做成 device property / CDF parameter；
- 网表导出时保留这些 property；
- 名字只用于人读和 fallback。

## 4. 推荐命名

如果团队暂时没有 property 流程，可以用可读的名字过渡：

```text
M1_DP    M2_DP     输入对
M3_CM    M4_CM     电流镜
M6_CAS   M7_CAS    cascode
M8_EN              enable
M9_ADJ             trim
M10_OUT            output
DM1_DP             输入对 boundary dummy
C1_CC              Miller cap
C2_DECAP           decap
```

但请把“名字约定”当作过渡方案，最终仍要把 `role` 落到属性里。

## 5. 标注检查

`a2l validate` 会检查：

- 缺 `w=` / `l=`；
- W/L ≤ 0；
- L 低于规则最小值（warning）；
- 电容值缺失或 ≤ 0；
- 关键 role 没有 `match`；
- `match` 组只有一个器件；
- role 无法解析（`unknown`）；
- 重复器件名；
- 使用 name fallback 的器件（提示 analog owner 确认）。

示例：

```bash
python3 -m a2l validate examples/two_stage/two_stage.sp
# CI 里可以强制要求显式 role=
python3 -m a2l validate examples/two_stage/two_stage.sp --require-explicit-roles
```

## 6. 与 AnalogLoop manifest 的对应

AnalogLoop 用 `roles.yaml` 的 manifest 记录 role/group/match/ratio/tunable/constraints，a2l 的 annotation schema 保留同样的语义，但把它放在原理图属性/导出网表的参数里：

```spice
M4 n2 n1 vdd vdd pmos w=5u l=1u nf=2 m=1 \
   role=current_mirror match=CM group=LOAD ratio=1 tunable=true \
   layout=interdigitated
```

```json
{
  "name": "M4",
  "role": "current_mirror",
  "match": "CM",
  "group": "LOAD",
  "layout": "interdigitated",
  "ratio": 1,
  "tunable": true,
  "constraints": ["same_wl", "common_centroid"]
}
```

原则和 AnalogLoop 一致：**名字是提示，manifest/annotation 是事实，validator 是仲裁。**

## 7. AI 如何参与标注

AI 适合做三件事：

1. **读拓扑**：diode-connected、mirror、cascode stack、diff pair、switch、output；
2. **读上下文**：网表注释、器件名、group、已知的 bias 网络；
3. **给出带证据的候选**：`role`、`confidence`、`evidence`（如“gate 与 drain 同网，疑似 diode-connected”）。

AI 不应该：

- 发明 W/L；
- 发明规则数值；
- 在不确定时强行给 role；
- 直接改原理图。

推荐流程：

```text
agent 读网表 → 输出 annotation JSON（含 confidence/evidence）
        ↓
a2l validate + 人工 review
        ↓
把确认后的 role 写回原理图属性
```

prompt 模板见 [`agent/prompts/annotate_roles.md`](../agent/prompts/annotate_roles.md)，schema 见 [`schemas/annotation.schema.json`](../schemas/annotation.schema.json)。

## 8. 公司规则里还应记录什么

v0.1 只覆盖面积/布局最相关的字段。真实落地建议扩展：

- `device_class`：core / IO / HV / ESD；
- `voltage_domain`：VDDx / VSSx；
- `current_density`：mA/µm；
- `matching_rule`：common-centroid / interdigitated / dummy count；
- `isolation`：deep nwell / guard ring / shielding；
- `orientation`：R0 / R90 / mirror；
- `keepout`：噪声/时钟布线禁入区；
- `company_rule_id`：公司规则库中的条目号。

这些字段应该由公司规则包定义，而不是写死在 a2l 里。
