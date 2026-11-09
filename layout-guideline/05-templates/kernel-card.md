# Kernel Card — K-xxx

A kernel is the reusable part extracted from a concrete design decision. It must
not be a project-specific number without a scope.

```text
id: K-xxx
type: principle | pattern | decision-rule | invariant | anti-pattern | verification-recipe
statement:
scope:
conditions:
exceptions:
counterexample:
source: D-xxx | step | incident
evidence:
status: proposed | accepted | superseded
verification:
```

## Rules

- A kernel without `scope` or `conditions` is a slogan, not a rule.
- A kernel derived from one project is `proposed` until it survives a second
  structure or an owner review.
- If a kernel conflicts with a PDK fact, the PDK fact wins.
- Link the kernel to the decision(s) and the check/test that enforce it.
