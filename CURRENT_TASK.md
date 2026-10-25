# CURRENT_TASK

## Goal

Maintain **Analog2Layout** as a **showcase/reference workspace** for technical
interaction between analog and layout engineers. The primary artifact is now the
**AI-native Layout Guideline**:

- a folder structure and workflow for turning analog intent into a one-page
  Layout Card;
- a demo that links role/area/floorplan/delta to the Layout Card;
- a public, generic scaffold that a company can overlay with private rules.

This is **not** a production rule base, signoff tool, training assistant, review
service, or audit service.

## Current state (2026-10-25)

- Deterministic demo works: role annotations → five-level area → white-line
  floorplan → layout delta.
- `layout-guideline/` scaffold added:
  - `00-workflow/` roles, steps, deliverables;
  - `01-principles/` matching, power/ground, signal/parasitics, ESD/HV;
  - `02-modules/` three cards: two-stage OTA, BGR, VCOM; plus BGR vs VCOM comparison;
  - `03-patterns/` diff pair, current mirror, resistor/cap array, trim network,
    output stage;
  - `04-cases/` two synthetic cases: BGR reference return, VCOM power return;
  - `05-templates/`, `06-sources/`.
- `docs/08-ai-layout-guideline.md` explains the four-layer model
  (Principle → Module → Pattern → Case) and the workflow.
- Agent layer now has two technical prompts: `annotate_roles` and
  `compile_layout_card`. The old `review_floorplan` prompt was removed.
- Tests/build still pass; demo output remains in `examples/two_stage/out/`.
- Git: public repo at https://github.com/XIAHONGYUU/Analog2Layout, CI green.

## Next atomic action

1. Review the BGR and VCOM cards against the “2-minute rule” and tighten wording.
2. Add a small **card completeness check** (not a review service): flags missing
   `ASK` / `UNKNOWN` / owner / evidence / source links.
3. (done) BGR vs VCOM comparison page added.
4. Optionally add LDO/SADC/AFE_CH cards only if the showcase needs more breadth.

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

- Which module should be the second card: BGR, LDO, VCOM, SADC, or AFE_CH?
- Should Layout Card stay Markdown-only, or also have a JSON/YAML form for
  tooling?
- How much private-overlay structure should be shown without leaking company
  rules?
- Should the demo keep the current two-stage OTA, or add a module with more
  matching/power/ESD tension?

## Verification

```bash
python3 -m unittest discover -s tests -v
python3 -m a2l build examples/two_stage/two_stage.sp --out examples/two_stage/out --area-budget-mm2 0.005 --fail-on-gate
python3 -m a2l validate examples/two_stage/two_stage.sp --require-explicit-roles
```
