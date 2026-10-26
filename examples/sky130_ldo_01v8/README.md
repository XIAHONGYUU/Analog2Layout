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

## Why this is a better target

- **41 MOS** plus one power pass device with `m=1000` (`XM61`);
- real feedback divider (`XR4/XR5`), bias resistor (`XR6`), MIM caps (`XC1/XC3`);
- enable, startup, bias generation, reference select, external-reference select;
- two level-shifter subcircuits (`x1/x2`);
- 5 V devices, 1.8 V devices, power stage, feedback loop: much more representative
  than a 10-MOS two-stage OP.

## Current parser result

```text
Devices: 41 (41 MOS, 0 cap) in 41 groups
Role sources: name 0, explicit 0, unknown 41
Block: 12203 µm² (undercount: R, MIM C, X subcircuits ignored)
```

This exposes the real problem: the netlist uses `XM46`, `XM52`, ... — names do
not carry semantic roles. A normal netlist needs a role map or topology-based
proposal before area/floorplan/white-line can be trusted.

## Run

```bash
python3 -m a2l analyze examples/sky130_ldo_01v8/ldo.sp
python3 -m a2l validate examples/sky130_ldo_01v8/ldo.sp
```

## Known gaps

- `XR*` resistors ignored;
- `XC*` MIM capacitors ignored;
- `x1/x2` level shifters ignored;
- role taxonomy has no `pass_device` (could map to `output_stage` or add a new role
  with analog-owner approval);
- all 41 MOS currently `unknown`.
