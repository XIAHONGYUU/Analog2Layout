# Low-voltage class-A CMOS op-amp — corrected review target

A real transistor-level schematic + netlist for role-map review.

> **Correction:** the upstream README calls this a class-AB design, but the
> netlist is **class A**: M13's gate is a bias node, only M14's gate is
> signal-driven. M13 is a PMOS current-source load, not a push-pull output device.
> The folder was renamed from `classab_opamp` to `classa_opamp`.

## Source

- Upstream:
  [Amirhossein7717/low-voltage-cmos-opamp](https://github.com/Amirhossein7717/low-voltage-cmos-opamp)
- Design: two-stage CMOS op-amp, 2 V supply, 0.8 µm Level=1 models
- License: MIT (see `LICENSE`)
- Original netlist: `src/AHLowVoltageOpAmp.net`
- Original schematic: [`schematic.png`](schematic.png)

## Annotated schematic

![Annotated class-A OP](schematic-annotated.png)

All dimensions are **W/L in µm**; every device has **L = 2 µm**.

| Device | W/L (µm) | Device | W/L (µm) |
| --- | ---: | --- | ---: |
| M1 | 80/2 | M2 | 80/2 |
| M3 | 64/2 | M4 | 64/2 |
| M5 | 162/2 | M6 | 240/2 |
| M7 | 240/2 | M8 | 109/2 |
| M9 | 109/2 | M10 | 194/2 |
| M11 | 240/2 | M12 | 240/2 |
| M13 | 640/2 | M14 | 1800/2 |
| M15 | 128/2 | M16 | 162/2 |

## What the netlist actually is

- **16 MOS** + one compensation cap (`C1_CC = 5 pF`);
- input pair `M1/M2`;
- PMOS current-source loads `M3/M4`;
- second stage `M6/M7` (PMOS common-gate) + `M8/M9` (NMOS mirror load);
- bias `M10/M15/M16`;
- `M11/M12/R1` form a **PMOS bias current source** that sets M13's gate `n003`;
- **M13 is a PMOS current-source load** (`gate n003 = bias`);
- **M14 is the only signal-driven output device** (`gate n012`);
- output stage is therefore **class A**, not class-AB push-pull.

The earlier explanation that called M13/M14 a class-AB push-pull pair was wrong.
The key check is simple: **M13's gate has no signal path**; it is tied to
`n003`, which is set by `M11/M12/R1`, not by `n012` or the first stage.

## Why this review target

- Has an actual schematic image and a netlist, so the user can judge the role map.
- 16 MOS is larger than the 10-MOS Miller OP, but still small enough to trace.
- Exposes a real documentation/verification issue: the upstream README's
  "class AB" label does not match the netlist.
- No enable / no feedback divider / no level shifters; focused role review.

## Current netlist

- 16 MOS + 1 compensation cap (`C1_CC = 5 pF`).
- `I_BIAS = 100 µA`, `R1 = 3.33 kΩ`; both currently ignored by the parser.
- External `CL = 10 pF` is documented but not in the core netlist.

```bash
python3 -m a2l analyze examples/classa_opamp/opamp.sp
```

## Documents

- [sizing.md](sizing.md): original W/L, m=1 check, and matching-group ratio analysis.

- [structure.md](structure.md): node-by-node explanation, corrected to class A.
- [textbook.md](textbook.md): what Allen & Holberg say about class AB, and why
  this circuit is not it.

## What to judge

- Which devices belong to `input_pair`, `current_mirror`, `output_stage`,
  `bias`, `compensation`?
- Is M13 `bias` / `current_mirror` rather than `output_stage`?
- Is M14 the only `output_stage` device?
- Which groups need match/dummy/ring?
