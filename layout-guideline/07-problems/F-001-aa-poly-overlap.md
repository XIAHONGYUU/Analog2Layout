# Problem Record — F-001

**模块**：SKY130 LDO / generic white-line
**状态**：open
**Owner**：analog + layout
**来源**：owner 举例（2026-11-09）；具体项目细节待项目运行中补充

## 1. 现象

在非预期 MOS 区域出现 AA/diff 与 poly 重叠。它可能形成一个非预期的 MOS
结构、寄生器件或错误连接，而不是我们想要的门极。

## 2. 机制

- 已确认：DRC 通常允许 poly 与 diff 重叠，因为两者相交本身就会形成 MOS；
  因此这不一定是一个 DRC violation。
- 候选：阵列边界、dummy 放置、电阻 body、poly 走线、block 重叠或坐标错误
  导致非预期重叠。
- 未知：具体发生位置、是否造成电学后果、现有检查是否能发现。

## 3. 版图动作

待补充：当时改了什么（位置/层/尺寸/连接）。

## 4. 为什么有效/无效

这是 **design-intent check**，不是 DRC：

- DRC 只看几何合法性；
- 我们需要知道“哪些 poly∩diff 是有意的门极”；
- 因此 checker 必须有 intended-gate whitelist，而不是只查 overlap。

## 5. Guideline 缺口

- 缺的是：rule + verification recipe
- 具体缺什么：每个 bank/array 的 intended gate region 没有显式记录；
- 应该怎么写：在 white-line input 或 manifest 中记录 intended gate shapes；
  checker 对所有 poly∩diff 做差集，非白名单重叠报 `HARD` 或 `REVIEW`。

## 6. 重复问题

- recurrence_of：none
- 同类问题次数：1（owner 举例）
- 如果重复：升级为 rule + checklist + test，不只改图。

## 7. Patch

| 文件 | 改什么 | 版本 |
| --- | --- | --- |
| `docs/14-sky130-rule-check.md` | 增加 intended-gate overlap 检查项 | draft |
| `a2l/layout/checks_sky130.py`（拟议） | `check_intended_gate_overlap()` | 未实现 |

## 8. 验证

- 后仿/测试/评审证据：待补
- 适用边界：所有 MOS bank / dummy / resistor 区域
- 未验证项：checker 实现、whitelist 来源、误报率
