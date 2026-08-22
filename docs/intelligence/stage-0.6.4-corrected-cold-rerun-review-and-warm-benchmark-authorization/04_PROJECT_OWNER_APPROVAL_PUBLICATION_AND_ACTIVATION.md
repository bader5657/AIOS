# Project Owner Approval, Publication, and Activation

## Project Owner approval

I, as Project Owner, accept the corrected cold rerun as methodology-validation
evidence and retain the original cold result as an invalid official result.

I authorize exactly twenty official warm benchmark requests under the frozen
contract in this package. The requests must be sequential, monitored, and
safety-gated. This approval changes no schema, sampling setting, model,
runtime, resource ceiling, retry policy, fallback policy, production service,
or production integration.

This approval does not authorize inference during the governance task. It does
not authorize a timeout test, malformed-output test, unload test, production
inference, Brain/provider integration, deployment, restart, cleanup, or
remediation.

## Publication and activation

Activation requires review and merge of the prerequisite Stage 0.6.4 benchmark
approval, the cold methodology reconciliation, and this exact package. Before
the first warm request, the operator must confirm those merged commits and
pass the existing immediate read-only safety preflight.

After activation, authority is exhausted when twenty requests have been sent
or any early stop condition occurs, whichever comes first. Return the complete
warm evidence before seeking separate authority for the timeout,
malformed-output, or unload/recovery tests.

## Remaining blockers and next action

The governance decision is complete. Execution remains blocked until the
prerequisite and current governance PRs are reviewed and merged and the
immediate preflight passes.

Next operator action after activation:

`Execute exactly 20 controlled sequential warm requests, preserve all required evidence and monitoring, stop on any approved stop condition, and return the warm evidence for review without beginning any special or unload test.`

`STAGE 0.6.4 WARM BENCHMARK APPROVED — READY FOR 20 CONTROLLED WARM RUNS`
