# Area report — two_stage

> Early planning estimate using **generic-180** (educational); owner: **analog design engineer**. Approval: example only; the analog design owner must approve any production rule pack. Not a signoff area.

## Summary

| Metric | Value |
| --- | ---: |
| Devices | 10 (9 MOS, 1 cap) |
| Functional groups | 7 |
| Device core (OD/cap) | 1159 µm² |
| Active area (+ guard ring + device routing) | 1432 µm² |
| Matched area (+ dummy + matching overhead) | 1972 µm² |
| Block area (+ periphery + block routing) | **3021 µm²** |
| PEX-fix reserve | 242 µm² |
| Total envelope (block + reserve) | 3263 µm² |
| Dummy area | 457 µm² |
| Estimate range | 2417 µm² – 4079 µm² |
| Area gate | **PASS** (budget 5000 µm²) |
| Width convention | `per_finger` |

**Area hierarchy:** device core (OD/cap only) < active (+ring/routing) < matched (+dummy/matching) < block (+periphery) < envelope (+reserve). Fractions below are relative to the block area.

### Breakdown

| Bucket | Area | Share of block |
| --- | ---: | ---: |
| Device core | 1159 µm² | 38.4% |
| Guard ring | 105 µm² | 3.5% |
| Device routing | 168 µm² | 5.5% |
| Dummy | 457 µm² | 15.1% |
| Matching overhead | 84 µm² | 2.8% |
| Periphery + block routing | 1049 µm² | 34.7% |
| PEX-fix reserve | 242 µm² | 8.0% |

### Annotation provenance

| Source | Devices |
| --- | ---: |
| Name (primary source) | 0 |
| Explicit `role=` override | 10 |
| Other / invalid | 0 |
| Unknown role | 0 |

## Area by role

| Role | Area | Share of device area |
| --- | ---: | ---: |
| 补偿电容 (`compensation`) | 825 µm² | 57.6% |
| 输出级 (`output_stage`) | 271 µm² | 18.9% |
| 尾电流源 (`tail_current`) | 127 µm² | 8.9% |
| 差分输入对 (`input_pair`) | 115 µm² | 8.1% |
| 电流镜 (`current_mirror`) | 88 µm² | 6.1% |
| 使能管 (`enable_switch`) | 4 µm² | 0.3% |
| 配置/Trim 开关 (`adj_switch`) | 2 µm² | 0.2% |

## Groups

| Group | Role | Devices | Dummies | Area (with overhead) |
| --- | --- | ---: | ---: | ---: |
| `COMP` | compensation | 1 | 0 | 825 µm² |
| `TAIL` | tail_current | 1 | 2 | 426 µm² |
| `OUT` | output_stage | 2 | 0 | 271 µm² |
| `DP` | input_pair | 2 | 2 | 258 µm² |
| `CM` | current_mirror | 2 | 2 | 186 µm² |
| `EN` | enable_switch | 1 | 0 | 4 µm² |
| `ADJ` | adj_switch | 1 | 0 | 2 µm² |

## Devices

| Device | Role | Group | W/L (µm) | nf×m | Total W (µm) | Layout (µm) | Area |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `M1` | input_pair | `IN` | 5/0.5 | 4×1 | 20 | 5.3 × 5.5 | 58 µm² |
| `M2` | input_pair | `IN` | 5/0.5 | 4×1 | 20 | 5.3 × 5.5 | 58 µm² |
| `M3` | current_mirror | `LOAD` | 5/1 | 2×1 | 10 | 3.6 × 5.5 | 44 µm² |
| `M4` | current_mirror | `LOAD` | 5/1 | 2×1 | 10 | 3.6 × 5.5 | 44 µm² |
| `M5` | tail_current | `BIAS` | 10/1 | 4×1 | 40 | 7.3 × 10.5 | 127 µm² |
| `M6` | output_stage | `OUT` | 10/1 | 4×1 | 40 | 7.3 × 10.5 | 90 µm² |
| `M7` | output_stage | `OUT` | 10/1 | 8×1 | 80 | 14.6 × 10.5 | 180 µm² |
| `M8` | enable_switch | `EN` | 2/0.5 | 1×1 | 2 | 1.3 × 2.5 | 4 µm² |
| `M9` | adj_switch | `ADJ` | 1/0.5 | 1×1 | 1 | 1.3 × 1.5 | 2 µm² |
| `C1` | compensation | `COMP` | — | — | — | 33.5 × 22.4 | 825 µm² |

## Warnings

- match group 'TAIL' has only one device; matching assumptions are weak

## Model notes

- Early planning estimate, not a signoff area.
- Area hierarchy: core < active < matched < block < envelope.
- Estimate range is 0.80x to 1.35x the nominal block area.
- 8% of the nominal block area is reported separately as PEX-fix reserve.
- Role taxonomy and rule values are owned by the analog design engineer; AI proposals need owner review.
- MOS area = OD footprint (fingers × pitch × finger height) + guard ring + routing overhead.
- Capacitor area = C / density; the generic density is a placeholder, not a PDK value.
- Block area adds a periphery and a global routing factor around the sum of group areas.
