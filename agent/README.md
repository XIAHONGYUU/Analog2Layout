# Agent layer

This directory is the **technical semantic layer** around the deterministic core.
It is not a training assistant, review service, or autonomous layout generator.

## Loop

```text
1. a2l validate / build
2. agent proposes role/match/group/layout
3. analog engineer confirms annotations
4. analog fills module-intent.yaml
5. agent compiles a one-page Layout Card
6. layout engineer reads the card, adds technical feedback
7. card / change log / case updated; version +1
```

## Prompts

| File | Purpose | Output |
| --- | --- | --- |
| [`prompts/annotate_roles.md`](prompts/annotate_roles.md) | infer device roles from topology/names/comments | annotation JSON |
| [`prompts/compile_layout_card.md`](prompts/compile_layout_card.md) | compile module intent + principles/patterns/cases into a one-page Layout Card | Markdown card |

## Guardrails

- The role taxonomy and rule values are owned by the analog design engineer/team. The agent may propose, not approve.
- The agent must not invent W/L, PDK numbers, DRC rules, or company rules.
- The agent compiles and links; it does not issue review verdicts or signoff.
- Every role proposal needs `confidence` and `evidence`.
- Uncertain devices must be `unknown`; a wrong confident label is worse than a gap.
- The agent may suggest a delta, but cannot change a schematic.
- All JSON must validate against [`schemas/`](../schemas/).
- The deterministic CLI remains the source of geometry/area numbers.

## Minimal integration

The prompts are plain Markdown so they can be used with any chat/agent runtime.
A future `a2l agent` command can call an LLM API, but v0.1 deliberately keeps the
core offline and auditable.
