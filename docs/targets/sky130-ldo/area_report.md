# Area report — ldo.annotated

> Early planning estimate using **generic-180** (educational); owner: **analog design engineer**. Approval: example only; the analog design owner must approve any production rule pack. Not a signoff area.

## Summary

| Metric | Value |
| --- | ---: |
| Devices | 41 (41 MOS, 0 cap) |
| Functional groups | 14 |
| Device core (OD/cap) | 8028 µm² |
| Active area (+ guard ring + device routing) | 10278 µm² |
| Matched area (+ dummy + matching overhead) | 11534 µm² |
| Block area (+ periphery + block routing) | **14649 µm²** |
| PEX-fix reserve | 1172 µm² |
| Total envelope (block + reserve) | 15820 µm² |
| Dummy area | 1119 µm² |
| Estimate range | 11719 µm² – 19776 µm² |
| Area gate | **PASS** (budget 30000 µm²) |
| Width convention | `per_finger` |

**Area hierarchy:** device core (OD/cap only) < active (+ring/routing) < matched (+dummy/matching) < block (+periphery) < envelope (+reserve). Fractions below are relative to the block area.

### Breakdown

| Bucket | Area | Share of block |
| --- | ---: | ---: |
| Device core | 8028 µm² | 54.8% |
| Guard ring | 683 µm² | 4.7% |
| Device routing | 1568 µm² | 10.7% |
| Dummy | 1119 µm² | 7.6% |
| Matching overhead | 138 µm² | 0.9% |
| Periphery + block routing | 3114 µm² | 21.3% |
| PEX-fix reserve | 1172 µm² | 8.0% |

### Annotation provenance

| Source | Devices |
| --- | ---: |
| Name (primary source) | 0 |
| Explicit `role=` override | 41 |
| Other / invalid | 0 |
| Unknown role | 0 |

## Area by role

| Role | Area | Share of device area |
| --- | ---: | ---: |
| 输出级 (`output_stage`) | 8569 µm² | 83.4% |
| 电流镜 (`current_mirror`) | 1347 µm² | 13.1% |
| 偏置 (`bias`) | 189 µm² | 1.8% |
| 尾电流源 (`tail_current`) | 69 µm² | 0.7% |
| 共源共栅 (`cascode`) | 43 µm² | 0.4% |
| 差分输入对 (`input_pair`) | 28 µm² | 0.3% |
| 使能管 (`enable_switch`) | 21 µm² | 0.2% |
| 配置/Trim 开关 (`adj_switch`) | 12 µm² | 0.1% |

## Groups

| Group | Role | Devices | Dummies | Area (with overhead) |
| --- | --- | ---: | ---: | ---: |
| `PASS` | output_stage | 1 | 0 | 8567 µm² |
| `BIAS_N` | current_mirror | 2 | 2 | 1929 µm² |
| `BIAS` | current_mirror | 3 | 0 | 245 µm² |
| `BIAS_P` | current_mirror | 2 | 2 | 146 µm² |
| `LOAD` | current_mirror | 2 | 2 | 146 µm² |
| `START` | bias | 5 | 0 | 104 µm² |
| `REF` | current_mirror | 4 | 0 | 92 µm² |
| `ERR` | tail_current | 2 | 0 | 83 µm² |
| `ERR_DP` | input_pair | 2 | 2 | 63 µm² |
| `BIAS_C` | cascode | 2 | 2 | 45 µm² |
| `CAS` | cascode | 2 | 2 | 45 µm² |
| `PASS_DRV` | current_mirror | 2 | 0 | 37 µm² |
| `EN` | enable_switch | 8 | 0 | 21 µm² |
| `SEL` | adj_switch | 4 | 0 | 12 µm² |

## Devices

