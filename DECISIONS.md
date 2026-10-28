# Decisions

Durable decisions for Analog2Layout. Each entry has an owner, status, and source.
`CURRENT_TASK.md` is the live action source; this file records decisions that
should survive individual tasks.

---

## D-001 — Role taxonomy and rule pack are owned by the analog design engineer

- **Status:** active
- **Date:** 2026-10-25
- **Owner:** analog design engineer / analog design team
- **Source:** user feedback
- **Decision:** The role table (`a2l/roles.py`, `docs/02-annotation.md`) and the
  rule pack (`rules/*.json`) are the analog design team's responsibility. AI and
  agents may propose roles, flag gaps, and explain results, but they do not
  approve taxonomy changes or rule values.
- **Consequences:**
  - explicit `role=` is preferred; name fallback is a suggestion;
  - `a2l validate --require-explicit-roles` can enforce explicit annotation in CI;
  - every role/rule change needs owner review, a version bump, and (for area
    rules) calibration evidence;
  - the public repository only carries the generic educational pack.
- **Related:** `AGENTS.md`, `docs/02-annotation.md`, `rules/README.md`.

---

## D-002 — Area is reported as a five-level hierarchy, not a single number

- **Status:** active
- **Date:** 2026-10-25
- **Owner:** analog design engineer / analog design team
- **Source:** user feedback
- **Decision:** Area is reported as:
  1. **Core** — MOS OD footprint + capacitor plate area;
  2. **Active** — core + guard ring + device-level routing;
  3. **Matched** — active + boundary dummy + matching overhead;
  4. **Block** — matched + periphery + block routing;
  5. **Envelope** — block + PEX-fix reserve.
  Dummy area, ring, device routing, matching overhead, periphery and reserve are
  reported as separate buckets.
- **Consequences:**
  - `area_core_um2` / `area_active_um2` / `area_matched_um2` /
    `area_block_um2` / `area_envelope_um2` are public JSON keys;
  - “committed area” for budget discussions is `area_block_um2` by default;
  - reserve is always reported separately and never silently folded into block.
- **Related:** `a2l/area.py`, `docs/03-area-model.md`, `examples/two_stage/out/area_report.md`.

---

## D-003 — Shape and arrangement are first-class area metrics

- **Status:** active
- **Date:** 2026-10-25
- **Owner:** analog design engineer / analog design team
- **Source:** user feedback
- **Decision:** Two modules with the same area are not equivalent if their shape
  or arrangement differs. The floorplan reports:
  - block width/height;
  - aspect ratio (W/H);
  - squareness (`min/max`, 1.0 = square);
  - orientation (`landscape` / `portrait` / `square-ish`);
  - rows and groups per band;
  - a one-line arrangement summary;
  - core utilization / whitespace fraction.
- **Consequences:**
  - these metrics live in `floorplan.json` `stats` and appear in `HANDOFF.md` /
    `index.html`;
  - the default placement template is intentionally explainable, not optimal;
  - future work can add a shape/arrangement score to architecture comparison.
- **Related:** `a2l/floorplan.py`, `docs/04-floorplan.md`.

---

## D-004 — Deltas are proposals, never automatic schematic edits

- **Status:** active
- **Date:** 2026-10-25
- **Owner:** project
- **Source:** project design
- **Decision:** `layout_delta.json` items have owner/status/reason/rule and are
  reviewed by humans. a2l does not modify a schematic.
- **Consequences:**
  - accepted analog items become schematic ECO work;
  - accepted layout items become floorplan checklist work;
  - a delta can be rejected/deferred;
  - reserve shortfall is surfaced (delta total vs PEX-fix reserve).
- **Related:** `a2l/delta.py`, `docs/05-layout-delta.md`.

---

## D-005 — Public repo contains only generic/desensitized rules

- **Status:** active
- **Date:** 2026-10-25
- **Owner:** project
- **Source:** project design
- **Decision:** The public repository never contains foundry PDK data, company
  rule decks, real schematics/layouts, or PEX reports. Company packs live in a
  private registry/submodule and are passed with `--rules`.
