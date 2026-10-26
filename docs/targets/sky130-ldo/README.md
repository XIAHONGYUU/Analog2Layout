# SKY130 1.8V LDO snapshot

Snapshot from the LDO role-proposal run on 2026-10-26. **Educational generic-180**
estimate, not a SKY130 signoff.

```bash
python3 -m a2l build examples/sky130_ldo_01v8/ldo.annotated.sp \
  --out out/sky130_ldo --area-budget-mm2 0.03 --fail-on-gate
```

- 41 MOS, 14 groups
- role proposal: 41 explicit overrides (agent-proposed, not analog-approved)
- block 14649 µm², envelope 15820 µm², gate PASS @ 30000 µm²
- output_stage (pass FET `XM61`) = 83.4% of device area
- floorplan is wide (605.6 µm) because 14 groups are still packed into 3 bands;
  power-device folding reduced the pass FET from 1320 µm to ~94 µm per row.

Files are copied from `out/sky130_ldo/`; regenerate with the command above.
