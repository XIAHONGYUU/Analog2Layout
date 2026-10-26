# References / 查表入口

## The Art of Analog Layout

- Author: Alan Hastings
- Title: *The Art of Analog Layout*
- Edition: 2nd edition (Chinese edition also exists)
- Publisher: Pearson / 电子工业出版社（中文版）
- Status: **copyrighted textbook, not open source**

这本书不是开源教材。为了避免把版权 PDF 放进公开仓库，这里只保留书目、阅读地图和本地私有副本入口：

```text
references/
  README.md          # 本文件
  private/           # gitignored；放你自己的授权 PDF / 笔记
```

`references/private/` 已在 `.gitignore` 中；不要把出版社 PDF、扫描件或公司培训材料提交到公开仓库。

## 读什么

| 主题 | 用在当前项目 |
| --- | --- |
| Matching / mismatch | DP、CM、TAIL 的匹配、dummy、共质心 |
| Dummy devices | W 方向两端各一个 dummy，源漏共用，W/L 规则 |
| Guard rings / wells | DP/CM/TAIL/OUT 各自独立 ring，ring 间距 |
| Resistors / capacitors | MOSCAP vs MOM/MIM、密度、电压系数、线性度 |
| Failure mechanisms / ESD | IO/ESD 目标的 SAB、粗长输出管、latch-up |
| Floorplan / routing | 紧凑摆放、abutment、VDD/VSS 主干 |

## 公开/可查资料

- SkyWater SKY130 PDK 文档（open PDK，规则以 PDK 为准）
- OpenFASOC / ALIGN / Magic / Netgen 文档（开源 analog layout 流程）
- 课程讲义和开源 PDK 的 matching/ESD application notes

> 教科书给的是方法和典型做法；具体 WPE/STI/ring/dummy 数值必须回到 PDK 或公司 rule deck。