- **Consequences:**
  - examples are synthetic;
  - `rules/generic_180.json` is marked `educational`;
  - contributions must be desensitized.
- **Related:** `rules/README.md`, `AGENTS.md`.

---

## D-006 — Area gate is three-valued, not a single threshold

- **Status:** active
- **Date:** 2026-10-25
- **Owner:** analog design engineer / analog design team
- **Source:** user feedback + AnalogLoop alignment
- **Decision:** When a budget is supplied (`--area-budget-mm2`), compare it with
  the estimate interval:
  - `area_high <= budget` → `PASS`;
  - `area_low > budget` → `REJECT`;
  - otherwise → `UNCERTAIN`.
  `--fail-on-gate` makes CI fail unless the status is `PASS`.
- **Consequences:**
  - nominal-only budget checks are not allowed in CI;
  - `UNCERTAIN` is a real outcome, not a hidden warning;
  - the three-valued gate matches AnalogLoop's area gate semantics.
- **Related:** `a2l/area.py`, `a2l/cli.py`, `docs/03-area-model.md`.

---

## D-007 — This workspace keeps evolving; it is not a production landing

- **Status:** active
- **Date:** 2026-10-25
- **Owner:** project
- **Source:** user direction
- **Decision:** Analog2Layout exists to develop and communicate the workflow: some parts are
  runnable, some are still being built, and the workspace will keep evolving. It
  is not a final production rule base, signoff tool, or company deployment.
- **Consequences:**
  - docs/examples may be synthetic;
  - calibration, PDK integration, and company rollout are not goals of this
    iteration; they may be explored later;
  - success is measured by clarity of the workflow and artifacts, not by
    production accuracy.

---

## D-008 — AI-native Layout Guideline is the primary artifact

- **Status:** active
- **Date:** 2026-10-25
- **Owner:** analog design + layout
- **Source:** user direction
- **Decision:** The central artifact is a `layout-guideline/` workspace with:
  - Principle (why);
  - Module (what this module fears);
  - Pattern (how this class is drawn);
  - Case (what went wrong / how it was verified);
  - a one-page Layout Card as the first-read artifact.
- **Consequences:**
  - the folder/workflow is part of the deliverable;
  - the site should be readable in ~2 minutes per module;
  - specific numbers stay in a private rule/overlay layer.

---

## D-009 — Only technical interaction is in scope

- **Status:** active
- **Date:** 2026-10-25
- **Owner:** project
- **Source:** user direction
- **Decision:** Do not build training-assistant, main-review, or audit-service
  features in this workspace. The workspace only carries technical interaction
  artifacts: intent, Layout Card, floorplan, delta, change log.
- **Consequences:**
  - the old `review_floorplan` prompt was removed;
  - agent prompts are limited to role annotation and Layout Card compilation;
  - "review" appears only as human engineering review, not as an AI service.

---

## D-010 — Public generic layer + private company overlay

- **Status:** active
- **Date:** 2026-10-25
- **Owner:** project
- **Source:** project design
- **Decision:** The public repo contains structure, templates, generic principles,
  and synthetic examples. Real PDK/company rules, module cards, and raw cases
  live in a private overlay and are linked by IDs.
- **Consequences:**
  - public examples must be synthetic or desensitized;
  - private content is not copied into public docs;
  - `source_id` / `rule_key` / `case_id` are the join points.

---

## D-011 — Device names are the primary semantic source

- **Status:** active
- **Date:** 2026-10-25
- **Owner:** analog design engineer / analog design team
- **Source:** user correction
- **Decision:** Real simulation/verification netlists usually carry semantics only
  in instance names. a2l treats the name token as the primary reference for
  role/match/group. Explicit `role=` is an optional confirmed override, not a
  precondition.
- **Consequences:**
  - name-only netlists are a first-class input;
  - `--require-known-roles` replaces `--require-explicit-roles`;
  - unknown names are marked `unknown`, not guessed into a confident role.

---

