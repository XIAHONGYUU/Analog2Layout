# CURRENT_TASK

## Goal

Ship **Analog2Layout v0.1**: a runnable, documented GitHub workspace that turns
role-annotated analog netlists into (a) a five-level area estimate, (b) a
white-line floorplan intent with shape/arrangement metrics, and (c) a
layout-induced schematic delta manifest.

## Current state (2026-10-25)

- Deterministic core implemented: parser, role taxonomy, rule pack, area model,
  floorplan intent, SVG renderer, delta planner, CLI.
- Role/rule ownership is explicit: the analog design engineer owns the taxonomy
  and rule values; AI only proposes/validates (see `DECISIONS.md` D-001).
- Area is reported as **core → active → matched → block → envelope**, with
  dummy/ring/routing/matching/periphery/reserve broken out (D-002).
- Floorplan reports **shape and arrangement**: bbox, aspect ratio, squareness,
  orientation, rows, groups/band, core utilization, whitespace (D-003).
- `a2l validate --require-explicit-roles` enforces explicit `role=` in CI;
  name fallback is warning-only.
- Three-valued area gate implemented: `--area-budget-mm2` → PASS / REJECT /
  UNCERTAIN using `area_low`/`area_high` (aligned with AnalogLoop).
- Tests: `python3 -m unittest discover -s tests -v` (34 tests).
- Demo: `examples/two_stage/out/` (SVG, PNG, JSON, HANDOFF, HTML); block area
  ≈ 3377 µm², envelope ≈ 3647 µm², shape 107.0 × 51.8 µm, aspect 2.07,
  squareness 0.48, landscape, area gate PASS at 0.005 mm² (headroom 442 µm²).
- Git: committed and pushed to
  https://github.com/XIAHONGYUU/Analog2Layout (public, `main`).
- GitHub Actions CI is green on Python 3.10 / 3.11 / 3.12.

## Next atomic action

1. Confirm the exact “committed area” convention for budget reviews:
   **`area_block_um2`** (default) vs `area_envelope_um2` (includes reserve).
2. Add a calibration CSV workflow (`a2l calibrate`) so the rule pack can be
   fitted against completed layouts.
3. Make the `squareness` warning threshold (currently `< 0.5`) configurable in
   the rule pack instead of hard-coded.
4. (done) CI runs `--fail-on-gate`; next, add a dedicated regression check that
   compares the budget against the committed baseline.

## Constraints

- No real PDK / company-confidential data in this public workspace.
- Do not auto-edit schematics; delta is a proposal.
- Keep the core dependency-free.
- Do not push to a remote or invent Git identity.
- Role/rule changes require analog-owner review (D-001).

## Done when

- `a2l build` runs on all three examples.
- Tests pass.
- `examples/two_stage/out/index.html`, `floorplan.svg` and `HANDOFF.md` are
  reviewable.
- README quickstart is accurate.
- Area hierarchy + shape metrics are visible in the report, not just internal.

## Open questions

- Is `area_block_um2` the number the team wants to quote as “模块面积”，or should
  the default include reserve (`area_envelope_um2`)?
- What squareness/aspect thresholds are “bad” for the team's block styles?
- `w` convention in the target PDK: per-finger or total?
- Which additional roles are needed (`bias_diode`, `output_nmos`, `output_pmos`,
  `dummy_logic`, ...)?
- Which schematic/layout tool should be the first adapter (Virtuoso/KLayout/OpenROAD)?

## Verification

```bash
python3 -m unittest discover -s tests -v
python3 -m a2l build examples/two_stage/two_stage.sp --out examples/two_stage/out --area-budget-mm2 0.005 --fail-on-gate
python3 -m a2l compare examples/ota5/ota5.sp examples/ota5_cascode/ota5_cascode.sp
python3 -m a2l validate examples/two_stage/two_stage.sp --require-explicit-roles
```
