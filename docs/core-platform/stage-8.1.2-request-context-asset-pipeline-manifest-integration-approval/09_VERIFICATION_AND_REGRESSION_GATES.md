# Verification and Regression Gates

Implementation acceptance requires:

| Gate | Required evidence |
|---|---|
| Focused Stage 8.1.2 | Exact one-file integration test; all cases pass |
| RequestContext handoff | Same object, one Pipeline call, zero reconstruction |
| Lifecycle | Store → Metadata → Manifest, exact call order |
| Mapping | Only received time and three optional Telegram contextual IDs |
| Leakage | No full context, username, source, or context-derived text |
| Failure containment | Storage bounded; Metadata/Manifest propagate; no later call |
| Readiness | True only after successful Manifest path |
| Registry | Zero execution and zero success claim |
| Retry/network | Absent |
| Asset Pipeline regression | `tests/unit/pipeline/test_asset_pipeline.py` unchanged and passing |
| Universal Ingestion/lifecycle | Existing ingestion and lifecycle tests unchanged and passing |
| Manifest | Existing Document Manifest tests unchanged and passing |
| RequestContext | Existing RequestContext tests unchanged and passing |
| Stage 8.1.1 | Existing focused integration evidence unchanged and passing |
| Core/Domain | Relevant Core regression and full Domain regression pass |
| Static/dependency | Compile, dependency, prohibited-source, and diff checks pass |
| Closed world | Diff contains exactly the one authorized test path |

Pre-existing baseline failures may be classified separately only after exact
clean-main fingerprint reproduction. The monolithic suite must not be
represented as fully green when it is not.
