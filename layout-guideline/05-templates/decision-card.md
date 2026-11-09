# Decision Card — D-xxx

Copy this card for every design decision that changes structure, geometry, or
acceptance. A decision is not a fact and not a derived value.

```text
id: D-xxx
stage: A0 | A1 | A2 | A3 | A4 | A5
layer: L1 semantic | L2 structure | L3 primitive/array | L4 placement | L5 acceptance
question:
options:
  - option A:
  - option B:
chosen:
why:
evidence:
  - source:
  - confidence:
type: hard | soft | free
applies_to:
owner:
status: proposed | confirmed | superseded
supersedes:
linked_artifacts:
kernel_candidate: K-xxx
```

## Rules

- `hard` cannot be traded away; `soft` can be balanced; `free` may be chosen by
  an algorithm.
- A decision without `why` and `evidence` is a proposal, not a confirmed rule.
- A confirmed decision that changes geometry requires a new artifact version.
- Do not hide a decision inside a generator script; link it here.
