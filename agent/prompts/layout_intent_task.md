# Prompt: layout-intent task

Use this prompt for a bank, primitive, or assembly task. Fill the inputs before
sending.

```text
Task: <one stage/artifact only>
Stage: spec | primitive | bank | assembly | routing
Artifact: <exact id/path>
Inputs: <canonical spec paths only>
Owner decisions already frozen: <list or "none">
Open questions: <numbered, or "none">

Rules:
- Read ARCHITECTURE.md and WORKFLOW.md first.
- Identify the single producer for the artifact. If another generator writes the
  same path, stop and report the collision; do not overwrite.
- Keep the artifact at the requested stage. Do not change upstream geometry to
  make a downstream packing result easier.
- A preview must have a versioned filename, a sha256 and a fresh-generation
  check.
- A check must be computed from geometry. Do not hand-write PASS.
- If a requirement or source conflicts, list the evidence and stop for owner
  decision; do not silently choose.
- Do not claim DRC/LVS/PEX signoff.

Deliver:
1. current stage and artifact id;
2. exact generator command;
3. preview path + sha256;
4. check report path + result;
5. open limitations;
6. next gate; stop there.
```