| Device | Role | Group | W/L (µm) | nf×m | Total W (µm) | Layout (µm) | Area |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `XM46` | current_mirror | `ERR` | 1/7 | 1×1 | 1 | 7.8 × 1.5 | 34 µm² |
| `XM48` | bias | `BIAS` | 1/7 | 1×1 | 1 | 7.8 × 1.5 | 14 µm² |
| `XM52` | input_pair | `ERR` | 2/0.5 | 1×1 | 2 | 1.3 × 2.5 | 14 µm² |
| `XM53` | input_pair | `ERR` | 2/0.5 | 1×1 | 2 | 1.3 × 2.5 | 14 µm² |
| `XM54` | tail_current | `ERR` | 3/9 | 1×1 | 3 | 9.8 × 3.5 | 69 µm² |
| `XM55` | bias | `ERR` | 1/7 | 1×1 | 1 | 7.8 × 1.5 | 14 µm² |
| `XM56` | current_mirror | `ERR` | 1/7 | 1×1 | 1 | 7.8 × 1.5 | 34 µm² |
| `XM57` | cascode | `ERR` | 1/0.5 | 1×1 | 1 | 1.3 × 1.5 | 11 µm² |
| `XM58` | cascode | `ERR` | 1/0.5 | 1×1 | 1 | 1.3 × 1.5 | 11 µm² |
| `XM59` | output_stage | `PASS_DRV` | 1/0.5 | 1×1 | 1 | 1.3 × 1.5 | 2 µm² |
| `XM60` | current_mirror | `PASS_DRV` | 1/7 | 1×1 | 1 | 7.8 × 1.5 | 34 µm² |
| `XM61` | output_stage | `PASS` | 5/0.5 | 1×1000 | 5000 | 1320.0 × 5.5 | 8567 µm² |
| `XM62` | current_mirror | `BIAS` | 1/7 | 1×1 | 1 | 7.8 × 1.5 | 34 µm² |
| `XM63` | cascode | `BIAS` | 1/0.5 | 1×1 | 1 | 1.3 × 1.5 | 11 µm² |
| `XM64` | current_mirror | `BIAS` | 1/7 | 1×1 | 1 | 7.8 × 1.5 | 34 µm² |
| `XM65` | cascode | `BIAS` | 1/0.5 | 1×1 | 1 | 1.3 × 1.5 | 11 µm² |
| `XM66` | current_mirror | `BIAS` | 1/9 | 1×20 | 20 | 196.4 × 1.5 | 724 µm² |
| `XM67` | current_mirror | `BIAS` | 1/9 | 1×5 | 5 | 49.1 × 1.5 | 185 µm² |
| `XM68` | current_mirror | `BIAS` | 1/10 | 1×1 | 1 | 10.8 × 1.5 | 45 µm² |
| `XM69` | current_mirror | `BIAS` | 1/9 | 1×5 | 5 | 49.1 × 1.5 | 185 µm² |
| `XM70` | bias | `START` | 1/0.5 | 1×1 | 1 | 1.3 × 1.5 | 2 µm² |
| `XM71` | bias | `START` | 1/2 | 1×1 | 1 | 2.8 × 1.5 | 5 µm² |
| `XM72` | bias | `START` | 1/2 | 1×1 | 1 | 2.8 × 1.5 | 5 µm² |
| `XM73` | bias | `START` | 1/2 | 1×1 | 1 | 2.8 × 1.5 | 5 µm² |
| `XM74` | bias | `START` | 1/9 | 1×5 | 5 | 49.1 × 1.5 | 87 µm² |
| `XM75` | adj_switch | `SEL` | 1/0.5 | 1×1 | 1 | 1.3 × 1.5 | 2 µm² |
| `XM76` | adj_switch | `SEL` | 2.5/0.5 | 1×1 | 2.5 | 1.3 × 3.0 | 5 µm² |
| `XM77` | adj_switch | `SEL` | 1/0.5 | 1×1 | 1 | 1.3 × 1.5 | 2 µm² |
| `XM78` | adj_switch | `SEL` | 1/0.5 | 1×1 | 1 | 1.3 × 1.5 | 2 µm² |
| `XM79` | current_mirror | `REF` | 1/7 | 1×1 | 1 | 7.8 × 1.5 | 34 µm² |
| `XM80` | bias | `REF` | 1/10 | 1×1 | 1 | 10.8 × 1.5 | 19 µm² |
| `XM81` | bias | `REF` | 1/10 | 1×1 | 1 | 10.8 × 1.5 | 19 µm² |
| `XM82` | bias | `REF` | 1/10 | 1×1 | 1 | 10.8 × 1.5 | 19 µm² |
| `XM83` | enable_switch | `EN` | 1/0.5 | 1×1 | 1 | 1.3 × 1.5 | 2 µm² |
| `XM84` | enable_switch | `EN` | 2.5/0.5 | 1×1 | 2.5 | 1.3 × 3.0 | 5 µm² |
| `XM85` | enable_switch | `EN` | 1/0.5 | 1×1 | 1 | 1.3 × 1.5 | 2 µm² |
| `XM86` | enable_switch | `EN` | 1/0.5 | 1×1 | 1 | 1.3 × 1.5 | 2 µm² |
| `XM87` | enable_switch | `EN` | 1/0.5 | 1×1 | 1 | 1.3 × 1.5 | 2 µm² |
| `XM88` | enable_switch | `EN` | 1/0.5 | 1×1 | 1 | 1.3 × 1.5 | 2 µm² |
| `XM89` | enable_switch | `EN` | 1/0.5 | 1×1 | 1 | 1.3 × 1.5 | 2 µm² |
| `XM90` | enable_switch | `EN` | 1/0.5 | 1×1 | 1 | 1.3 × 1.5 | 2 µm² |

## Warnings

- XM54: role tail_current needs a match group; add match= or give the instance a semantic name token
- XM60: role current_mirror needs a match group; add match= or give the instance a semantic name token
- XM68: role current_mirror needs a match group; add match= or give the instance a semantic name token
- XM69: role current_mirror needs a match group; add match= or give the instance a semantic name token
- XM79: role current_mirror needs a match group; add match= or give the instance a semantic name token

## Model notes

- Early planning estimate, not a signoff area.
- Area hierarchy: core < active < matched < block < envelope.
- Estimate range is 0.80x to 1.35x the nominal block area.
- 8% of the nominal block area is reported separately as PEX-fix reserve.
- Role taxonomy and rule values are owned by the analog design engineer; AI proposals need owner review.
- MOS area = OD footprint (fingers × pitch × finger height) + guard ring + routing overhead.
- Capacitor area = C / density; the generic density is a placeholder, not a PDK value.
- Block area adds a periphery and a global routing factor around the sum of group areas.
