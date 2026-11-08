# 约束排布试验（2026-11-07）

独立算法试验；不消费 LDO 草稿，不修改项目基线。所有尺寸和规则是合成测试条件，不是 PDK 或 owner 批准的工程规则。

## 运行

```bash
python3 -m venv /tmp/a2l-ortools-experiment-env
/tmp/a2l-ortools-experiment-env/bin/pip install ortools==9.15.6755
/tmp/a2l-ortools-experiment-env/bin/python experiment.py
```

脚本将结果和 SVG 写入自身目录。`requirements-lock.txt` 保存本次实际环境。

## 方法

- 8 个固定方向矩形，整数坐标；全部对象必须保留。
- 基线：first-fit shelf，扫描全部指定整数宽度，比较输入顺序与高度排序；加入纵向间距，结果经独立规则检查筛选。不是原项目脚本的直接跑分。
- CP-SAT：与基线相同的几何与规则，最小化外框 W×H；外框宽高均不超过 100 个单位。使用合法 shelf 解提供上界和提示。
- 每个实例分别限时 1 秒、5 秒，单线程、seed=0；只测求解调用时间，不包含模型构建、导入与绘图。每档仅运行一次，不能代表稳定性能统计。
- 矩形 case：全部对象之间至少沿 X 或 Y 一个轴分离 1 单位。
- 关系 case：在上述条件外，A 位于 B 左侧且同 Y；C/D 至少沿一个轴分离 3 单位。
- 阶梯 case：L 形由两个固定相对位置的矩形组成，Q 可以进入凹口；间距为 0，边界接触允许。shelf 仅按外接矩形排布，用来展示形状表达差异，不是两个同等形状能力算法的纯速度比较。
- 各 case 独立复核：对象集合、整数坐标、包含、矩形部件间距、位置关系、面积。
- 负例：篡改坐标制造重叠必须被拒绝；将外框限制为 2×2 必须返回 INFEASIBLE。

## 解释边界

FEASIBLE 不是最优证明；结果带 best_bound。OPTIMAL 只针对本试验有限整数域和已编码规则。未测试旋转、共享 ring、自动行列选择、连线、真实 LDO 约束或大规模实例。

生成图仅用于解释排布；results.json 是实测结果，experiment.py 是可复核模型和检查代码。
