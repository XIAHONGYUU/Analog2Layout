# Bank and passive detail review — DNW1 on hold

Status: **DNW1 assembly paused.** The existing `dnw1-area-study` and
`dnw1-assembly` files are exploratory, not the baseline.

## Review order

1. `NMOS_2X0.5_BANK` — template bank
2. `XR4`, `XR5`, `XR6` — resistor macros
3. `XC1`, `XC3` — capacitor macros
4. `PMOS_1X2`, `PMOS_2.5X0.5`, `NMOS_1X0.5`
5. `PMOS_1X10`, `NMOS_3X9`, `NMOS_1X10`
6. `PMOS_1X7`, `NMOS_1X7`, `NMOS_1X9`, `PMOS_1X0.5`
7. `PASS_XM61` — full 34-finger sub-bank detail

## MOS bank checklist

| bank | drawing | array | dummy L | ring | selected DRC | status |
| --- | --- | --- | ---: | --- | --- | --- |
| `NMOS_2X0.5_BANK` | yes | 1×2 | 0.5 | 0.5/0.8 | yes | template |
| `PMOS_1X7_BANK` | yes | 6×1 | 0.5 | 0.5/0.8 | no | first pass |
| `NMOS_1X7_BANK` | yes | 2×1 | 0.5 | 0.5/0.8 | no | first pass |
| `NMOS_3X9_BANK` | yes | 1×1 | 0.5 | 0.5/0.8 | no | first pass |
| `PMOS_1X0.5_BANK` | yes | 1×8 | — | 0.5/0.8 | no | first pass |
| `NMOS_1X9_BANK` | yes | 18×2 | 0.5 | 0.5/0.8 | no | first pass |
| `PMOS_1X10_BANK` | yes | 1×1 | 0.5 | 0.5/0.8 | no | first pass |
| `NMOS_1X0.5_BANK` | yes | 2×4 | — | 0.5/0.8 | no | first pass |
| `PMOS_1X2_BANK` | yes | 3×1 | 0.5 | 0.5/0.8 | no | first pass |
| `PMOS_2.5X0.5_BANK` | yes | 1×2 | — | 0.5/0.8 | no | first pass |
| `NMOS_1X10_BANK` | yes | 3×1 | 0.5 | 0.5/0.8 | no | first pass |
| `PASS_XM61` | sub-bank only | 6×34 | — | 2.0/2.0 | no | incomplete |

## Passive macros

| macro | current content | needs |
| --- | --- | --- |
| `XR4/XR5/XR6` | **frozen XR_GROUP**: common well, bbox 40×17, stepped outline, 10 per-column long-edge dummies | structural freeze only; selected DRC and heads still open |
| `XC1` | 15×15 structure, assumed 3×15×5 stack | confirm unit split; MIM plate/contact selected DRC |
| `XC3` | 5×5 single-unit structure | MIM plate/contact selected DRC |

## Important

- Do not claim DRC/LVS signoff.
- Do not resume DNW1 packing until the bank and passive macros below are frozen.
- Bank-level ports/S-D topology remain a separate decision; current drawings do
  not include S/D metal.
