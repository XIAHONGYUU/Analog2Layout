# two_stage — reference example

A synthetic two-stage Miller OTA used to exercise all three handoff steps.

```bash
python3 -m a2l build examples/two_stage/two_stage.sp --out examples/two_stage/out --area-budget-mm2 0.005 --fail-on-gate
```

Expected summary (generic-180 rules):

| Metric | Value |
| --- | ---: |
| Devices | 10 (9 MOS + 1 cap) |
| Groups | 7 |
| Nominal block area | ≈ 3021 µm² |
| Range | ≈ 2417–4079 µm² |
| PEX-fix reserve | ≈ 242 µm² |
| Area gate @ 0.005 mm² | PASS (headroom ≈ 921 µm²) |
| Proposed deltas | 12 |

## What to look at

- `out/floorplan.svg` — input pair straddles the symmetry axis; mirror above;
  tail below; output/comp cap right; dummy/decap proposals and reserve visible.
- `out/HANDOFF.md` — layout-preserve list + proposed deltas + PEX re-sim scope.
- `out/area_report.md` — compensation cap dominates the device area, which is a
  useful early warning: a 1.5 pF cap is not free.

## Annotations

| Device | role | match | group | layout |
| --- | --- | --- | --- | --- |
| M1, M2 | input_pair | DP | IN | common_centroid |
| M3, M4 | current_mirror | CM | LOAD | interdigitated |
| M5 | tail_current | TAIL | BIAS | common_centroid |
| M6, M7 | output_stage | — | OUT | interdigitated |
| M8 | enable_switch | — | EN | minimal |
| M9 | adj_switch | — | ADJ | minimal |
| C1 | compensation | — | COMP | — |

> `w` is per-finger width: total W = `w × nf × m`.
