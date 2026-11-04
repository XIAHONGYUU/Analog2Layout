# LDO matching review — grouped by W/L and type

Status: **proposal / needs owner confirmation**. This is not a matching signoff.

Grouping rule requested by the owner: **same W/L + same device type = one matching bank**.

Important: being in the same W/L bank is **necessary but not sufficient** for physical matching.
Devices from different logical groups (for example an enable switch and a bias cascode) can share
a W/L bank but may still need to be laid out separately. The owner must keep/split each bank.

Device type is read from the SPICE model in `netlistlabel-overlay/ldo.annotated.sp`
(`sky130_fd_pr__pfet...` → PMOS, `sky130_fd_pr__nfet...` → NMOS), not guessed from names.

### `m` is not the device count

- `devices` = number of SPICE device instances, **not** multiplied by `m`.
- `Σm` = sum of each device's `m` multiplicity.
- `Σnf` = sum of each device's `nf`.
- `fingers` = `Σ(nf × m)` — this is what the compiler lays out as active fingers.
- Example: `XM61` is **one device** with `m=1000`; it contributes **1** to `devices`,
  **1000** to `Σm`, and **1000** to `fingers`.

## Bank summary

| bank | type | W/L (µm) | devices (instances) | Σm | Σnf | fingers = Σ(nf×m) | m values | logical groups | current match tokens |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| `PMOS_1x0.5` | PMOS | 1/0.5 | 8 | 8 | 8 | 8 | 1 | AMP, BIAS, CTRL_EN, OUT | `CAS_AMP`, `CAS_BIAS` |
| `PMOS_2.5x0.5` | PMOS | 2.5/0.5 | 2 | 2 | 2 | 2 | 1 | CTRL_EN, CTRL_SEL | — |
| `PMOS_1x2` | PMOS | 1/2 | 3 | 3 | 3 | 3 | 1 | START | — |
| `PMOS_1x7` | PMOS | 1/7 | 6 | 6 | 6 | 6 | 1 | AMP, BIAS, OUT, REF | `LOAD_AMP`, `MIR_BIAS_VBIAS_P` |
| `PMOS_1x10` | PMOS | 1/10 | 1 | 1 | 1 | 1 | 1 | BIAS | — |
| `NMOS_1x0.5` | NMOS | 1/0.5 | 8 | 8 | 8 | 8 | 1 | CTRL_EN, CTRL_SEL, START | — |
| `NMOS_2x0.5` | NMOS | 2/0.5 | 2 | 2 | 2 | 2 | 1 | AMP | `DP_AMP` |
| `NMOS_5x0.5` | NMOS | 5/0.5 | 1 | 1000 | 1 | 1000 | 1000 | OUT | — |
| `NMOS_1x7` | NMOS | 1/7 | 2 | 2 | 2 | 2 | 1 | AMP | `MIR_AMP_net2` |
| `NMOS_1x9` | NMOS | 1/9 | 4 | 35 | 4 | 35 | 5, 20 | BIAS, START | `MIR_BIAS_DEG` |
| `NMOS_3x9` | NMOS | 3/9 | 1 | 1 | 1 | 1 | 1 | AMP | — |
| `NMOS_1x10` | NMOS | 1/10 | 3 | 3 | 3 | 3 | 1 | REF | — |

**Owner decision 2026-11-04 — `PMOS_1x0.5`:** keep all 8 devices as **one large
matching item**. `XM86` and `XM88` are **real enable switches at the two outer
edges**, with separate S/D (not connected dummy fingers). The interior order is
`XM86, XM57, XM58, XM59, XM63, XM65, XM90, XM88`.

## Owner-confirmed bank plan (2026-11-04)

| bank | physical plan | dummy | active L (µm) | dummy L (µm) |
| --- | --- | --- | ---: | ---: |
| `PMOS_1x0.5` | one large bank; XM86/XM88 at outer edges | edge switches, no extra dummy | 0.5 | — |
| `PMOS_2.5x0.5` | XM76/XM84 together | none | 0.5 | — |
| `PMOS_1x2` | XM71/XM72/XM73 together | 1 per side | 2 | 0.5 |
| `PMOS_1x7` | XM46/56/62/64/60/79 together | 1 per side | 7 | 0.5 |
| `PMOS_1x10` | XM68 alone | 1 per side | 10 | 0.5 |
| `NMOS_1x0.5` | XM70/75/77/78/83/85/87/89 together | none | 0.5 | — |
| `NMOS_2x0.5` | XM52/XM53 together | 1 per side | 0.5 | 0.5 |
| `NMOS_5x0.5` | XM61; 6 sub-banks ×34 fingers, W≈24.51, total W=5000, 3×2, shared body-ring walls; outer DNW guard ring | none (edge dummy not used) | 0.5 | — |
| `NMOS_1x7` | XM48/XM55 together | 1 per side | 7 | 0.5 |
| `NMOS_1x9` | XM66/67/69/74 together | 1 per side | 9 | 0.5 |
| `NMOS_3x9` | XM54 alone | 1 per side | 9 | 0.5 |
| `NMOS_1x10` | XM80/XM81/XM82 together, separate block | 1 per side | 10 | 0.5 |

