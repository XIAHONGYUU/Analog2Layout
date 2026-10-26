# Low-voltage class-AB CMOS op-amp — review target

A real transistor-level schematic + netlist for role-map review. This one has an
upstream **schematic image**, unlike the LDO.

## Source

- Upstream:
  [Amirhossein7717/low-voltage-cmos-opamp](https://github.com/Amirhossein7717/low-voltage-cmos-opamp)
- Design: two-stage class-AB CMOS op-amp, 2 V supply, 0.8 µm Level=1 models
- License: MIT (see `LICENSE`)
- Original netlist: `src/AHLowVoltageOpAmp.net`
- Original schematic: [`schematic.png`](schematic.png)

## Why this review target

- **16 MOS**: larger than the 10-MOS Miller OP, smaller than the 41-MOS LDO.
- Real **class-AB output stage** (`M13/M14`), bias (`M15/M16`), input pair
  (`M1/M2`), PMOS current sources, NMOS mirror.
- Has an actual schematic image, so the user can judge the role map.
- No enable / no feedback divider / no level shifters; this is a focused
  role-map review target, not the final LDO.

## Current netlist

- 16 MOS + 1 compensation cap (`C1_CC = 5 pF`).
- `I_BIAS = 100 µA`, `R1 = 3.33 kΩ`; both currently ignored by the parser.
- External `CL = 10 pF` is documented but not in the core netlist.

```bash
python3 -m a2l analyze examples/classab_opamp/opamp.sp
```

## Second-stage structure

See [structure.md](structure.md) for a node-by-node explanation of
M6/M7/M8/M9/M10/M11/M12/M13/M14/R1/Cc, including the R1-vs-README discrepancy.
See [textbook.md](textbook.md) for the Allen & Holberg class-AB / floating-current-source
explanation and how it maps to this netlist.

## What to judge

- Which devices belong to `input_pair`, `current_mirror`, `output_stage`,
  `bias`, `compensation`?
- Are `M3/M4` current sources or part of a mirror?
- Are `M11/M12/M13` a cascode/output driver group?
- Which groups need match/dummy/ring?
