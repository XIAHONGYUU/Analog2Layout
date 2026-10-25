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

## D-007 — This workspace is an evolving concept workspace, not a production landing

- **Status:** active
- **Date:** 2026-10-25
- **Owner:** project
- **Source:** user direction
- **Decision:** Analog2Layout exists to develop and communicate the workflow: some parts are
  runnable, some are still conceptual, and the workspace will keep evolving. It
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
