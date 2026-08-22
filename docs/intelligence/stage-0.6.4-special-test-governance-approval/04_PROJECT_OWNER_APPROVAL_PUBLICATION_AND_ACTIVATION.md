# Project Owner Approval, Publication, and Activation

## Project Owner approval

I, as Project Owner, authorize exactly one timeout test, one malformed-output
containment test, and one unload/recovery observation for Intelligence Stage
0.6.4.

The tests must remain synthetic, isolated, bounded by the existing `3 GiB` RAM
/ `1 vCPU` / concurrency-`1` controls, and must not affect production services.

No production authority or Brain integration is granted.

## Publication and activation

Activation requires review and merge of this exact governance package from
branch `governance/intelligence-stage-0.6.4-special-test-approval`. Before the
single timeout request, the operator must confirm the merged authority and
complete the fresh safety preflight.

After activation, authority is exhausted when the exact sequence in this
package completes or any stop condition occurs, whichever comes first. It does
not authorize inference during governance review, any additional normal
request, a second special case, or remediation.

## Remaining blockers and next action

There is no governance-design blocker. Controlled execution remains blocked
until this package is reviewed and merged and the fresh safety preflight
passes.

Next operator action after activation:

`Execute the exact controlled sequence: fresh safety preflight; one 1 ms timeout test; safety post-check; one malformed-output containment test; safety post-check; unload/recovery observation; and final production/resource state capture. Stop on any approved stop condition and return all evidence for final Stage 0.6.4 classification.`

`STAGE 0.6.4 SPECIAL TESTS APPROVED — READY FOR CONTROLLED EXECUTION`
