# SKY130 1.8 V LDO — candidate real target

A real, flat, transistor-level LDO from the Efabless/CHIPALOOZA open-source IP
family. This is a **candidate** for the next main target; the small OP remains a
unit test.

## Source

- Upstream:
  [fossi-foundation/sky130_am_ip__ldo_01v8](https://github.com/fossi-foundation/sky130_am_ip__ldo_01v8)
- Original: `sky130_am_ip__ldo_01v8`, low-power 1.8 V LDO
- License: Apache-2.0 (see `LICENSE`)
- Netlist copied from `netlist/schematic/sky130_am_ip__ldo_01v8.spice`

## Schematic view

![Reconstructed LDO block schematic](../../docs/targets/sky130-ldo/schematic.png)

Upstream has no PNG screenshot; it has an xschem `.sch`. This block schematic is
reconstructed from the block labels + netlist for role-map review, not a
transistor-level screenshot.

## Why this is a better target

- **41 MOS** plus one power pass device with `m=1000` (`XM61`);
- real feedback divider (`XR4/XR5`), bias resistor (`XR6`), MIM caps (`XC1/XC3`);
- enable, startup, bias generation, reference select, external-reference select;
- two level-shifter subcircuits (`x1/x2`);
- 5 V devices, 1.8 V devices, power stage, feedback loop: much more representative
  than a 10-MOS two-stage OP.

## Current parser result

Raw netlist:

```text
Devices: 41 (41 MOS, 0 cap) in 41 groups
Role sources: name 0, explicit 0, unknown 41
Block: 12203 µm² (undercount: R, MIM C, X subcircuits ignored)
```

Agent role proposal: [`ldo.annotated.sp`](ldo.annotated.sp)

```text
Devices: 41 (41 MOS, 0 cap) in 14 groups
Role sources: explicit 41, unknown 0
Block: 14649 µm²
Gate: PASS @ 30000 µm²
Pass FET XM61: 83.4% of device area
```

The role map is **proposed by the agent from topology**, not approved by the
analog owner. `pass_device` is mapped to `output_stage` for now.

## Run

```bash
python3 -m a2l analyze examples/sky130_ldo_01v8/ldo.annotated.sp
python3 -m a2l validate examples/sky130_ldo_01v8/ldo.annotated.sp --require-known-roles
python3 -m a2l build examples/sky130_ldo_01v8/ldo.annotated.sp --out out/sky130_ldo --area-budget-mm2 0.03 --fail-on-gate
```

## Known gaps

- `XR*` resistors ignored;
- `XC*` MIM capacitors ignored;
- `x1/x2` level shifters ignored;
- role taxonomy has no `pass_device` (could map to `output_stage` or add a new role
  with analog-owner approval);
- raw netlist: all 41 MOS `unknown`; annotated proposal: 41 explicit, still needs analog review.
