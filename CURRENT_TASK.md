# CURRENT_TASK

## Goal

Maintain **Analog2Layout** as an evolving workspace for technical interaction
between analog and layout engineers: role/area → floorplan/white-line intent →
Layout Card → layout delta. This is not a production rule base, signoff tool,
training assistant, review service, or audit service.

## Current state (2026-10-30)

- The deterministic a2l core still works: name/role → five-level area → floorplan
  sketch → layout delta; 55 unittest tests pass.
- The SKY130 two-stage OP remains a unit test; the SKY130 1.8 V LDO remains the
  primary system target but is paused while the class-A layout-reference exercise
  is being consolidated.
- The 16-MOS class-A reference is corrected from the upstream class-AB label:
  M13 is a PMOS current-source load; only M14 is signal-driven.
- User-defined sizing is recorded: W/L/m, M8/M9 = 108 (W=9, m=12), R1 2×3 m=4,
  C1 5 pF MOM fixed 5×10 µm = 50 µm².
- White-line ground rules:
  - merged interdigitated arrays; shared DM at both ends; no fake `FILL DM`;
  - flexible per-group rows (2/4/6 preferred, others allowed);
  - `sd_mode=shared`; gate pitch **L+0.36 µm**; ring gap **0.8 µm**; group gap
    **2 µm**;
  - dummy fingers have the same geometry as active fingers; only external `DM`
    labels differ;
  - R/C are **inside DNW1**, each with an AA ring; ring AA is counted;
  - ring AA is explicitly part of effective area; no DRC/LVS or full CT ring.
- Selected area-first full render:
  - `area-min.png/svg`;
  - bbox **225.9 × 69.8 µm**, area **15,766 µm²**, AR **3.24**;
  - effective area **11,754 µm²**, utilization **74.6%**;
  - per-group rows: LOAD 3, IN 2, MIRROR_P 3 / FOLD 2, MIRROR_N 3, BIAS 11;
  - R/C passive bay has no residual local gap;
  - input-center, local-route, and parasitic checks remain open.
- Balanced baseline retained as `white-line.png/svg`:
  - bbox 147.2 × 121.2 µm, area 17,845 µm², utilization 73.7%;
  - useful for comparison; not the selected area-first version.
- Aspect exploration: tall 0.71 / square 0.99 / mid 1.21 / wide 1.63 /
  area-min 3.24. Full area ordering and metrics are in
  `examples/classa_opamp/aspect-candidates.png`.
- The 14,051 µm² packing estimate was invalid: it omitted the 2 µm group gaps and
  passive-bay insertion. The corrected full render is **15,766 µm²**.
- Skill contract foundation (2026-10-30):
  - `schemas/white_line_input.schema.json` defines the unified JSON input;
  - `examples/classa_opamp/white-line-input.json` is the class-A golden input;
  - `examples/classa_opamp/white-line-expected.json` records rows and metrics;
  - `tests/test_white_line_input.py` checks the golden case; 55 tests pass.
  - No general white-line compiler/skill script yet.
- Still open: exact NW/PW boundaries, complete CT ring, top/bottom half-W dummy
  variant, exact R/C model footprint, input-center/local-route verification, and
  returning to the LDO white-line/card.

## White-line skill direction (2026-10-28)

- Decision under evaluation: **hybrid prompt + deterministic scripts**, not
  prompt-only. Prompt owns clarification/explanation; scripts own geometry,
  area, assertions, and rendering.
- Input will be a **unified JSON** contract. Netlist is a semantic source only;
  the JSON is the geometry contract.
- Acceptance priorities are not fixed from the class-A case yet. Hard constraints,
  primary objective (minimum area), and soft constraints (input-center tolerance,
  AR cap, local empty rectangles) must be calibrated on multiple structures.
- Proposed first benchmark set:
  1. 5T OTA;
  2. two-stage Miller OTA;
  3. class-A 16-MOS (golden case);
  4. SKY130 two-stage OP (real small target);
  5. LDO 41-MOS (large/pass-FET stress test).
- No skill code or schema has been committed yet. The next step is the input
  schema + class-A golden case, then multi-structure comparison.
- The selected area-min layout (`area-min.png`, 225.9×69.8, 15,766 µm², 74.6%)
  remains the current class-A reference candidate; open checks are input-center,
  local empty rectangles, and parasitic/power-return implications.

## Next atomic action

1. (done) Define `white-line-input.schema.json` and the class-A golden case.
2. Build benchmark input JSONs for 5T OTA, two-stage Miller, SKY130 two-stage OP,
   and LDO; run the same metric/constraint collection.
3. Use the benchmark to calibrate priority tiers and thresholds.
4. Implement `SKILL.md` + deterministic compiler/checker scripts; no prompt-only
   geometry.

## Constraints

- Scope: workflow/demo/white-line intent; no production landing, no real PDK or
  company rules; no DRC/LVS claims.
- Public repo contains generic/synthetic/desensitized content only.
- Do not auto-edit a schematic; delta is a proposal.
- Dummy fill must be real geometry, not fake area padding.
- No remote push without explicit user instruction.

## Done when

- The layout-reference case can be read as a white-line intent: arrays, DM,
  rings, DNW, R/C, NW/PW, scale, and effective-area number are consistent.
- The LDO target resumes with R/C/X support and a compact 14-group floorplan.
- Tests/build remain green.

## Open questions

- Which 3–5 structures should be the first benchmark set?
- What fields are mandatory in the input JSON?
- Is input-pair center a hard constraint or a configurable tolerance?
- Is AR a hard slot constraint or a soft preference?
- Which local-empty rule is hard for matched arrays vs non-matched areas?
- Do we keep `sd_mode=shared` for matched pairs in the skill default?
- Does the skill need to generate candidate SVGs, or only the selected one plus a manifest?
