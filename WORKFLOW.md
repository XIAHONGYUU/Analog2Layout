# Analog2Layout workflow

This is the stage/gate contract for layout-intent work. `AGENTS.md` holds durable
boundaries; `CURRENT_TASK.md` holds the live action. This file answers **how work
moves from a leaf cell to an assembled module without rework**.

## 0. Why this exists

The 2026-11-05 review found the main failure was not a missing algorithm. It was
starting the global layout before the leaf primitives were understood, then
reinterpreting the same requirement in several drawing iterations.

The repair is:

```text
requirements contract
→ one golden primitive
→ one approved bank
→ batch of banks
→ frozen macro registry
→ assembly
→ routing
```

Batch generation is allowed only **after** the template gate. A batch is not a
substitute for a template review.

## 1. Artifact states

Use exactly one state per artifact:

| state | meaning | may feed assembly? |
| --- | --- | --- |
| `exploratory` | sketch/study; may be discarded | no |
| `draft` | candidate geometry; still changing | no |
| `frozen_structural` | owner accepted structure; geometry locked | yes |
| `verified_selected_rules` | frozen + listed rule checks pass | yes |
| `superseded` | replaced; keep for history | no |

`frozen_structural` is **not** DRC/LVS/PEX signoff. Do not use "frozen" alone
when the rule checks are incomplete.

## 2. Gates

### G0 — Requirement card

Before drawing:

- goal and scope;
- members / W / L / m / match group;
- orientation (poly direction);
- dummy policy: where, size, orientation, count;
- ring/AA/well policy;
- required ports or explicitly "no metal/connections";
- size/area constraints;
- open questions and explicit assumptions.

No drawing starts with an unresolved high-cost requirement. A "temporary
default" must be written into the card.

### G1 — Golden primitive

Build **one** representative leaf:

- one MOS bank (smallest useful);
- one resistor group;
- one capacitor.

For each, deliver:

```text
SVG + PNG (versioned filename)
geometry JSON
selected-rule report
one-line change summary
sha256
```

Owner reviews the primitive, not a batch.

### G2 — One approved bank

Expand the primitive to one real bank. Freeze only when:

- structure meets G0;
- selected rule checks are listed and run;
- dimensions are recorded;
- preview is fresh (hash matches);
- open limitations are explicit.

### G3 — Batch

After G2:

- generate the remaining banks from the same primitive;
- each bank gets its own SVG/PNG/report;
- one batch review card;
- no silent template changes during the batch.

### G4 — Frozen macro registry

A bank may enter assembly only when it appears in `ARTIFACTS.md` with:

```text
name | version | state | owner | sha256 | verification command | open items
```

`bank-specs.json` is the machine source; the registry is the human index.
Do not keep independent status prose in several files.

### G5 — Assembly

Assembly consumes frozen macros only. It may not change a bank's internal
geometry. Any required bank change returns to G1/G2 and creates a new version.

### G6 — Routing

Only after the assembly baseline is frozen.

## 3. Change rules

- A frozen artifact is immutable. A change creates a new version and a new hash.
- Never overwrite a preview at the same path. Use
  `name-vYYYYMMDD-HHMM.png` and show the hash.
- Exploratory variants live in `*-study/` or `out/`; they never sit beside the
  baseline without a state label.
- Each freeze is followed by a small Git commit; do not accumulate a day of
  unreviewed changes.
- If a requirement changes, update the requirement card first, then the artifact.

## 4. Verification

Before presenting any artifact:

```text
1. regenerate from source;
2. compare output hash with the recorded hash;
3. run the listed selected-rule checks;
4. compare against the G0 checklist;
5. report what is verified vs inferred.
```

A stale preview is a release-blocking defect, not a display nuisance.

## 5. Current LDO application

```text
MOS bank library: draft (NMOS_2X0.5 has selected checks)
XR_GROUP: frozen_structural
XC1/XC3: draft, XC1 unit split unconfirmed
DNW1/DNW2 studies: exploratory, not assembly baselines
```

Next gate: G1/G2 for XC1/XC3, then remaining MOS banks.
