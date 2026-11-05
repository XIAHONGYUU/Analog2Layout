# Passive bank structures — resistor / MIM

Status: **structure-level drawings**, not GDS/DRC/LVS.

DNW1 assembly remains paused.

## Resistors — one common well

XR4/XR5/XR6 are **not three separate rings**. They share one passive well/ring:

```text
XR5 / XR4 / XR6 in one compact stepped common well.

Compact geometry:

```text
bbox 40 × 17 µm
no rectangular fill in the right-bottom corner
XR6 sits under XR4; XR5 occupies the left full-height column
```

Dummy placement:

```text
one 10×0.35 dummy strip above and below each active column
XR5: 2 columns → 4 dummies
XR4: 2 columns → 4 dummies
XR6: 1 column  → 2 dummies
total: 10 dummy segments
```

Dummy strips run along the long edge, same horizontal orientation, and are
inside the common well.

AA/tap is a perimeter band only; the resistor and dummy body are over field,
not AA. Resistor head/contact intent is shown as violet end bars and black
contacts.

Still not checked: dummy-to-ring spacing, head/contact DRC, full AA/tap DRC.
The stepped perimeter is a layout-intent outline, not a DRC-clean polygon.

Actual active arrays:

```text
XR4: 18 active / 2 cols = 9 rows
XR5: 36 active / 2 cols = 18 rows
XR6: 4 active / 1 col = 4 rows
```

The earlier 20×10.55 / 20×20.75 / 10×7.15 footprints included unused
row/column cells; those are not required by the resistor and are now removed.
```

The individual `XR4/XR5/XR6` drawings below are retained as resistor-array
references; the actual passive macro is `XR_GROUP`.

| macro | active / dummy | footprint | outer | segment | fold |
| --- | --- | --- | --- | --- | --- |
| `XR4` | 18 / 2 | 20 × 10.55 | 23.60 × 14.15 | 10 × 0.35, gap 0.5 | 13×2 |
| `XR5` | 36 / 2 | 20 × 20.75 | 23.60 × 24.35 | 10 × 0.35, gap 0.5 | 25×2 |
| `XR6` | 4 / 2 | 10 × 7.15 | 13.60 × 10.75 | 10 × 0.35, gap 0.5 | 9×1 |

Current drawing:

- yellow = active resistor segment;
- gray `DM` = one end dummy at each end of the chain (2 total);
- ring 1.0 / 0.8;
- no resistor-end metal, vias, or connections.

The 0.5 µm segment gap remains a layout choice; it is not a PDK value.
`poly.9` is 0.48 µm for resistor poly to other poly or diff/tap. Full resistor
head/contact geometry is not yet checked.

## MIM capacitors

| macro | footprint | outer | units | assumption |
| --- | --- | --- | ---: | --- |
| `XC1` | 15 × 15 | 18.60 × 18.60 | 3 | three 15×5 plate units stacked; **needs owner confirmation** |
| `XC3` | 5 × 5 | 8.60 × 8.60 | 1 | single 5×5 plate |

Current drawing:

- violet = MIM plates;
- black = plate contact/via intent;
- ring 1.0 / 0.8;
- no terminal metal.

MIM plate/contact DRC rules have not yet been checked. The XC1 unit split is an
assumption until the owner confirms it.

## Artifacts

- `XR_GROUP.svg/png` (common well)
- `XR4.svg/png`, `XR5.svg/png`, `XR6.svg/png` (individual array references)
- `XC1.svg/png`, `XC3.svg/png`
- `passive-library.png`
- `passive-group-library-v20261105-1512.png`
- `passive-banks.json`
