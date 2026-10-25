---
name: analog2layout
description: Use when working in the Analog2Layout workspace to parse device names/roles, estimate area from a rule pack, generate a floorplan sketch, compile a Layout Card, or plan layout-induced schematic deltas (dummy/decap/reserve) before PEX. Do not use for signoff DRC/LVS/PEX or for inventing PDK rules.
---

# Analog2Layout skill

## What this workspace does

It turns a name/role-annotated analog netlist into:

1. an explainable area report (`area_report.md/json`);
2. a floorplan sketch intent (`floorplan.svg/json`);
3. a layout-induced schematic delta manifest (`layout_delta.json`, `HANDOFF.md`);
4. a one-page Layout Card in `layout-guideline/02-modules/`.

The deterministic core lives in `a2l/`; the rule pack lives in `rules/`; the
examples live in `examples/`.

## Read first

1. `CURRENT_TASK.md` — the live task and next action.
2. `AGENTS.md` — hard boundaries and validation commands.
3. `docs/02-annotation.md` — role taxonomy and annotation fields.
4. `docs/03-area-model.md` — area formulas, if the task touches area.

## Standard workflow

```bash
# 1. Validate known roles and geometry
python3 -m a2l validate <netlist> --require-known-roles

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

Real simulation/verification netlists usually carry semantics only in instance
names. Names are the primary source; explicit parameters are an optional
confirmed override:

```spice
* name-only (common)
M1_DP n1 vinp ntail vss nmos w=5u l=0.5u nf=4 m=1

* optional override (confirmed by analog owner)
M1 n1 vinp ntail vss nmos w=5u l=0.5u nf=4 m=1 \
   role=input_pair match=DP group=IN layout=common_centroid
```

- `role` is optional; names like `M1_DP` / `M3_CM` / `M8_EN` are primary.
- `match`/`group` can be proposed from the name token.
- `layout` is an intent, not a legal layout pattern.
- If no token and topology is ambiguous, use `unknown`.

## Hard boundaries

- Never invent W/L, PDK numbers, DRC rules, or company rules.
- Never claim signoff accuracy. The output is an early planning estimate.
- Never auto-edit a schematic. Delta is a proposal; humans accept/reject it.
- Never commit proprietary PDK/company data.
- Keep the core dependency-free unless justified.
- If a role is uncertain, use `unknown` and say why.

## Technical checklist

- Does every device have a known role (name token or explicit override)?
- Does every critical device have a match group?
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
