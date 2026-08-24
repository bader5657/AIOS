# Scope, Tests, Regression, and Rollback

## Exact four-path implementation authority

1. `core/ingestion/universal_ingestion.py`;
2. `tests/unit/core_platform/test_universal_ingestion.py`;
3. `tests/unit/core_platform/test_stage8_import_boundaries.py`; and
4. `tests/unit/brain/test_inference_contracts.py`.

The two policy paths may encode only the three exact dependency edges. The
default-deny policy remains intact; no broad ingestion-to-Brain allowlist is
authorized.

The existing Universal Ingestion test path must cover all 35 Project Owner
controls, including inactive defaults, one pre-envelope correlation, exact
format and propagation, one original envelope and route call, non-Brain zero
Mapper/Brain/request-ID behavior, exact eligible route and inputs, exact object
identities, incomplete configuration, complete exception/cancellation
propagation, and absence of retry, fallback, provider, automatic semantics,
persistence, and business action. Tests use fakes only.

After implementation, retain evidence for focused Stage 0.16 tests; Stage 0.15
integration; Stage 0.14 Mapper; Stage 0.11 BrainInput; Stage 0.12 Receiver;
Stage 0.9 Invoker; Stage 0.7 adapter mocks; Stage 0.3 contracts; Core and Domain
regressions; Stage 8 and Stage 9; the full suite; compile/static checks;
dependency/import and prohibited-source audits; `git diff --check`; and exact
four-path closed-world audit. No live inference is permitted.

Rollback reverts exactly the four implementation paths. Stop and request scope
expansion if implementation requires a fifth path, AIOSCore, EventEnvelope
schema, RequestContext, Mapper, Brain contract/implementation, startup,
composition, schema binding, provider/runtime dependency, live inference, or
real user/business semantic data.
