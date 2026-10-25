# Name-only OTA

A synthetic netlist with **no** `role=`, `match=` or `group=` annotations. It
demonstrates the real simulation/verification case: the instance name is the
primary semantic reference.

```bash
python3 -m a2l analyze examples/name_only_ota/ota_named.sp
python3 -m a2l build examples/name_only_ota/ota_named.sp --out out/name_only --area-budget-mm2 0.005
python3 -m a2l validate examples/name_only_ota/ota_named.sp --require-known-roles
```

The tool infers:

- `M1_DP` / `M2_DP` → `input_pair`, match `DP`
- `M3_CM` / `M4_CM` → `current_mirror`, match `CM`
- `M5_TAIL` → `tail_current`, match `TAIL`
- `M6_OUT` / `M7_OUT` → `output_stage`, group `OUT`
- `M8_EN` → `enable_switch`
- `M9_ADJ` → `adj_switch`
- `C1_CC` → `compensation`

These are **name-derived proposals**; the analog owner can still confirm or
override them with explicit annotations.