Matching is **interleaved by m ratio**, not sequential. The compiler uses a
weighted round-robin sequence. S/D rule: separate drains; share a source rail
only where the source net is identical. Dummy connections/metals are not drawn
in this step.

Ring policy: MOS bank ring 0.5 / gap 0.8; XM61 body ring 2.0 / gap 2.0 with an
extra outer DNW guard ring; passive ring 1.0 / 0.8; DNW margin 2.0.

## Banks

### `PMOS_1x0.5` — PMOS, W=1 µm, L=0.5 µm

**Owner decision: one big matching bank.**

`XM86` and `XM88` are real enable switches at the two outer edges; they keep
separate S/D and are not unconnected dummy fingers. `XM57/XM58` and
`XM63/XM65` remain the cascade cores; `XM59` and `XM90` are inside the same
array as the owner requested.

Logical groups: AMP, BIAS, CTRL_EN, OUT. Current match token: not yet written
back to the input as `PMOS_1X0.5_BANK`; this is the owner decision being applied.

Proposed physical order (one row, outer devices first/last):

```text
XM86 | XM57 | XM58 | XM59 | XM63 | XM65 | XM90 | XM88
edge       matched/bank active                edge
```

| device | logical group | role | nf | m | total fingers | current match | owner decision |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| XM57 | AMP | cascode | 1 | 1 | 1 | `CAS_AMP` | bank active |
| XM58 | AMP | cascode | 1 | 1 | 1 | `CAS_AMP` | bank active |
| XM63 | BIAS | cascode | 1 | 1 | 1 | `CAS_BIAS` | bank active |
| XM65 | BIAS | cascode | 1 | 1 | 1 | `CAS_BIAS` | bank active |
| XM90 | CTRL_EN | enable_switch | 1 | 1 | 1 | — | bank active |
| XM59 | OUT | output_stage | 1 | 1 | 1 | — | bank active |
| XM86 | CTRL_EN | enable_switch | 1 | 1 | 1 | — | **edge switch / separate S/D** |
| XM88 | CTRL_EN | enable_switch | 1 | 1 | 1 | — | **edge switch / separate S/D** |

### `PMOS_2.5x0.5` — PMOS, W=2.5 µm, L=0.5 µm

Logical groups: CTRL_EN, CTRL_SEL. Current match tokens: none.

| device | logical group | role | nf | m | total fingers | current match | matched? | owner decision |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| XM84 | CTRL_EN | enable_switch | 1 | 1 | 1 | `—` | False | keep / split / add |
| XM76 | CTRL_SEL | adj_switch | 1 | 1 | 1 | `—` | False | keep / split / add |

### `PMOS_1x2` — PMOS, W=1 µm, L=2 µm

Logical groups: START. Current match tokens: none.

| device | logical group | role | nf | m | total fingers | current match | matched? | owner decision |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| XM71 | START | bias | 1 | 1 | 1 | `—` | False | keep / split / add |
| XM72 | START | bias | 1 | 1 | 1 | `—` | False | keep / split / add |
| XM73 | START | bias | 1 | 1 | 1 | `—` | False | keep / split / add |

### `PMOS_1x7` — PMOS, W=1 µm, L=7 µm

Logical groups: AMP, BIAS, OUT, REF. Current match tokens: `LOAD_AMP`, `MIR_BIAS_VBIAS_P`.

| device | logical group | role | nf | m | total fingers | current match | matched? | owner decision |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| XM46 | AMP | current_mirror | 1 | 1 | 1 | `LOAD_AMP` | True | keep / split / add |
| XM56 | AMP | current_mirror | 1 | 1 | 1 | `LOAD_AMP` | True | keep / split / add |
| XM62 | BIAS | current_mirror | 1 | 1 | 1 | `MIR_BIAS_VBIAS_P` | True | keep / split / add |
| XM64 | BIAS | current_mirror | 1 | 1 | 1 | `MIR_BIAS_VBIAS_P` | True | keep / split / add |
| XM60 | OUT | current_mirror | 1 | 1 | 1 | `—` | False | keep / split / add |
| XM79 | REF | current_mirror | 1 | 1 | 1 | `—` | False | keep / split / add |

### `PMOS_1x10` — PMOS, W=1 µm, L=10 µm

Logical groups: BIAS. Current match tokens: none.

| device | logical group | role | nf | m | total fingers | current match | matched? | owner decision |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| XM68 | BIAS | bias | 1 | 1 | 1 | `—` | False | keep / split / add |

### `NMOS_1x0.5` — NMOS, W=1 µm, L=0.5 µm

Logical groups: CTRL_EN, CTRL_SEL, START. Current match tokens: none.

