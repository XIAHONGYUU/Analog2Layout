# Agent layer

This directory is the **semantic layer** around the deterministic core. It is not
an autonomous layout generator.

## Loop

```text
1. a2l validate / build
2. agent reads netlist + annotations, proposes role/match/group/layout
3. human reviews proposals, writes them back to the schematic/export
4. a2l build again
5. agent reviews floorplan.json + layout_delta.json against the rule pack
6. human accepts/rejects delta items
7. PEX feedback updates the rules and prompts
```

## Prompts

| File | Purpose | Output |
| --- | --- | --- |
| [`prompts/annotate_roles.md`](prompts/annotate_roles.md) | infer device roles from topology/names/comments | annotation JSON |
| [`prompts/review_floorplan.md`](prompts/review_floorplan.md) | review a white-line floorplan for matching/symmetry/isolation issues | review comments JSON |

## Guardrails

- The role taxonomy and rule values are owned by the analog design engineer/team. The agent may propose, not approve.
- The agent must not invent W/L, PDK numbers, DRC rules, or company rules.
- Every role proposal needs `confidence` and `evidence`.
- Uncertain devices must be `unknown`; a wrong confident label is worse than a gap.
- The agent may suggest a delta, but cannot change a schematic.
- All JSON must validate against [`schemas/`](../schemas/).
- The deterministic CLI remains the source of geometry/area numbers.

## Minimal integration

The prompts are plain Markdown so they can be used with any chat/agent runtime.
A future `a2l agent` command can call an LLM API, but v0.1 deliberately keeps the
core offline and auditable.
