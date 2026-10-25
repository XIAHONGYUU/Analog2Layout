# ota5_cascode — architecture comparison example

Same OTA core as `ota5`, plus a cascode load (M6/M7). Use it to see how the
tool exposes the area cost of a topology change:

```bash
python3 -m a2l compare examples/ota5/ota5.sp examples/ota5_cascode/ota5_cascode.sp --out out/compare
```

With generic-180 rules the cascode version is a few hundred µm² larger at the
same cap value. That is the kind of early, explainable trade-off the tool is
meant to support — not a signoff comparison.
