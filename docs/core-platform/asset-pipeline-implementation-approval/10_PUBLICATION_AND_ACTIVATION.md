# Publication and Activation

| Control | Value |
|---|---|
| Publication mechanism | Governance package merged to `main` |
| Activation mechanism | Clean PR review and normal merge |
| Active scope | Exact three runtime and five test paths only |
| Implementation effect | Authorized only after activation |

## Activation Conditions

- the PR changes only this governance package;
- baseline and REPLACE disposition remain traceable;
- no unresolved review or required failing check exists;
- no runtime, test, schema, dependency, prior authority, Registry, or PostgreSQL
  file changes in the governance PR; and
- normal merge policy is used without bypass.

Upon merge, this package is Published and Active. It authorizes the separate
implementation branch to change only the exact paths and behavior recorded
here. It does not itself implement Asset Pipeline or complete Stage 4.2/4.3.

**ASSET PIPELINE IMPLEMENTATION APPROVAL: APPROVED — PUBLISHED — ACTIVE**

**READY TO BUILD WITHIN CLOSED SCOPE**
