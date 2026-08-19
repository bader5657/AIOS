# Authority, Baseline, Classification, and Scope

## Authority trace

This approval is controlled by the Blueprint, Frozen Roadmap, Authority
Hierarchy, Canonical Model, Layer Architecture, Core Platform Execution Plan,
and the accepted closures for Stages 3, 5, 6, 7, 8.1.1–8.1.4, 8.2.1, and
8.3.1.

The active Execution Plan row is:

`8.4.1 Test storage, metadata, manifest, registry, dispatch, and Core-boundary failures`

Its objective is approved-pipeline resilience verification, with no new
capability. Its required output is a failure matrix and passing tests.

## Exact scope

- Verification baseline: `2d2b31610fad7c2f5407ef8302146bf4378a7744`
- Work: test-only, no-op runtime verification
- Runtime files: `NONE`
- Authorized test: `tests/integration/core_platform/test_stage8_failure_matrix.py`
- New infrastructure: `NONE`

Receive failure, RequestContext construction failure, and Telegram
acknowledgement-send failure are not mandatory Stage 8.4.1 cases. Existing
Stage 8.2.1 and earlier evidence may be referenced without expanding this
scope.
