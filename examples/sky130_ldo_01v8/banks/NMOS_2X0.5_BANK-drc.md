# NMOS_2X0.5_BANK — DRC-aware primitive review

Status: **selected-rule check**, not a full DRC/LVS/PEX run.

Geometry:

```text
core  5.21 × 2.26 µm
outer 7.81 × 4.86 µm
L=0.5 W=2.0 diff_len=1.10 contact=0.17
```

## Checked rules

| check | value | rule | result |
| --- | ---: | --- | --- |
| poly_width_um | 0.5 | poly.3 min 0.33 | PASS |
| sd_length_um | 0.3 | poly.7 min 0.25 | PASS |
| poly_extension_um | 0.13 | poly.8 min 0.13 | PASS |
| licon_size_um | 0.17 | licon.1 min 0.17 | PASS |
| licon_gate_gap_um | 0.075 | licon.11 min 0.055 | PASS |
| diff_enclosure_licon_um | 0.055 | licon.5 min 0.04 | PASS |
| diff_space_um | 0.27 | difftap.3 min 0.27 | PASS |
| tap_contact_in_ring | true | licon on tap/AA ring | PASS |
| tap_contact_enclosure_um | 0.165 | licon.7 min 0.12 | PASS |

## Important correction

The earlier bank drawing put tap/body contacts in the ring gap, not on the
ring AA. They are now placed inside the 0.5 µm tap ring:

```text
tap contact enclosure = 0.165 µm >= licon.7 0.12 µm
tap contact is on the ring, not floating in the gap
```

## Not checked here

- actual full DRC deck run (KLayout not installed in this workspace);
- all tap body-ring enclosure rules;
- contact-to-contact spacing and contact overlap with poly;
- poly-to-contact edge cases beyond the selected gate gap;
- S/D metal, gate metal, vias, body tie, DNW/NW/DNW polygons;
- dummy connection/metals.

Source deck: `out/refs/sky130.lydrc`; facts: `pdk/sky130/facts.json`.

This is a DRC-aware white-line primitive, not a signoff result.

## Ring / spacing audit

Current bank drawing:

```text
outer ring width = 0.50 µm
ring gap to core = 0.80 µm
poly extension = 0.13 µm
tap/body contact = 0.17 µm
```

| check | value | rule | result |
| --- | ---: | --- | --- |
| ring width | 0.50 | difftap.1 min 0.15 | PASS |
| ring-to-diff gap | 0.80 | difftap.3 min 0.27 | PASS |
| poly-to-ring gap | 0.67 | poly.5 min 0.055 | PASS |
| tap contact enclosure | 0.165 | licon.7 min 0.12 | PASS |
| tap contact on ring | yes | licon on tap/AA | PASS |

The ring is DRC-minimum-compatible at 0.5 / 0.8, but:

- only four corner tap contacts are drawn; a real body ring should have
  contacts distributed along the ring, not only at corners;
- the ring is drawn as a generic tap/body ring, not a full GDS layer stack;
- full ring enclosure/notch/contact-spacing rules are not checked without
  the actual DRC deck.