## D-012 — Virtuoso white line is not our floorplan sketch

- **Status:** active
- **Date:** 2026-10-25
- **Owner:** project
- **Source:** user correction
- **Decision:** In Virtuoso, a white line is a schematic annotation/guide line
  that can be shown with the circuit. Our generated `floorplan.svg/json` is a
  separate layout-planning sketch. The two must not share a name.
- **Consequences:**
  - "白线图" is retired as a name for our artifact;
  - use "布局草图 / floorplan sketch" for our output;
  - a future schematic overlay (white-line markers) would be a separate feature.

---

## D-013 — Layout must be area/aspect- and device-aware

- **Status:** active
- **Date:** 2026-10-25
- **Owner:** analog design + layout
- **Source:** user correction
- **Decision:** Placement is constrained by device type/parameters, matching,
  sensitive regions, power/ESD, and the target total area/bbox. The same total
  area can require different layouts for 200×200, 100×400, or 400×100.
- **Consequences:**
  - a single default floorplan is not enough;
  - future work should generate and compare multiple target-bbox variants;
  - a layout is chosen by constraints and evidence, not by "where it looks nice".

---

## D-014 — "Core" means sensitive reusable region, not pure device OD

- **Status:** active
- **Date:** 2026-10-25
- **Owner:** analog design + layout
- **Source:** user correction
- **Decision:** In layout discussions, "core" means the sensitive region that
  includes mandatory special drawing, ring, WPE/STI spacing, dummy, shielding,
  and routing reservation; it is a candidate for reuse. The pure OD/cap metric is
  called `device_core`, not `sensitive_core`.
- **Consequences:**
  - current `area_core_um2` is provisional and labelled `device_core`;
  - next area model should add `sensitive_core`, `flexible_area`,
    `sensitive_overhead`, and `reuse_candidate`;
  - reuse must carry process/voltage/temperature/version conditions.

---

## D-015 — Layout guideline iterates from real problems

- **Status:** active
- **Date:** 2026-10-25
- **Owner:** analog design + layout
- **Source:** user correction
- **Decision:** The primary purpose of the guideline is to prevent repeated
  project problems. Every real problem must feed `07-problems/` and produce a
  principle/pattern/module/card/rule patch when the same mechanism recurs.
- **Consequences:**
  - new problems are deduplicated against existing problems/cases;
  - a recurrence (≥2) requires a guideline change before closure;
  - project-specific numbers stay in the private rule pack.

---

## D-016 — Class-A reference is a layout-realization exercise, not a signoff target

- **Status:** active
- **Date:** 2026-10-26
- **Owner:** analog design + layout
- **Source:** user direction + class-A reference review
- **Decision:** The 16-MOS class-A reference (`examples/classa_opamp/`) is used to
  exercise layout intent: merged/interdigitated arrays, shared DM, flexible array
  rows, stepped DNW, outer M14 DNW, guarded R/C inside DNW1, and effective-area
  accounting. It is **not** a DRC/LVS/PEX signoff layout. `sd_mode=shared` is a
  temporary mode; the matching rule's "avoid shared S/D" remains a future
  decision.
- **Consequences:**
  - gate pitch is `L+0.36 µm` in shared mode; ring gap 0.8 µm; group gap 2 µm;
  - dummy fingers use the same geometry as active fingers; only the external
    `DM` label differs; no fake `FILL DM` padding;
  - NW/PW are simplified outlines, not extracted wells;
  - effective area = MOS ring outer (inner + ring AA) + guarded R/C ring outer;
    max area = rectangular bbox enclosing all DNW outer boundaries;
    rendered baseline is 17,845 µm² / 73.7%; selected area-first candidate is
    15,766 µm² / 74.6% at 225.9×69.8 (AR 3.24); other local/parasitic checks
    remain open;
  - no DRC/LVS claims; no full CT ring.
- **Related:** `examples/classa_opamp/README.md`, `examples/classa_opamp/area-min.png`, `examples/classa_opamp/area-min.svg`, `CURRENT_TASK.md`.
