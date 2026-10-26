# SKY130 op-amp snapshot

Snapshot from the target run on 2026-10-26. It is a **generic-180 educational**
estimate, not a SKY130 signoff result.

```bash
python3 -m a2l build examples/sky130_two_stage_opamp/opamp.sp \
  --out out/sky130_opamp --area-budget-mm2 0.006 --fail-on-gate
```

- 11 devices (10 MOS, 1 cap), 7 groups
- block 2815 µm², envelope 3041 µm², gate PASS @ 6000 µm²
- 6 proposed dummies, 11 proposed deltas
- reserve shortfall: 1178 µm² (proposed deltas exceed reserve)
- [`white-line.svg`](white-line.svg) / [`white-line.png`](white-line.png): v0.3
  strict-scale white-line layout sketch (dummies, separate rings, MOSCAP)
- [`white-line-detail.png`](white-line-detail.png): cropped layout-plan detail
- [`make_white_line_layout.py`](make_white_line_layout.py): editable generator

Files are copied from `out/sky130_opamp/` for documentation; regenerate them
with the command above.
