# Verification, Regression, and Deferred Debt

| Gate | Result |
|---|---|
| Focused BrainInput | `67 passed` |
| Stage 0.3 inference contracts | `84 passed` |
| Stage 0.9 BrainInferenceInvoker | `23 passed` |
| Stage 0.7 adapter | `61 passed`; mocks only |
| Core regressions | `139 passed`; `31 skipped`; `252 subtests passed` |
| Domain regressions | `212 passed`; `454 subtests passed` |
| Stage 8 | `9 passed`; `12 skipped` |
| Stage 9 applicable repository gates | `PASS` |
| Full repository | `666 passed`; `58 skipped`; `727 subtests passed` |
| Compile/static | `PASS`; 103 Python files compiled in memory |
| Dependency/import audit | `PASS` |
| Prohibited-source audit | `PASS` |
| `git diff --check` | `PASS` |
| Closed-world diff | `PASS`; exactly two paths |

The three Domain collection warnings are pre-existing and unrelated. There are
no unresolved failures and no live inference in verification.

## Mapper debt

No mapper exists. A future mapper owns originating correlation-ID
preservation, one request-ID generation per handoff attempt, semantic intent
assignment, bounded data snapshot, opaque provenance references, and
`BrainInput` construction. It must not create prompts, select provider/model,
timeout, or output schema, or invoke inference.

## Brain receiver debt

No Brain receiver exists. A future receiver consumes `BrainInput`, owns static
intent policy and instruction/timeout/output-schema derivation, derives IDs
directly from the immutable input, applies equality/fail-before-inference
control, and calls the unchanged `BrainInferenceInvoker`.

Core wiring and production/outer composition remain unresolved and
unauthorized. Preserve the Stage 0.8 and Stage 0.10 temporary staging sources;
cleanup remains separately governed.
