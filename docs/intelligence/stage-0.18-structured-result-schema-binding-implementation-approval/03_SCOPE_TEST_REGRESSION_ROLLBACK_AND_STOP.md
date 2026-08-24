# Scope, Tests, Regression, Rollback, and Stop

## Exact two-path authority

1. `core/brain/schema_binding.py`;
2. `tests/unit/brain/test_schema_binding.py`.

The focused test module must cover all 50 Project Owner controls: exact
one-reference resolver vocabulary; deterministic recursive immutability; exact
schema contents without length/provider keywords; valid normal, empty, and
Unicode results; no input mutation and None success; wrong reference/value
types; missing/extra fields; all non-string result types; no coercion/repair;
and static standard-library-only dependency and side-effect exclusions.

After implementation run focused Stage 0.18; Stage 0.17 projection; Stage 0.16
wiring; Stage 0.15 integration; Stage 0.14 Mapper; BrainInput, Receiver,
Invoker, adapter mocks, and inference contracts; Core and Domain regressions;
Stage 8 and Stage 9; full repository; compile/static; dependency/import and
prohibited-source audits; `git diff --check`; and exact two-path closed-world
audit. No live inference is permitted.

Stage 8 must pass unchanged. Stop and request scope expansion if implementation
requires a third path, provider or receiver modification, generalized registry,
new dependency, Stage 8 policy update, runtime/composition change, live
inference, or Level B activation.

Rollback removes/reverts only the exact two implementation paths and has no VPS
or runtime operation.
