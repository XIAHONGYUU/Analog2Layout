# SKY130 PDK facts

这个目录只保存**可追溯的 PDK 事实**，不保存完整 PDK，也不是 DRC signoff。

## 结论：1.0 µm 的 AA ring 不是 PDK 值

当前 workspace 里的 `1.0 µm ring / 0.8 µm gap` 来自 class-A 的
**educational placeholder**，不是 Sky130 PDK 规则。

`docs/targets/sky130-opamp/make_white_line_layout.py` 自己就写着：

```text
ring: 1.0 µm width / 1.5 µm gap
educational placeholder, not PDK
```

`pdk/sky130/facts.json` 的 `ring` 节点因此明确标记：

```json
"pdk_defined": false
```

PDK 实际定义的是 `diff` / `tap` / `nwell` / `dnwell` / contact 的最小
width、space、enclosure，例如：

| fact | value | rule |
| --- | ---: | --- |
| difftap min width | 0.15 µm | `difftap.1` |
| difftap min space | 0.27 µm | `difftap.3` |
| diff/tap non-coincident space | 0.13 µm | `difftap.7` |
| nwell min width | 0.84 µm | `nwell.1` |
| nwell min space | 1.27 µm | `nwell.2a` |
| nwell enclosure of dnwell | 0.4 µm | `nwell.5` |
| dnwell enclosure of nwell | 1.03 µm | `nwell.6` |
| dnwell min width | 3.0 µm | `dnwell.2` |
| dnwell min space | 6.3 µm | `dnwell.3` |
| diff enclosure of licon | 0.04 µm | `licon.5` |
| tap enclosure of licon | 0.12 µm | `licon.7` |

## 为什么有 `facts.json` 而不是直接引用 PDK 文件

- PDK deck 很大，且不应把完整 runset 复制进本仓库；
- 每个 fact 都带 `drc_rule`、`source_line`、`source_sha256`；
- 生成 white-line 时只能引用 **fact key**，不能把 heuristic 伪装成 PDK；
- 需要更新时，替换本地 deck，重新核对 hash 和 line。

当前参考 deck：

```text
out/refs/sky130.lydrc
sha256 81cf4f998fc6fb6925ccc8618afba3dc8530058db1d0e31dc1f6ad5299e52372
deck revision 2020-10-04 v1.0
```

官方规则入口：

- <https://skywater-pdk.readthedocs.io/en/main/rules/periphery.html>

## 使用规则

1. **PDK fact**：必须有 `rules.*.drc_rule`，并在 `facts.json` 中存在。
2. **Layout heuristic**：必须显式写 `source=heuristic`，不能写成 PDK。
3. 1.0 µm ring、3.0 µm DNW margin、0.8 µm gap 目前都属于 heuristic，不是
   PDK fact。
4. 任何 DRC/LVS 结论必须由实际 deck 跑出，不由本目录推断。

## Resistor segment spacing

`0.5 µm` segment-to-segment gap is **not** a PDK rule.

Relevant Sky130 checks from the local deck:

| rule | value | meaning |
| --- | ---: | --- |
| `poly.2` | 0.21 µm | minimum poly spacing |
| `poly.3` | 0.33 µm | minimum poly resistor width |
| `poly.9` | 0.48 µm | minimum poly resistor space to poly or diff/tap |

`0.5 µm` is a layout choice with 0.02 µm margin above the `poly.9` bound.
If the folded resistor is one continuous poly shape, the actual notch/self-spacing
must be checked by the DRC deck; if dummy/segments are separate shapes, `poly.9`
is the relevant bound.
