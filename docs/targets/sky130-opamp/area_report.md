# Area report — opamp

> Early planning estimate using **generic-180** (educational); owner: **analog design engineer**. Approval: example only; the analog design owner must approve any production rule pack. Not a signoff area.

## Summary

| Metric | Value |
| --- | ---: |
| Devices | 11 (10 MOS, 1 cap) |
| Functional groups | 7 |
| Device core (OD/cap) | 2048 µm² |
| Active area (+ guard ring + device routing) | 2296 µm² |
| Matched area (+ dummy + matching overhead) | 2364 µm² |
| Block area (+ periphery + block routing) | **3526 µm²** |
| PEX-fix reserve | 282 µm² |
| Total envelope (block + reserve) | 3809 µm² |
| Dummy area | 59 µm² |
| Estimate range | 2821 µm² – 4761 µm² |
| Area gate | **PASS** (budget 6000 µm²) |
| Width convention | `per_finger` |

**Area hierarchy:** device core (OD/cap only) < active (+ring/routing) < matched (+dummy/matching) < block (+periphery) < envelope (+reserve). Fractions below are relative to the block area.

### Breakdown

| Bucket | Area | Share of block |
| --- | ---: | ---: |
| Device core | 2048 µm² | 58.1% |
| Guard ring | 33 µm² | 0.9% |
| Device routing | 215 µm² | 6.1% |
| Dummy | 59 µm² | 1.7% |
| Matching overhead | 9 µm² | 0.2% |
| Periphery + block routing | 1163 µm² | 33.0% |
| PEX-fix reserve | 282 µm² | 8.0% |

### Annotation provenance

| Source | Devices |
| --- | ---: |
| Name (primary source) | 11 |
| Explicit `role=` override | 0 |
| Other / invalid | 0 |
| Unknown role | 0 |

## Area by role

| Role | Area | Share of device area |
| --- | ---: | ---: |
| 补偿电容 (`compensation`) | 2200 µm² | 95.8% |
| 输出级 (`output_stage`) | 39 µm² | 1.7% |
| 差分输入对 (`input_pair`) | 20 µm² | 0.9% |
| 电流镜 (`current_mirror`) | 20 µm² | 0.9% |
| 尾电流源 (`tail_current`) | 10 µm² | 0.4% |
| 使能管 (`enable_switch`) | 6 µm² | 0.3% |
| 偏置 (`bias`) | 2 µm² | 0.1% |

## Groups

| Group | Role | Devices | Dummies | Area (with overhead) |
| --- | --- | ---: | ---: | ---: |
| `CC` | compensation | 1 | 0 | 2200 µm² |
| `DP` | input_pair | 2 | 2 | 44 µm² |
| `CM` | current_mirror | 2 | 2 | 42 µm² |
| `OUT` | output_stage | 2 | 0 | 39 µm² |
| `TAIL` | tail_current | 1 | 2 | 31 µm² |
| `EN` | enable_switch | 2 | 0 | 6 µm² |
| `BIAS` | bias | 1 | 0 | 2 µm² |

## Devices

| Device | Role | Group | W/L (µm) | nf×m | Total W (µm) | Layout (µm) | Area |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `M1_DP` | input_pair | `DP` | 0.75/0.5 | 1×1 | 0.75 | 1.3 × 1.2 | 10 µm² |
| `M2_DP` | input_pair | `DP` | 0.75/0.5 | 1×1 | 0.75 | 1.3 × 1.2 | 10 µm² |
| `M3_CM` | current_mirror | `CM` | 0.75/0.5 | 1×1 | 0.75 | 1.3 × 1.2 | 10 µm² |
| `M4_CM` | current_mirror | `CM` | 0.75/0.5 | 1×1 | 0.75 | 1.3 × 1.2 | 10 µm² |
| `M5_TAIL` | tail_current | `TAIL` | 0.75/0.5 | 1×1 | 0.75 | 1.3 × 1.2 | 10 µm² |
| `M6_OUT` | output_stage | `OUT` | 8.5/0.5 | 2×1 | 17 | 2.6 × 9.0 | 28 µm² |
| `M7_OUT` | output_stage | `OUT` | 6.5/0.5 | 1×1 | 6.5 | 1.3 × 7.0 | 11 µm² |
| `M8_BIAS` | bias | `BIAS` | 0.75/0.5 | 1×1 | 0.75 | 1.3 × 1.2 | 2 µm² |
| `M9_EN` | enable_switch | `EN` | 2/0.5 | 1×1 | 2 | 1.3 × 2.5 | 4 µm² |
| `M10_EN_PD` | enable_switch | `EN` | 1/0.5 | 1×1 | 1 | 1.3 × 1.5 | 2 µm² |
| `C1_CC` | compensation | `CC` | — | — | — | 54.8 × 36.5 | 2200 µm² |

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
