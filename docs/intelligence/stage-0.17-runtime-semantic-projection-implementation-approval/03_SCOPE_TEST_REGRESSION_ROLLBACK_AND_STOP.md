# Scope, Tests, Regression, Rollback, and Stop

## Exact two-path authority

1. `core/ingestion/semantic_projection.py`;
2. `tests/unit/core_platform/test_semantic_projection.py`.

The test module must cover all 52 Project Owner controls: public API and exact
fresh shape; deterministic output; strict type and empty rejection; ordered
line-ending conversion and outer trimming; preservation of internal whitespace;
inclusive character and UTF-8 bounds; allowed TAB/LF and rejected controls;
Unicode preservation without normalization; and static exclusion of Telegram,
RequestContext, EventEnvelope, Mapper, Brain contracts/implementation,
provider, database, Registry, filesystem, network, environment/config, logging,
persistence, Memory, Specialist, and business dependencies.

After implementation, run focused Stage 0.17 tests; Stage 0.16 wiring;
Stage 0.15 integration; Stage 0.14 Mapper; Stage 0.11 BrainInput; Stage 0.12
Receiver; Stage 0.9 Invoker; Stage 0.7 adapter mocks; Stage 0.3 contracts; Core
and Domain regressions; Stage 8 and Stage 9; full repository; compile/static;
dependency/import and prohibited-source audits; `git diff --check`; and exact
two-path closed-world audit. No live inference is permitted.

Stage 8 policy must pass unchanged. The production module uses only the
standard library. If implementation requires a Stage 8 exception, third path,
Universal Ingestion or RequestContext change, EventEnvelope, Mapper, Brain
contract/implementation, new dependency, Telegram SDK, DB/network/filesystem,
secret scanner, live inference, or Level B activation, stop and request scope
expansion.

Rollback reverts only the exact two implementation paths and has no runtime or
VPS operation.
