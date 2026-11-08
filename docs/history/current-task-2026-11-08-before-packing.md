# 当前任务入口归档

来源：根目录 CURRENT_TASK.md；归档日期：2026-11-08。
以下保留归档前原文；其中路径按原仓库根目录理解，旧问题不代表重新开放已确认决定。

---

# CURRENT_TASK

## Goal

Maintain **Analog2Layout** as an evolving workspace for technical interaction
between analog and layout engineers: role/area → floorplan/white-line intent →
Layout Card → layout delta. This is not a production rule base, signoff tool,
training assistant, review service, or audit service.

## Current state (2026-11-03)

- The deterministic a2l core still works: name/role → five-level area → floorplan
  sketch → layout delta; **76 unittest tests pass**.
- The SKY130 1.8 V LDO is the primary system target. The SKY130 two-stage OP and
  the 16-MOS class-A case remain small reference/unit-test cases.
- The 16-MOS class-A reference is corrected from the upstream class-AB label:
  M13 is a PMOS current-source load; only M14 is signal-driven. Selected
  area-first render: **225.9 × 69.8 µm, 15,766 µm², 74.6%**.
- LDO semantic overlay is imported from `AnalogNetlistLabel` v0.2.0 commit
  `8cefac8`; source and hash provenance are in
  `examples/sky130_ldo_01v8/netlistlabel-overlay/provenance.json`. Overlay status
  remains **PROPOSAL, NOT APPROVED**; sampled review is not global accuracy.
- LDO white-line input:
  - `examples/sky130_ldo_01v8/white-line-input.json`;
  - 41 MOS + 5 passives + 2 level-shifter blackboxes + 9 logical groups;
  - `sd_mode=shared` user-confirmed; XC3/XR6 user-confirmed; x1/x2 are 5×5
    cell+ring placeholders;
  - resistor blocks are square folded/dummy blocks; `output_outer` is soft.
- LDO deterministic device-level compiler baseline:
  - `examples/sky130_ldo_01v8/make_white_line.py`;
  - bbox **129.20 × 110.70 µm**, area **14,302.4 µm²**, effective **11,961.0 µm²**,
    utilization **83.6%**, aspect **1.17**;
  - 41 devices, 12 bank clusters (11 MOS banks + XM61);
  - actual device arrays/fingers, shared boundary dummies only on matched
    clusters, per-bank rings, passive rings, x1/x2 placeholders, DNW1/DNW2;
  - outputs: `white-line.svg/png`, `white-line-manifest.json`.
- PDK facts source (2026-11-03):
  - `pdk/sky130/facts.json` has 13 traceable facts with DRC rule, line number,
    and deck sha256; `pdk/sky130/check.py` validates them;
  - reference deck: `out/refs/sky130.lydrc`, sha256
    `81cf4f998fc6fb6925ccc8618afba3dc8530058db1d0e31dc1f6ad5299e52372`;
  - **SKY130 does not define an “AA ring width = 1.0 µm” rule.** PDK defines
    minimum diff/tap/nwell/dnwell/contact width, space, and enclosure only.
  - ring/dummy dimensions are **layout heuristics**, not PDK facts:
    MOS bank ring 0.5/0.8; XM61 body ring 2.0/2.0; passive 1.0/0.8;
    DNW margin 2.0. `ring_audit.pdk_defined=false`.
- LDO matching review (2026-11-03):
  - `examples/sky130_ldo_01v8/matching-review.md`;
  - grouped by **same W/L + same device type** (NMOS/PMOS from SPICE model);
  - 12 matching banks; PMOS 20 devices, NMOS 21 devices;
  - same W/L is necessary but not sufficient; the owner must mark each bank
    `keep / split / add`;
  - **owner-confirmed 2026-11-04:** all 12 banks are mapped;
    `PMOS_1x0.5` is one large bank with XM86/XM88 as real edge switches;
    other banks follow the plan in `matching-review.md`;
  - MOS bank ring 0.5 / gap 0.8; XM61 uses six body-ringed sub-banks
    (W≈24.51 um/finger, 34 fingers each, total W=5000, 3×2) with shared ring
    walls and an outer DNW guard ring; passive ring 1.0 / 0.8; DNW margin 2.0;
  - dummy L=0.5, active L unchanged; separate drains, shared source only when
    identical;
  - DNW1 effective/main area = 2,893.8/4,507.7 = 64.2%; total effective
    utilization 85.9% includes the pass envelope, so it is not a main-module
    density number;
  - compiler now uses 11 bank clusters + the XM61 pass block; dummies are one strip per side where
    requested; XM61 has no edge dummy.
