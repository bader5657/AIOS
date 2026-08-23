# AIOS Intelligence Stage 0.15 — Repository Integration Test Implementation Approval

| Control | Approved value |
|---|---|
| Work type | `GOVERNANCE / TEST IMPLEMENTATION APPROVAL ONLY` |
| Approval baseline | `d5e2acce2c5c9b76e42d2bd84132401efba0592d` |
| Stage 0.14 | `CORE-TO-BRAIN MAPPER VERIFIED — ACCEPTED — CLOSED` |
| Authorized path | `tests/integration/test_core_to_brain_chain.py` |
| Authorized path count | exactly `1` |
| Production source changes | `NONE` |
| Architecture change | `NO` |
| Live inference / Core wiring | `PROHIBITED / NOT AUTHORIZED` |
| Decision | `APPROVED — READY TO BUILD` |

This package authorizes one repository-only integration test for:

`eligible CoreRouteResult → CoreToBrainMapper → BrainInput → BrainSemanticReceiver → BrainInferenceInvoker → fake InferenceProvider → InferenceResult`

The test must use the real mapper, BrainInput, receiver, and invoker. It creates
no production wiring, composition root, provider/runtime integration, service
lifecycle, or business behavior.

No second test/policy path, package export, production source, dependency, or
configuration change is authorized. Any such need stops implementation for
scope expansion.
