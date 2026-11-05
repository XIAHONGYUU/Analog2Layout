# XR_GROUP — frozen for now

Status: **frozen_for_now**

Date: 2026-11-05
Members: XR4, XR5, XR6

## Frozen structure

```text
one common well / one common ring
XR5 left full-height
XR4 right-top
XR6 right-bottom
stepped outline, no rectangular right-bottom fill
bbox 40 × 17 µm
```

Dummy:

```text
one 10×0.35 horizontal strip above and below each active column
XR5: 4
XR4: 4
XR6: 2
total: 10
```

AA:

```text
perimeter band only
no AA under resistor body
```

Head/contact: intent only.

## Source identity

```text
PNG: XR_GROUP_COMPACT2.png
sha256 931bd7b0b09f1ec304a0aced8dcc46adff2b5dbf17d44a7dadac11b431ed6664
```

## Not a signoff

This freeze is structural. It is not a DRC/LVS/PEX release. The stepped
perimeter, dummy-to-ring spacing, head/contact geometry, and AA/tap enclosure
still need selected-rule checks.

## Change rule

Do not change this bank without explicit owner direction. If changed, create a
new frozen version; do not overwrite this record.
