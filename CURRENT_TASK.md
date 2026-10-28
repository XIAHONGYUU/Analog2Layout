# CURRENT_TASK

## Goal

Maintain **Analog2Layout** as an evolving workspace for technical interaction
between analog and layout engineers: role/area → floorplan/white-line intent →
Layout Card → layout delta. This is not a production rule base, signoff tool,
training assistant, review service, or audit service.

## Current state (2026-10-28)

- The deterministic a2l core still works: name/role → five-level area → floorplan
  sketch → layout delta; 49 unittest tests pass.
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
- Still open: exact NW/PW boundaries, complete CT ring, top/bottom half-W dummy
  variant, exact R/C model footprint, input-center/local-route verification, and
  returning to the LDO white-line/card.

## Next atomic action

1. Review the selected area-min full render against the remaining constraints:
   - input-pair center;
   - local empty rectangles beyond the passive bay;
   - R/C ring/DNW enclosure;
   - parasitic/power-return implications of AR 3.24.
2. Decide whether to keep AR 3.24 as the class-A reference baseline or use the
   1.21 baseline when the target slot is less wide.
3. Then resume the LDO target: R/C/X area, 14-group floorplan, LDO white-line/card.

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

- Effective area: ring inner + AA is fixed; include CT/li/M1? currently no.
- Is input-pair center a hard constraint for the area-first candidate?
- Is AR 3.24 acceptable as the default class-A reference shape?
- Do we keep `sd_mode=shared` for the matching pairs?
- Do we add top/bottom half-W dummies to the input pair?
