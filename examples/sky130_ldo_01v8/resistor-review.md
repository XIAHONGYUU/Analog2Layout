# LDO resistor placement / connection review

Status: **placement study, not GDS/DRC/LVS signoff**.

Source: `netlistlabel-overlay/ldo.annotated.sp` lines 20, 21, 42.

## Netlist connectivity

| Device | Terminals | Connected function |
| --- | --- | --- |
| XR5 | AVSS – VM – AVSS(body) | lower feedback divider |
| XR4 | VM – VOUT – AVSS(body) | upper feedback divider |
| XR6 | AVSS – net5 – AVSS(body) | XM66 source degeneration |
| XC1 | VERR – AVSS | AMP output decap |
| XC3 | VREF – AVSS | VREF input filter/decap |

The two FB resistors form a series divider:

```text
VOUT -- XR4 -- VM -- XR5 -- AVSS
```

`VM` is a shared center node, not two independent two-terminal blocks.

## Current V1 placement

From the current manifest:

| Device | Position | Verdict |
| --- | --- | --- |
| XR5 | x=2.0, y=33.4 | adjacent to XR4, but each has its own ring |
| XR4 | x=21.6, y=33.4 | ring boundary separates it from XR5 |
| XR6 | x=37.2, y=33.4 | far from the BIAS/XM66 bank; no net5 route |
| XC1 | x=27.0, y=2.0 | no shown VERR connection |
| XC3 | x=48.8, y=33.4 | no shown VREF connection |

V1 is **not connectivity-proof**:

- `XR4/XR5` are geometrically adjacent, but the VM center node is not drawn
  between them; the two independent rings do not show a shared tap.
- `XR6` is not placed against XM66's source.
- `XC1/XC3` have no drawn terminal connection.
- No S/D or resistor-end metal is drawn, so connectivity is not proven.

## Variants

See [resistor-variants.png](resistor-variants.png).

| Variant | Intent |
| --- | --- |
| V1 | current free placement; red flags show unproven connections |
| V2 | XR4/XR5 in one FB ring with shared VM; XR6 next to BIAS/XM66; C1/C3 in functional zones |
| V3 | same nets as V2, but rotated/vertical FB divider |

V2 is the recommended placement intent. V3 is the orientation alternative.

## Remaining requirement

The variants show **placement intent and terminal names**, not resistor-end
metal, vias, or body ties. Those must be drawn before DRC/LVS/PEX signoff.

## Why the main block looks square

The square block is a **folded footprint**, not the resistor body.

Actual xhigh resistor active dimensions:

| device | active length | active width | folded block | segments | dummy |
| --- | ---: | ---: | --- | ---: | ---: |
| XR4 | 180 µm | 0.35 µm | 20×10.55 µm | 18 × 10 µm | 7 |
| XR5 | 360 µm | 0.35 µm | 20×20.75 µm | 36 × 10 µm | 13 |
| XR6 | 40 µm | 0.35 µm | 10×7.15 µm | 4 × 10 µm | 5 |

So:

```text
true resistor body: 0.35 × L
folded block:        a layout choice; roughly square
```

The previous block diagram did not make that distinction clear and drew a
grid of cells. The current block diagram draws a serpentine intent; the
dimension reference is in `resistor-scale.png`.

## Segment gap: 0.5 µm is not a PDK value

The current folded resistor uses:

```text
segment = 10 × 0.35 µm
segment gap = 0.5 µm
```

`0.5 µm` is a layout choice, not a Sky130 rule. Relevant facts:

| rule | value | meaning |
| --- | ---: | --- |
| `poly.2` | 0.21 µm | minimum poly spacing |
| `poly.3` | 0.33 µm | minimum poly resistor width |
| `poly.9` | 0.48 µm | min. poly resistor space to poly or diff/tap |

If the folded resistor is one continuous poly shape, its notch/self-spacing must
be checked by the actual DRC deck. If dummy/segments are separate poly shapes,
`poly.9` is the relevant 0.48 µm bound; 0.5 µm is only 0.02 µm above it.

Source: `pdk/sky130/facts.json`, `resistor_spacing`.
