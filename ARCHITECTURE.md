# Analog2Layout architecture

This document defines the target architecture for layout-intent work. It is
deliberately independent of the current LDO details.

## 1. Goal

Make every layout artifact:

```text
reproducible
single-source
single-writer
freeze-aware
verifiable
```

The architecture must prevent the known failure modes:

- two generators overwriting the same image;
- a downstream stage changing an upstream cell;
- a frozen artifact being consumed from an unfrozen source;
- a preview disagrees with its manifest/report;
- a stale file being mistaken for the current baseline;
- a prompt or skill describing an older workflow.

## 2. Layers

| layer | responsibility | may write |
| --- | --- | --- |
| L0 source facts | netlist, PDK facts, owner decisions | no geometry |
| L1 design spec | frozen inputs: members, W/L, match, dummy, ring, ports | no geometry |
| L2 model | deterministic geometry/coordinates/layers | no file rendering |
| L3 generators | spec + model → SVG/PNG/JSON/report | one named output |
| L4 validators | rule checks, geometry checks, hash/freshness | reports only |
| L5 assembly | frozen macros → DNW/module placement | assembly artifacts |
| L6 routing | frozen assembly → routing | routing artifacts |

Dependency direction is one-way:

```text
L0 → L1 → L2 → L3 → L4 → L5 → L6
```

A downstream layer must not silently recompute an upstream layer.

## 3. Non-negotiable invariants

1. **One output, one writer.** A path is claimed by exactly one producer.
2. **One canonical input per artifact.** Generated output never becomes an
   implicit input for another generator without an explicit spec.
3. **Frozen is immutable.** A change creates a new version and hash.
4. **Downstream reads frozen only.** Assembly cannot consume `draft` or
   `exploratory`.
5. **Exploration is quarantined.** `*-study/` or `out/`; never beside the
   baseline without a state label.
6. **A preview is an artifact.** It has a versioned name and a hash.
7. **A check is code, not a claim.** Selected-rule reports are computed from
   geometry; no hand-written `True`.
8. **A prompt routes to one stage.** It does not carry every rule from every
   stage.

## 4. Code skeleton

The first enforceable layer is implemented in:

```text
a2l/layout/contracts.py
```

It provides:

```text
Stage
State
Artifact
ArtifactRegistry
DuplicateWriterError
FreezeError
```

Enforced now:

- duplicate writer on one path is rejected;
- a frozen artifact needs a sha256;
- `verified_selected_rules` needs a checker;
- downstream cannot consume a non-frozen artifact;
- stage order is forward-only;
- a frozen artifact cannot be downgraded to draft.

The current LDO scripts are **not yet migrated** to this API. Migration is a
separate phase; do not pretend the old scripts already obey it.

## 5. Target repository shape

```text
a2l/layout/
  contracts.py        artifact/stage/freeze guardrails
  model.py            shared geometry primitives
  checks.py           geometry/rule validators

examples/<design>/
  spec/               L1 design inputs (owner-approved)
  primitives/         L2/L3 golden cells
  banks/              L3 generated bank artifacts
  assembly/           L5 frozen-macro assembly
  studies/            exploratory only
  ARTIFACTS.md        generated/indexed status
```

## 6. Migration sequence

Do not do a big-bang refactor. Move in this order:

1. **Guardrails** — contracts + tests + prompt/skill routing (this change).
2. **LDO input split** — separate netlist facts, owner decisions, derived
   geometry; no rendering changes.
3. **Shared primitives** — extract MOS/R/C primitives used by all generators.
4. **One writer per bank** — remove the duplicate NMOS generator.
5. **Assembly** — consume only frozen bank macros.
6. **Retire** obsolete scripts into `studies/` or delete after a reviewed
   snapshot.

Each step must keep existing tests green and add one regression test for the
failure it removes.

## 7. Current phase

```text
architecture guardrails: this change
LDO details: frozen/paused unless required by migration
DNW1 assembly: paused
```

The LDO-specific data cleanup is intentionally deferred.
