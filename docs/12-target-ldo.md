# Candidate target: SKY130 1.8 V LDO

## Why replace the 10-MOS OP

The two-stage Miller OP is useful as a unit test, but it is too small to show the
agent's advantage:

- only 10 MOS;
- `C1_CC = 3 pF` at 2 fF/µm² is 1500 µm², which dominates a 10-MOS circuit and
  looks unreasonable for this topology;
- no power stage, no feedback divider, no startup, no level shifters, no
  hierarchy.

## Candidate

- IP: `sky130_am_ip__ldo_01v8`
- Source:
  [fossi-foundation/sky130_am_ip__ldo_01v8](https://github.com/fossi-foundation/sky130_am_ip__ldo_01v8)
- License: Apache-2.0
- Local copy: [`examples/sky130_ldo_01v8/ldo.sp`](../examples/sky130_ldo_01v8/ldo.sp)
- Local license: [`examples/sky130_ldo_01v8/LICENSE`](../examples/sky130_ldo_01v8/LICENSE)

## Size / content

| Item | Value |
| --- | --- |
| MOS devices | 41 |
| Power pass device | `XM61`, `m=1000` |
| Feedback divider | `XR4/XR5` |
| Bias resistor | `XR6` |
| MIM caps | `XC1/XC3` |
| Enable / startup | `XM83–XM90`, `XM70–XM74` |
| Reference select | `XM75–XM78` |
| Level shifters | `x1/x2` |

## What it exposes

1. **Real netlist names are generic** (`XM46`, `XM52`, ...), so name-only role
   inference gives 41 unknowns. The agent must propose roles from topology and a
   human-approved annotation layer.
2. **Parser gaps**: `XR*`, `XC*`, and `x*` subcircuits are ignored; area is
   undercounted and no LDO-specific roles exist.
3. **Power stage**: the pass FET is a real power device; floorplan/white-line
   must handle current density, wide metal, ESD, and feedback routing.
4. **Control/analog mix**: enable, startup, reference select, level shifters —
   good test for role grouping and module boundaries.

## Current run

```text
Devices:  41 (41 MOS, 0 cap) in 41 groups
Unknown:  41
Block:    12203 µm² (undercount; R/C/X ignored)
```

## Decision needed

- Make LDO the new primary target, with OP as a unit test?
- Should the agent propose the LDO role map from topology, or will analog provide
  the `role=` overlay?
- Do we add `pass_device`, `feedback_divider`, `level_shift` roles, or map them to
  existing `output_stage` / `bias` / `adj_switch`?

## Why this matters

A real target with 41 MOS, power stage, feedback, enable, startup, and hierarchy
is a much better test of the agent than a 10-MOS OP. It also shows where the agent
must stop guessing and ask the analog owner for a role map.
