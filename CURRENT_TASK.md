# CURRENT_TASK

## Goal

Maintain **Analog2Layout** as an **evolving workspace** for technical interaction
between analog and layout engineers: role/area → floorplan/white-line intent →
Layout Card → layout delta. This is not a production rule base, signoff tool,
training assistant, review service, or audit service.

## Current state (2026-10-26 end of day)

- The workspace still has the deterministic a2l core: name/role → five-level area
  → floorplan sketch → layout delta; 49 unittest tests pass.
- The SKY130 two-stage OP remains a **unit test** (10 MOS + 1 cap); the SKY130
  1.8 V LDO remains the **primary system target** but is **paused** while we
  finish the layout-realization exercise.
- A 16-MOS **class-A reference** was added from a real schematic/netlist
  (`examples/classa_opamp/`). Upstream calls it class-AB, but the netlist only
  drives M14; M13 is a PMOS current-source load. The target is corrected to
  class-A.
- User-defined sizing is recorded: W/L/m, M8/M9 = 108 (W=9, m=12), R1 2×3
  m=4, C1 5 pF MOM fixed 5×10 µm = 50 µm².
- White-line exercise (latest):
  - merged interdigitated arrays; shared DM at both ends; no fake `FILL DM`;
  - flexible array rows (2/4/6 preferred, other rows allowed);
  - `sd_mode=shared`; gate pitch **L+0.36 µm**; ring gap **0.8 µm**; group gap
    **2 µm**;
  - dummy fingers have the same finger geometry as active devices; only the
    external `DM` label differs;
  - input pair in the center row; PMOS upper / NMOS lower; M14 at the outer
    right in its own DNW; DNW1/DNW2 gap **8 µm**;
  - R/C placed between DNW1 and DNW2 and counted in area;
  - NW/PW shown as simplified well outlines;
  - no DRC/LVS or exact CT-ring drawing.
- Effective-area accounting (current number):
  - ring-inner effective area + R/C = **11,764 µm²**;
  - DNW1+DNW2 outer area = **15,965 µm²**;
  - utilization = **73.7%** by DNW sum; **67.7%** by total bbox; **81.6%** if
    ring metal is included.
- CT fit check: with 0.36 µm gate-to-gate S/D, one CT needs
  0.055+0.17+0.04 = 0.265 µm, so it fits; W > 5.7 µm needs multiple CT rows.
- Still open: exact NW/PW outlines, complete CT ring, top/bottom half-W dummy
  variant, exact R/C model footprint, and returning to the LDO white-line/card.
- Git: latest class-A white-line code plus this documentation update; CI green.

## Next atomic action

1. Tomorrow: deep review of the layout flow, not another incremental tweak.
2. Review the effective-area definition:
   - ring inner vs ring metal included;
   - DNW sum vs total bbox denominator;
   - whether R/C and routing inside the DNW gap count.
3. Decide whether the class-A exercise becomes the standard layout-reference case
   or remains a teaching target beside the LDO.
4. Then resume the LDO target: R/C/X area, 14-group floorplan, LDO white-line/card.

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

- Effective area: include ring metal or only ring interior?
- Denominator: sum of DNW outer areas or total DNW bounding box?
- Do we keep `sd_mode=shared` for the class-A reference, or switch to separated
  S/D for matched pairs later?
- Do we add top/bottom half-W dummies to the input pair, or keep the flattened
  left DNW?
- What is the next layout-review milestone: CT ring, NW/PW spacing, or LDO?
