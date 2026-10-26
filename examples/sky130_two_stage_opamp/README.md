# SKY130 two-stage Miller op-amp

A **name-only** transistor-level netlist for the first real target of
Analog2Layout. It is derived from an open-source SKY130 design and extended with
a real bias/enable branch.

## Source

- Base topology and device sizes:
  [chennakeshavadasa/Miller-Compensated-Two-stage-OPAMP-using-SKY130PDK](https://github.com/chennakeshavadasa/Miller-Compensated-Two-stage-OPAMP-using-SKY130PDK)
- License: MIT, Copyright (c) 2024 Nithin P
- The original is a 7-transistor two-stage Miller op-amp with an ideal 30 µA bias
  source.

## What changed

This demo keeps the 7-transistor core and adds:

| Device | Purpose |
| --- | --- |
| `M8_BIAS` | diode-connected NMOS in the bias mirror |
| `M9_EN` | NMOS enable switch in the bias branch |
| `M10_EN_PD` | PMOS pull-up that forces the bias node off when `EN=0` |

`I0 = 30 µA` is still ideal so the netlist stays small and readable. A production
version would replace it with a real bias generator.

## Why this target

- It is a **classic two-stage Miller op-amp**, not a synthetic arbitrary circuit.
- It has **real MOS devices** with W/L and a real compensation capacitor.
- The 10 pF load capacitor from the original testbench is documented but kept out
  of the core netlist, because it is not on-die area.
- It adds **enable and bias auxiliary devices**, so the demo can exercise
  `enable_switch`, `bias`, `current_mirror`, `input_pair`, `output_stage`, and
  `compensation` together.
- It is **name-only**, matching real simulation/verification netlists.

## Run

```bash
python3 -m a2l analyze examples/sky130_two_stage_opamp/opamp.sp
python3 -m a2l validate examples/sky130_two_stage_opamp/opamp.sp --require-known-roles
python3 -m a2l build examples/sky130_two_stage_opamp/opamp.sp --out out/sky130_opamp
```

## Expected name inference

| Name | Role | Match/group |
| --- | --- | --- |
| `M1_DP`, `M2_DP` | `input_pair` | `DP` |
| `M3_CM`, `M4_CM` | `current_mirror` | `CM` |
| `M5_TAIL` | `tail_current` | `TAIL` |
| `M6_OUT`, `M7_OUT` | `output_stage` | `OUT` |
| `M8_BIAS` | `bias` | `BIAS` |
| `M9_EN`, `M10_EN_PD` | `enable_switch` | `EN` |
| `C1_CC` | `compensation` | `CC` |
