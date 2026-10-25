---
name: analog2layout
description: Use when working in the analog2layout workspace to annotate analog devices by role, estimate area from a rule pack, generate or review a white-line floorplan, or plan layout-induced schematic deltas (dummy/decap/reserve) before PEX. Do not use for signoff DRC/LVS/PEX or for inventing PDK rules.
---

# analog2layout skill

## What this workspace does

It turns a role-annotated analog netlist into:

1. an explainable area report (`area_report.md/json`);
2. a white-line floorplan intent (`floorplan.svg/json`);
3. a layout-induced schematic delta manifest (`layout_delta.json`, `HANDOFF.md`).

The deterministic core lives in `a2l/`; the rule pack lives in `rules/`; the
examples live in `examples/`.

## Read first

1. `CURRENT_TASK.md` — the live task and next action.
2. `AGENTS.md` — hard boundaries and validation commands.
3. `docs/02-annotation.md` — role taxonomy and annotation fields.
4. `docs/03-area-model.md` — area formulas, if the task touches area.

## Standard workflow

```bash
# 1. Validate annotations and geometry
python3 -m a2l validate <netlist>

# 2. Build the full review bundle
python3 -m a2l build <netlist> --out <out-dir>

# 3. Compare architectures
python3 -m a2l compare <a.sp> <b.sp>

# 4. Inspect
#    <out-dir>/index.html
#    <out-dir>/floorplan.svg
#    <out-dir>/layout_delta.json
#    <out-dir>/HANDOFF.md
```

## Annotation contract

Use explicit device parameters whenever possible:

```spice
M1 n1 vinp ntail vss nmos w=5u l=0.5u nf=4 m=1 \
   role=input_pair match=DP group=IN layout=common_centroid
```

- `role` is required for reliable area/floorplan.
- `match` means electrical matching, not just functional grouping.
- `group` is a functional/floorplan block.
- `layout` is an intent, not a legal layout pattern.
- Names are only a fallback; do not rely on them as a long-term contract.

## Hard boundaries

- Never invent W/L, PDK numbers, DRC rules, or company rules.
- Never claim signoff accuracy. The output is an early planning estimate.
- Never auto-edit a schematic. Delta is a proposal; humans accept/reject it.
- Never commit proprietary PDK/company data.
- Keep the core dependency-free unless justified.
- If a role is uncertain, use `unknown` and say why.

## Review checklist

- Does every critical device have a role and a match group?
- Does the input pair straddle the symmetry axis?
- Are dummy/decap proposals visible and owned?
- Is the PEX-fix reserve present?
- Does the area report explain the dominant role?
- Are warnings acceptable or fixed?

## Output style

- Chinese docs, English identifiers/JSON keys.
- In the final response, show the primary artifact (SVG or HTML) and cite the
  exact files; do not just list paths.
- Report what was verified (tests, build) vs inferred.
