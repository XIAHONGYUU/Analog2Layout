# LDO bank plan — bank-first freeze

Status: **draft geometry freeze**; no global placement/routing yet.

Global rule: DNW1 poly orientation is **vertical**; no individual bank
rotation is allowed. Ports and S/D connections remain pending.

## MOS banks

| bank | type | members | m | array | L | dummy | core µm | outer µm | status |
| --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| `PMOS_1X7_BANK` | PMOS | XM46, XM56, XM60, XM62, XM64, XM79 | 1 | 6×1 | 7 | 2 side(s), L=0.5 | 9.08×9.60 | 11.68×12.20 | draft_frozen_geometry |
| `NMOS_1X7_BANK` | NMOS | XM48, XM55 | 1 | 2×1 | 7 | 2 side(s), L=0.5 | 9.08×3.20 | 11.68×5.80 | draft_frozen_geometry |
| `NMOS_2X0.5_BANK` | NMOS | XM52, XM53 | 1 | 1×2 | 0.5 | 2 side(s), L=0.5 | 3.44×2.60 | 6.04×5.20 | draft_frozen_geometry |
| `NMOS_3X9_BANK` | NMOS | XM54 | 1 | 1×1 | 9 | 2 side(s), L=0.5 | 11.08×3.60 | 13.68×6.20 | draft_frozen_geometry |
| `PMOS_1X0.5_BANK` | PMOS | XM57, XM58, XM59, XM63, XM65, XM86, XM88, XM90 | 1 | 1×8 | 0.5 | 0 side(s), L=None | 6.88×1.60 | 9.48×4.20 | draft_frozen_geometry |
| `NMOS_1X9_BANK` | NMOS | XM66, XM67, XM69, XM74 | 5,20 | 18×2 | 9 | 2 side(s), L=0.5 | 20.44×28.80 | 23.04×31.40 | draft_frozen_geometry |
| `PMOS_1X10_BANK` | PMOS | XM68 | 1 | 1×1 | 10 | 2 side(s), L=0.5 | 12.08×1.60 | 14.68×4.20 | draft_frozen_geometry |
| `NMOS_1X0.5_BANK` | NMOS | XM70, XM75, XM77, XM78, XM83, XM85, XM87, XM89 | 1 | 2×4 | 0.5 | 0 side(s), L=None | 3.44×3.20 | 6.04×5.80 | draft_frozen_geometry |
| `PMOS_1X2_BANK` | PMOS | XM71, XM72, XM73 | 1 | 3×1 | 2 | 2 side(s), L=0.5 | 4.08×4.80 | 6.68×7.40 | draft_frozen_geometry |
| `PMOS_2.5X0.5_BANK` | PMOS | XM76, XM84 | 1 | 1×2 | 0.5 | 0 side(s), L=None | 1.72×3.10 | 4.32×5.70 | draft_frozen_geometry |
| `NMOS_1X10_BANK` | NMOS | XM80, XM81, XM82 | 1 | 3×1 | 10 | 2 side(s), L=0.5 | 12.08×4.80 | 14.68×7.40 | draft_frozen_geometry |

## Output bank

- `PASS_XM61`: 6 sub-banks × 34 fingers; W=24.51 µm; arrangement [3, 2]; body ring 2.0/2.0 shared; DNW2 76.48×99.33; no edge dummy.

## Passive / blackbox macros

| macro | kind | core/outer µm | status |
| --- | --- | --- | --- |
| `XR4` | passive | 20×10.55 / 23.60×14.15 | draft_frozen_geometry |
| `XR5` | passive | 20×20.75 / 23.60×24.35 | draft_frozen_geometry |
| `XC1` | passive | 15×15 / 18.60×18.60 | draft_frozen_geometry |
| `XC3` | passive | 5×5 / 8.60×8.60 | draft_frozen_geometry |
| `XR6` | passive | 10×7.15 / 13.60×10.75 | draft_frozen_geometry |
| `x1` | blackbox | — / 5.00×5.00 | placeholder |
| `x2` | blackbox | — / 5.00×5.00 | placeholder |

## Freeze checklist

- [x] members / m / nf
- [x] bank array rows×cols
- [x] dummy policy and L
- [x] ring dimensions
- [x] core / outer footprint
- [x] poly orientation vertical
- [ ] port-side assignment
- [ ] S/D topology
- [ ] global placement (later)

This file is a geometry contract for the next assembly stage, not a release.
`bank-specs.json` is the machine-readable source.
