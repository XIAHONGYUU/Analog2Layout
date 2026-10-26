# AGENTS.md — Analog2Layout

This file is the durable operating contract for AI agents working in this repository.
`CURRENT_TASK.md` is the live action source; read it first.

## Mission

Maintain an **evolving workspace** for technical interaction
between analog and layout engineers:

1. turn device intent (role/match/group/layout) into structured data;
2. estimate area with explainable, versioned rules;
3. generate a floorplan sketch intent with device IDs;
4. compile an AI-native **Layout Guideline** (Principle → Module → Pattern → Case)
   with a one-page Layout Card as the first-read artifact;
5. plan predictable post-PEX schematic deltas (dummy/decap/reserve).

The project is an **evolving workspace**, not a final production rule base
or signoff tool.

**Ownership:** the device-role taxonomy (`a2l/roles.py`, `docs/02-annotation.md`)
and the rule pack (`rules/*.json`) belong to the analog design engineer/team.
AI agents may propose roles, flag gaps, and explain results, but they must not
treat a new role or a changed rule value as approved.

## Non-negotiable boundaries

- Do not invent foundry/company rule values. Every number must come from a rule pack or be explicitly marked as a heuristic.
- Do not add/remove/rename a role or change a rule value without an explicit analog-owner request. Propose it in an issue/PR instead.
- Names are the primary semantic source **when they carry role tokens**. Real IP netlists may use generic names (`XM46`); then the agent must propose roles from topology and a human must confirm the `role=` overlay. Use `a2l validate --require-known-roles` to catch `unknown` roles.
- Do not commit proprietary PDK data, company rule files, schematics, or layout data. Use the generic rule pack and synthetic examples.
- Do not auto-edit a user's schematic. `layout_delta.json` is a proposal; humans accept/reject it.
- Do not claim DRC/LVS/PEX accuracy. The output is an early planning estimate.
- Do not present LLM output as geometry truth. Deterministic code owns geometry and arithmetic; AI owns semantic compilation, gap marking, and explanation.
- Do not build training-assistant, main-review, or audit-service features. This workspace only carries technical interaction artifacts.
- Preserve existing user changes and unrelated files.

## Architecture rules

- Keep the core dependency-free (Python standard library only) unless a dependency is clearly justified and documented.
- Keep `a2l/area.py`, `a2l/floorplan.py`, `a2l/delta.py` deterministic and unit-testable.
- Keep `layout-guideline/` readable in two minutes per module: one-page Layout Card first, deeper Principle/Pattern/Case after.
- Any new area term must be traceable to a rule key and appear in the report/tests.
- Any new role must be added to `a2l/roles.py` with band/side/priority and documented in `docs/02-annotation.md`.
- Keep the SVG readable at a glance: solid = existing, dashed = proposed, hatched = reserved.
- JSON output is a public interface. Update `schemas/` and `docs/` when changing it.

## Validation

Run before claiming completion:

```bash
python3 -m unittest discover -s tests -v
python3 -m a2l build examples/two_stage/two_stage.sp --out examples/two_stage/out --area-budget-mm2 0.005 --fail-on-gate
python3 -m a2l compare examples/ota5/ota5.sp examples/ota5_cascode/ota5_cascode.sp --area-budget-mm2 0.005 --fail-on-gate
python3 -m a2l validate examples/name_only_ota/ota_named.sp --require-known-roles
python3 -m a2l validate examples/sky130_two_stage_opamp/opamp.sp --require-known-roles
python3 -m a2l build examples/sky130_two_stage_opamp/opamp.sp --out out/sky130_opamp --area-budget-mm2 0.006 --fail-on-gate
python3 -m a2l validate examples/sky130_ldo_01v8/ldo.annotated.sp --require-known-roles
python3 -m a2l build examples/sky130_ldo_01v8/ldo.annotated.sp --out out/sky130_ldo --area-budget-mm2 0.03 --fail-on-gate
```

If you change the SVG renderer, also rasterize and inspect the preview:

```bash
PYTHONPATH=.tools python3 -c "import cairosvg; cairosvg.svg2png(url='examples/two_stage/out/floorplan.svg', write_to='out/preview.png', scale=2)"
```

(`.tools/` is a local dev-only install and must stay untracked.)

## Documentation rules

- README is the front door; keep the quickstart working.
- `docs/03-area-model.md` must match `a2l/area.py` and `rules/generic_180.json`.
- `docs/08-ai-layout-guideline.md` and `layout-guideline/` are the primary artifacts; keep their links and templates consistent.
- When changing a formula, update the doc and add/adjust a test in the same change.
- Chinese is the primary documentation language; code identifiers and JSON keys stay English.

## Repository hygiene

- Keep generated demo output in `examples/two_stage/out/` only; do not commit other `out/` directories.
- Do not commit `.tools/`, `__pycache__/`, virtualenvs, or secrets.
- No remote push or release without an explicit human instruction.
- If Git identity is not configured, stage changes but do not invent the user's identity.
