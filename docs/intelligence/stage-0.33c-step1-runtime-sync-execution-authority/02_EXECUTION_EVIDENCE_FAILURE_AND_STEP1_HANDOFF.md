# Execution Evidence, Failure, and Step 1 Handoff

## Evidence contract

The future execution must retain one bounded, non-secret record outside the
source checkout. The frozen location is:

`/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/runtime-sync-evidence/`

This directory is not provisioned by this publication. Before activation, a
separate privileged filesystem decision must establish it as a real,
non-symlink `aiosadmin:aiosadmin` directory mode `0700`; each authority-bound
record must be created exclusively as mode `0600` and must fail on collision
(`O_EXCL`), never overwrite. If provisioning is not separately authorized or
safe metadata cannot be established, stop before authority consumption.

The record must include authority identity (this PR's eventual merge commit),
governance PR #266 and merge commit, this execution-authority PR/merge commit,
pre-sync SHA, target SHA, remote identity, pre-sync status, consumption
timestamp, exact mutation command, mutation result, post-sync SHA, module/import
results, callable assertion, DB contact `NO`, service PID/start identity before
and after, restart `NO`, post-sync status, rollback `YES/NO`, secret exposure
`NONE`, and Step 2 `NOT AUTHORIZED`. It must contain no secret values or source
payloads.

## Failure rules

- Any pre-mutation gate failure leaves authority `UNCONSUMED`, runtime source
  unchanged, and Step 1 OPEN.
- Once checkout mutation begins, authority is `CONSUMED` permanently.
- Post-mutation import, exact-SHA, worktree, or health failure permits only the
  one explicitly frozen rollback to the recorded pre-sync SHA; no forward retry.
- Import verification never calls the controlled candidate-create function and
  never opens a database connection.
- Service restart, filesystem provisioning, harness creation, input selection,
  first-write authority, candidate creation, and Step 2 remain unauthorized.

## Success and handoff

If exact prestate, target checkout, imports, callable assertion, clean worktree,
service health, secret safety, and durable evidence all pass, classify the
execution `STAGE 0.33C-P1S RUNTIME SOURCE SYNCHRONIZATION PASS`. This does not
automatically close Step 1: it makes Step 1 eligible for separate post-sync
closure review. Step 2 may begin only after that independent closure review.

Project Owner approval for this publication covers one future synchronization
attempt to the exact SHA only, after independent review/merge and all prestate
gates. It excludes restart, Step 2, filesystem provisioning for Step 2,
first-write authority, and candidate execution.
