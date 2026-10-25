# Modules

每个模块一个目录，至少包含：

```text
02-modules/<module>/
  README.md        # 模块特性、信号链、最怕什么
  layout-card.md   # 一页 card（版图第一眼看的）
  intent.yaml      # 结构化意图（模拟填写/确认）
```

可选：

```text
  floorplan.svg    # 布局草图
  cases.md         # 模块相关案例
  change-log.md    # 修改记录
```

## 写模块页的顺序

1. 一句话：这个模块做什么？
2. 信号链/电源域：谁进来、谁出去、参考是什么？
3. Top 3 风险：这个模块最容易错在哪？
4. 哪些器件/网络必须一起处理？
5. 哪些是禁止动作？
6. 画完后怎么验证？

## 当前示例

- [`two-stage-ota/`](two-stage-ota/)：合成示例，和 `examples/two_stage/` 的 demo 对应。
- [`bgr/`](bgr/)：匹配 + 启动 + 参考回流的示例。
- [`vcom/`](vcom/)：大功率输出 + 电阻串/trim + 稳定性的示例。
- [`bgr-vcom-comparison.md`](bgr-vcom-comparison.md)：同一原则在两个模块里的不同优先级。
