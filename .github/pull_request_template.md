## What changed

## Why

## Verification

- [ ] `python3 -m unittest discover -s tests -v`
- [ ] `python3 -m a2l build examples/two_stage/two_stage.sp --out examples/two_stage/out`
- [ ] `python3 -m a2l compare examples/ota5/ota5.sp examples/ota5_cascode/ota5_cascode.sp`
- [ ] SVG reviewed for label overlap / clipping
- [ ] No PDK, company rules, real schematics/layouts, or secrets committed

## Notes for reviewers

Area/rule changes: include before/after numbers and the rule key.
JSON changes: update `schemas/` and `docs/`.
