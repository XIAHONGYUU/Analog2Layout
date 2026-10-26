# CURRENT_TASK

## Goal

Maintain **Analog2Layout** as an **evolving workspace** for
technical interaction between analog and layout engineers. The primary artifact is now the
**AI-native Layout Guideline**:

- a folder structure and workflow for turning analog intent into a one-page
  Layout Card;
- a demo that links role/area/floorplan/delta to the Layout Card;
- a public, generic scaffold that a company can overlay with private rules.

This is **not** a production rule base, signoff tool, training assistant, review
service, or audit service.

## Current state (2026-10-26)

- Deterministic demo works: name/role semantics → five-level area → floorplan
  sketch → layout delta.
- `layout-guideline/` scaffold added:
  - `00-workflow/` roles, steps, deliverables;
  - `01-principles/` matching, power/ground, signal/parasitics, ESD/HV,
    sensitive-region/reuse;
  - `02-modules/` three cards: two-stage OTA, BGR, VCOM; plus BGR vs VCOM comparison;
  - `03-patterns/` diff pair, current mirror, resistor/cap array, trim network,
    output stage;
  - `04-cases/` two synthetic cases: BGR reference return, VCOM power return;
  - `05-templates/` card/intent/area-target/change-log; `06-sources/`;
  - `07-problems/` problem-to-guideline loop.
- `examples/name_only_ota/` demonstrates name-token parsing and match inference
  with no `role=` properties; `--require-known-roles` replaces the old
  explicit-role flag.
- `docs/09-white-line-and-floorplan.md` separates Virtuoso white line from our
  floorplan sketch.
- `docs/10-layout-variants.md` documents target-bbox variants (200×200 vs
  100×400); code generation is still pending.
- Sensitive-core vs device-core distinction documented; code metrics for
  `sensitive_core` / `flexible_area` / `reuse_candidate` are still pending.
- `docs/diagrams/` contains the first-read visuals: three-minute overview,
  four-panel full overview, variants, and the guideline problem loop.
- First real target added: `examples/sky130_two_stage_opamp/` — a name-only
  SKY130 two-stage Miller op-amp derived from an MIT-licensed open-source design
  (Nithin P, 2024), with 10 MOS + 1 compensation cap and a real bias/enable
  branch (`M8_BIAS`, `M9_EN`, `M10_EN_PD`). Source/license are recorded in the
  example and in `docs/11-target-sky130-opamp.md`.
- Target run: 11 devices / 7 groups / device core 2048 µm² / block 3526 µm² /
  gate PASS at 6000 µm²; `validate --require-known-roles` passes.
- `docs/08-ai-layout-guideline.md` explains the four-layer model
  (Principle → Module → Pattern → Case) and the workflow.
- Agent layer now has two technical prompts: `annotate_roles` and
  `compile_layout_card`. The old `review_floorplan` prompt was removed.
- 40 unittest tests pass; demo output remains in `examples/two_stage/out/`.
- Git: public repo at https://github.com/XIAHONGYUU/Analog2Layout, CI green.

## Next atomic action

0. (done) First-page diagrams checked at 880 px width; tall/short labels were
   adjusted to avoid clipping.
1. Generate a one-page Layout Card for the SKY130 target and link it from the
   module index.
2. Split the area model into `device_core` / `sensitive_core` / `flexible_area` /
   `reuse_candidate`, including ring/WPE/dummy/shielding/routing reservation.
3. Add a target-bbox/aspect variant generator (square / wide / tall) and compare
   utilization / power return / matching-group stretch.
4. Add 1–2 real problem records from this target to `07-problems/` and show the
   resulting principle/pattern patch.
5. Add a small card completeness check (not a review service): flags missing
   `ASK` / `UNKNOWN` / owner / evidence / source links.

## Constraints

- Showcase only: no production landing, no real PDK/company rules.
- Public repo contains generic/synthetic content only.
- No training assistant, main-review, or audit service.
- Only technical interaction artifacts: intent, card, floorplan, delta, change log.
- Do not auto-edit a schematic; delta is a proposal.
- No remote push without explicit user instruction.

## Done when

- A layout engineer can read the two-stage, BGR, or VCOM Layout Card in ~2 minutes
  and state the top 3 risks / must-preserve items.
- The workflow in `layout-guideline/00-workflow/` is clear enough to add a new
  module from templates.
- README links the guideline scaffold and docs/08 correctly.
- Existing tests/build still pass.

## Open questions

- Sensitive region 的边界：按模块、按 group、还是按 net 划分？
- 复用敏感区时，最小必须携带哪些版本/验证条件？
- 目标 bbox 变体需要多少候选？谁来做最终选择？
- 问题回流到什么阈值必须升级为 principle/pattern，而不是只留在 case？
- Layout Card 是否需要机器可读形式（JSON/YAML）？

## Verification

```bash
python3 -m unittest discover -s tests -v
python3 -m a2l build examples/two_stage/two_stage.sp --out examples/two_stage/out --area-budget-mm2 0.005 --fail-on-gate
python3 -m a2l validate examples/name_only_ota/ota_named.sp --require-known-roles
python3 -m a2l validate examples/sky130_two_stage_opamp/opamp.sp --require-known-roles
python3 -m a2l build examples/sky130_two_stage_opamp/opamp.sp --out out/sky130_opamp --area-budget-mm2 0.006 --fail-on-gate
```