- The earlier A/B/C multi-agent LDO outputs were block-level estimates. They are
  exploratory only and are not the acceptance artifact.

## Bank-first workflow (2026-11-05)

- Stage/gate contract: `WORKFLOW.md`; human artifact index:
  `examples/sky130_ldo_01v8/ARTIFACTS.md`; freeze template:
  `layout-guideline/05-templates/freeze-record.md`.
- Golden-primitive gate before batching: one approved MOS/R/C primitive, then one
  bank, then the batch. Batch generation is not a template review.
- Stop global DNW1 packing until every bank macro is frozen.
- `examples/sky130_ldo_01v8/bank-specs.json` is the machine-readable bank contract;
  `bank-plan.md` is the human review table.
- DNW1 poly orientation is **vertical**; individual bank rotation is not allowed.
- Current bank status is `draft_frozen_geometry`; ports, S/D topology and global
  placement are still pending.
- Next: owner reviews the 12 bank macros, then freeze them before DNW1 assembly.

## Pause DNW1, bank/R-C detail first (2026-11-05)

- DNW1 area study and assembly are **paused/exploratory**, not a baseline.
- Current focus: resolve each bank's internal white-line content and the
  resistor/capacitor macros before any further DNW1 packing.
- The first-pass `banks/` library is useful for structure review, but only
  `NMOS_2X0.5_BANK` has a selected-rule report. Do not call the other banks
  DRC-clean.
- Bank-level drawings do not include S/D metal routes or global DNW polygons.

## Frozen R group (2026-11-05)

- `XR_GROUP` (XR4/XR5/XR6) is **frozen_for_now**: one common well, bbox 40×17 µm,
  stepped outline, 10 per-column long-edge dummies, AA only on the perimeter.
- Source: `examples/sky130_ldo_01v8/passive-banks/XR_GROUP_FROZEN.md` and
  `XR_GROUP_COMPACT2.png`.
- Freeze is structural only; no DRC/LVS signoff.

## Architecture hardening (current)

- Target architecture: `ARCHITECTURE.md`; executable guardrails:
  `a2l/layout/contracts.py` + `tests/test_layout_contracts.py`.
- Enforced now: one writer per path, freeze requires a hash, downstream cannot
  consume draft, frozen cannot be downgraded.
- The existing LDO scripts are **not yet migrated** to the contract API. Do not
  claim they already obey one-writer/freeze rules.
- Generic task prompt: `agent/prompts/layout_intent_task.md`.

## Next atomic action

1. Review `ARCHITECTURE.md` and the new guardrail tests.
2. Migrate LDO inputs in this order: source facts → owner decisions → derived
   geometry; no rendering changes in the first migration.
3. Then remove duplicate writers and extract shared MOS/R/C primitives.
4. Keep LDO-specific detail changes paused unless required by migration.

## Constraints

- Scope: workflow/demo/white-line intent; no production landing, no signoff.
- No complete PDK or company rule base is bundled. `pdk/sky130/facts.json` is a
  small traceable fact registry, not a DRC deck or a complete PDK.
- Do not claim DRC/LVS/PEX accuracy.
- Public repo contains generic/synthetic/desensitized content only.
- Do not auto-edit a schematic; delta is a proposal.
- Dummy fill must be real geometry, not fake area padding.
- Same W/L does not imply matching; matching requires an owner-confirmed match
  group.
- No remote push without explicit user instruction.

## Done when

- The LDO has an owner-confirmed matching map and an explicit ring/DNW policy.
- The LDO white-line has actual device arrays, shared dummies only on confirmed
  matched clusters, consistent per-well rings, passive rings, and DNW1/DNW2.
- The manifest and SVG agree on devices, rows/cols, area, and DNW gap.
- Tests/build remain green.
- No artifact presents a heuristic as a PDK fact or a block estimate as a
  device-level white-line.

## Open questions

- Which same-W/L banks are real matching groups, and which must be split?
- What ring width/gap and DNW enclosure margin should be used?
- Is the local-empty rule hard for matched arrays, and what is its exact
  interpretation (any-dimension vs area)?
- Is `sd_mode=shared` the default for all future matched arrays?
- Does the skill need to emit candidate SVGs, or only the selected one plus a
  manifest?
- Which rail-to-rail netlist should become the second area benchmark?
