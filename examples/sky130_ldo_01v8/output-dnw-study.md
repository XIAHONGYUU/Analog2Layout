# XM61 output-FET DNW shape / area study

Status: **Step-1 geometry study**, not GDS/DRC/LVS.

Assumptions:

```text
total W = 5000 µm
5 sub-banks × 1000 µm total W
body ring 2.0 / gap 2.0
shared ring wall between adjacent sub-banks
DNW margin 2.0 µm
outer DNW guard ring 2.0 / 2.0
```

## Options

| opt | W/finger | fingers/sub | array | sub-banks | DNW | DNW area | AR | guard envelope |
| --- | ---: | ---: | --- | --- | --- | ---: | ---: | --- |
| A | 5.000 | 200 | 4×50 | 5×1 | 55.0×148.0 | 8,140 | 0.37 | 63.0×156.0 |
| B | 10.000 | 100 | 4×25 | 1×5 | 143.5×54.4 | 7,806 | 2.64 | 151.5×62.4 |
| C | 14.925 | 67 | 2×34 | 1×5 | 182.2×43.1 | 7,844 | 4.23 | 190.2×51.1 |
| D | 20.000 | 50 | 2×25 | 1×5 | 143.5×53.2 | 7,634 | 2.70 | 151.5×61.2 |
| E | 25.000 | 40 | 1×40 | 5×1 | 46.4×164.0 | 7,610 | 0.28 | 54.4×172.0 |

Current compiler choice:

```text
W ≈ 20.408
49 fingers/sub
5×1 sub-banks
DNW2 54.14 × 141.04
area 7,636
AR 0.38
```

## Observation

DNW area varies by less than **7%** across these options:

```text
7,610 … 8,140 µm²
```

So the real decision is **shape**:

- A/E: tall, narrow;
- B/D: wide, moderate aspect;
- C: very wide.

## Recommendation

For a typical output-DNW shape, **D** is the best compromise:

```text
W=20 µm/finger, 50/sub
DNW 143.5 × 53.2 µm
area 7,634 µm²
AR 2.70
```

Current compiler choice is still a valid **area-first total-LDO** layout, but its DNW shape is tall (AR 0.38), not the balanced DNW shape.

## Artifacts

- [output-dnw-study.png](output-dnw-study.png)
- [output-dnw-study.json](output-dnw-study.json)
- [make_output_dnw_study.py](make_output_dnw_study.py)

## 6-DNW alternative (owner question)

The 5-DNW split was an assumption from the "1000 µm total W per ring" rule, not a
requirement. A 6-way split is valid and gives a much better DNW shape:

| option | split | W/finger | fingers/sub | array | sub-banks | DNW | DNW area | AR |
| --- | --- | ---: | ---: | --- | --- | --- | ---: | ---: |
| F | 6 equal active groups, 833.33 µm total W each | 24.51 | 34 | 1×34 | 3×2 | 76.48×99.33 | 7,597 | 0.77 |
| G | 5 active ×1000 + 1 dummy ×1000 | 25.00 | 40 | 1×40 | 3×2 | 86.80×100.80 | 8,749 | 0.86 |

F keeps total active W = 5000. G adds a full 1000 µm dummy group; it is **not**
free: DNW area rises from 7,597 to 8,749 (+15%).

Recommendation:

```text
F: six equal active sub-banks, no full dummy group.
```

If edge/dummy protection is needed, add dummy fingers at the sub-bank edges
rather than a whole 1000 µm dummy DNW group.
