# Rule packs

A rule pack is a **versioned JSON file** that turns a role-annotated netlist
into an area/floorplan estimate. It is deliberately separate from the code so a
company can keep its real values private and swap them in without forking the
project.

## Bundled pack

`generic_180.json` is an **educational** pack:

- 180 nm-ish numbers;
- no foundry PDK data;
- no company-specific matching/isolation rules;
- suitable for demos and relative comparisons only.

Do not use it for signoff or tape-out decisions.

## Minimal pack

```json
{
  "schema_version": "0.1",
  "name": "my-company-28nm",
  "description": "Desensitized internal rule pack",
  "confidence": "calibrated",
  "owner": "analog design engineer",
  "approval": "approved by <name/team> on <date>; sample count: N",
  "width_convention": "per_finger",
  "mos": {
    "min_l_um": 0.03,
    "max_w_per_finger_um": 8.0,
    "sd_ext_um": 0.12,
    "od_ext_um": 0.10,
    "contact_spacing_um": 0.08,
    "routing_overhead": 0.22,
    "guard_ring_width_um": 0.35
  },
  "matching": {
    "dummy_per_group": 2,
    "dummy_width_factor": 1.0,
    "common_centroid_overhead": 0.15,
    "matching_overhead": 0.08,
    "group_spacing_um": 2.0,
    "band_spacing_um": 4.0,
    "guard_ring_for_critical": true
  },
  "cap": {
    "density_ff_per_um2": 2.0,
    "routing_overhead": 0.12,
    "aspect_ratio": 1.5
  },
  "block": {
    "periphery_um": 3.0,
    "routing_overhead": 0.12,
    "reserve_fraction": 0.10,
    "decap_min_pf": 1.0,
    "decap_ratio_to_comp": 0.5,
    "decap_max_pf": 20.0
  },
  "estimate": {
    "low_factor": 0.85,
    "high_factor": 1.25
  },
  "layout_delta": {
    "boundary_dummies_per_critical_group": 2,
    "dummy_logic_for_switches": 1,
    "guard_ring_for_input_pair": true,
    "max_current_density_ma_per_um": 1.0,
    "reserve_fraction": 0.10
  }
}
```

## Conventions

### Width

`width_convention` must be one of:

- `per_finger` (default): SPICE `w` is one finger; `W_total = w × nf × m`.
- `total`: `w` already includes all fingers; `W_total = w × m`.

This is the most common source of 2×–8× area errors. State it explicitly.

### Units

- lengths: µm
- area: µm²
- capacitance: pF
- cap density: fF/µm²

### Ownership

`owner` and `approval` are mandatory in a company pack. The role taxonomy and
the rule values are the analog design team's responsibility; an AI/agent may
propose a change but cannot approve it.

### Confidence

- `educational`: demo only.
- `estimated`: based on engineering judgment, not calibrated.
- `calibrated`: fitted against completed layouts; record sample count and date.

The pack should include a `description` with the process node, source, date, and
sample count, without disclosing confidential details.

## Creating a company pack

1. Copy `generic_180.json` to a private location (do not commit it).
2. Replace `name`, `description`, `confidence`.
3. Set `width_convention` to match the schematic export.
4. Fill in `mos`, `matching`, `cap`, `block` from the company rule deck and
   historical layouts.
5. Run `a2l analyze` on 10–30 completed blocks; compare estimated vs actual.
6. Adjust `routing_overhead`, `periphery_um`, `common_centroid_overhead`.
7. Record the calibration method and error range in `description`.
8. Validate the pack in CI with a small set of golden netlists.

## What not to put in a public pack

- foundry PDK parameters;
- company rule IDs and decks;
- real schematics, layouts, or PEX reports;
- customer names / product names that are not public.

The public repo should only contain the schema, the generic pack, and
desensitized examples.
