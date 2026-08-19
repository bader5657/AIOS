# Scope, Stop Rules, Project Owner Approval, Publication, and Activation

## Stop rules

Only `tests/integration/core_platform/test_stage8_failure_matrix.py` may be
created or modified during verification. Runtime files are unauthorized.

If another test path is required, stop with:

`STAGE 8.4.1 SCOPE EXPANSION REQUIRED`

If verification proves an active runtime-contract defect, do not patch runtime;
stop with:

`STAGE 8.4.1 RUNTIME CORRECTION APPROVAL REQUIRED`

The defect report must identify the failing assertion, violated authority,
implicated runtime path, and smallest correction candidate.

## Project Owner approval

The Project Owner approves:

- the exact mandatory Stage 8.4.1 failure matrix;
- one dedicated test file and zero runtime changes;
- disposable PostgreSQL execution;
- inclusion of unexpected Registry exception propagation;
- reuse of Stage 6 evidence for `INVALID_ENVELOPE`;
- current acknowledgement behavior after bounded Registry, Event, and Core
  failures;
- acknowledgement as receipt/readiness only, not end-to-end success;
- no retry, compensation, deduplication, cross-component transaction, or Brain;
  and
- separate runtime-correction approval if a real violation is proven.

Upon merge, this governance package is published and active with disposition:

`STAGE 8.4.1 FAILURE-VERIFICATION APPROVED — READY TO VERIFY`

It does not create the failure-matrix test, close Stage 8.4.1, or execute the
Stage 8 exit gate.