| device | logical group | role | nf | m | total fingers | current match | matched? | owner decision |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| XM83 | CTRL_EN | enable_switch | 1 | 1 | 1 | `—` | False | keep / split / add |
| XM85 | CTRL_EN | enable_switch | 1 | 1 | 1 | `—` | False | keep / split / add |
| XM87 | CTRL_EN | enable_switch | 1 | 1 | 1 | `—` | False | keep / split / add |
| XM89 | CTRL_EN | enable_switch | 1 | 1 | 1 | `—` | False | keep / split / add |
| XM75 | CTRL_SEL | adj_switch | 1 | 1 | 1 | `—` | False | keep / split / add |
| XM77 | CTRL_SEL | adj_switch | 1 | 1 | 1 | `—` | False | keep / split / add |
| XM78 | CTRL_SEL | adj_switch | 1 | 1 | 1 | `—` | False | keep / split / add |
| XM70 | START | bias | 1 | 1 | 1 | `—` | False | keep / split / add |

### `NMOS_2x0.5` — NMOS, W=2 µm, L=0.5 µm

Logical groups: AMP. Current match tokens: `DP_AMP`.

| device | logical group | role | nf | m | total fingers | current match | matched? | owner decision |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| XM52 | AMP | input_pair | 1 | 1 | 1 | `DP_AMP` | True | keep / split / add |
| XM53 | AMP | input_pair | 1 | 1 | 1 | `DP_AMP` | True | keep / split / add |

### `NMOS_5x0.5` — NMOS, W=5 µm, L=0.5 µm

Logical groups: OUT. Current match tokens: none.

| device | logical group | role | nf | m | total fingers | current match | matched? | owner decision |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| XM61 | OUT | output_stage | 1 | 1000 | 1000 | `—` | False | keep / split / add |

### `NMOS_1x7` — NMOS, W=1 µm, L=7 µm

Logical groups: AMP. Current match tokens: `MIR_AMP_net2`.

| device | logical group | role | nf | m | total fingers | current match | matched? | owner decision |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| XM48 | AMP | current_mirror | 1 | 1 | 1 | `MIR_AMP_net2` | True | keep / split / add |
| XM55 | AMP | current_mirror | 1 | 1 | 1 | `MIR_AMP_net2` | True | keep / split / add |

### `NMOS_1x9` — NMOS, W=1 µm, L=9 µm

Logical groups: BIAS, START. Current match tokens: `MIR_BIAS_DEG`.

| device | logical group | role | nf | m | total fingers | current match | matched? | owner decision |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| XM66 | BIAS | current_mirror | 1 | 20 | 20 | `MIR_BIAS_DEG` | True | keep / split / add |
| XM67 | BIAS | current_mirror | 1 | 5 | 5 | `MIR_BIAS_DEG` | True | keep / split / add |
| XM69 | BIAS | current_mirror | 1 | 5 | 5 | `—` | False | keep / split / add |
| XM74 | START | current_mirror | 1 | 5 | 5 | `—` | False | keep / split / add |

### `NMOS_3x9` — NMOS, W=3 µm, L=9 µm

Logical groups: AMP. Current match tokens: none.

| device | logical group | role | nf | m | total fingers | current match | matched? | owner decision |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| XM54 | AMP | tail_current | 1 | 1 | 1 | `—` | False | keep / split / add |

### `NMOS_1x10` — NMOS, W=1 µm, L=10 µm

Logical groups: REF. Current match tokens: none.

| device | logical group | role | nf | m | total fingers | current match | matched? | owner decision |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| XM80 | REF | cascode | 1 | 1 | 1 | `—` | False | keep / split / add |
| XM81 | REF | bias | 1 | 1 | 1 | `—` | False | keep / split / add |
| XM82 | REF | bias | 1 | 1 | 1 | `—` | False | keep / split / add |

## Owner review

- Mark each bank `keep`, `split`, or `add`; a W/L bank is only a candidate set.
- Same W/L + same type is the physical matching precondition, not proof of matching.
- Devices in different logical groups need an explicit decision before sharing an array.
- `XM66/XM67` (NMOS 1/9, m=20/5) are already marked `MIR_BIAS_DEG`; confirm the 20:5 interleave.
- `XM80/XM81/XM82` are NMOS 1/10 but currently no match token; decide whether they are a matched trio.
- `XM71/XM72/XM73` are PMOS 1/2 but currently no match token; decide whether they are a matched trio.
- `XM59/XM60` and the CTRL switches share W/L banks with other functions; do not merge by W/L alone.

## Current `match` tokens (proposal only)

- AMP: `LOAD_AMP` (XM46/XM56), `MIR_AMP_net2` (XM48/XM55), `DP_AMP` (XM52/XM53), `CAS_AMP` (XM57/XM58).
- BIAS: `MIR_BIAS_VBIAS_P` (XM62/XM64), `CAS_BIAS` (XM63/XM65), `MIR_BIAS_DEG` (XM66/XM67).
- All other devices have no `match` token and must not be silently clustered.

Corrections can be made directly in this file or returned as a bank/device table; the compiler will then be rerun deterministically.
