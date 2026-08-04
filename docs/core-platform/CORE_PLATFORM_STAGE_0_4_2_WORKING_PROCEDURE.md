# Core Platform Stage 0.4.2 Working Procedure

## Record

| Field | Value |
|---|---|
| Status | **APPROVED — ACTIVE** |
| Approval authority | Project Owner |
| Target branch | `main` |
| Source baseline | `1d261faa87806a506a93d2b333c03f2786725753` |
| Scope | Stage 3.1.3 Tasks A → B → C only |

## Procedure

For each authorized task:

1. confirm that the accepted authority and governance baseline is an ancestor
   of the current `main` HEAD;
2. inspect the existing source and focused tests without changing excluded
   artifacts;
3. implement only the current task within the scoped Change Request;
4. add or update only focused unit tests required by that task;
5. run focused verification and the applicable repository-root regression
   command;
6. record the exact diff, commands, results, and boundary checks;
7. stop before the next task for explicit Project Owner review;
8. after approval, accept the reviewed task change into `main` history; and
9. begin the next task only from that accepted baseline.

Review is distinct from approval. Approval is distinct from acceptance into
history. A failed test, scope expansion, authority conflict, or missing
contract stops the current task without inference.

No PR tooling, reviewer count, merge strategy, branch-protection rule, or
release procedure is created by this scoped procedure. For this scope,
acceptance means an approved commit recorded on target branch `main`.

## Verification Requirements

- Preserve task order A → B → C.
- Identify the exact pre-change and post-change commits.
- Confirm no excluded artifact changed.
- Preserve unrelated working-tree content.
- Do not represent unaccepted source as current baseline.
- Do not advance roadmap, release, milestone, or version status.

## Lifecycle

| Stage | Evidence |
|---|---|
| Draft | Procedure prepared from GD-003, GD-007, and the scoped Change Request. |
| Proposed | Submitted for Stage 0.4.2 review. |
| Reviewed | Procedure reviewed with the scoped request; review result PASS. |
| Approved | Explicit Project Owner instruction approves this procedure. |
| Published | Accepted into repository history. |
| Active | Current working procedure for Stage 3.1.3 Tasks A → B → C. |
