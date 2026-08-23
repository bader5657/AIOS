# Scope, Policy Impact, Project Owner Approval, and Next Action

## Expected dependency direction and policy impact

The frozen direction is:

`Telegram/application ingress → Universal Ingestion → Event/Core route → exact CoreRouteResult → application continuation → CoreToBrainMapper → BrainInput → injected async Brain boundary → InferenceResult`

It is never `AIOSCore → Brain implementation`.

A typed callable expressed directly in Universal Ingestion would require these
future narrow source/target edges:

- `core/ingestion/universal_ingestion.py → core.core_to_brain_mapper`;
- `core/ingestion/universal_ingestion.py → core.brain.input_contracts`, limited
  to `BrainInput` typing/contract use; and
- `core/ingestion/universal_ingestion.py → core.brain.inference_contracts`,
  limited to `InferenceResult` typing/contract use.

No edge to Receiver, Invoker, provider, Ollama adapter, Memory, Specialist, or
business modules is approved. The existing Stage 8 default-deny audit and the
Stage 0.14 reverse-dependency audit currently reject the two Brain-contract
edges. A later implementation approval must explicitly authorize the exact
contract-only expansion and include exact policy changes; it must not silently
weaken either audit.

The likely smallest future scope is:

1. `core/ingestion/universal_ingestion.py`;
2. one focused runtime-wiring test path, preferably the existing
   `tests/unit/core_platform/test_universal_ingestion.py` if bounded coverage is
   clear; and
3. the exact policy tests
   `tests/unit/core_platform/test_stage8_import_boundaries.py` and
   `tests/unit/brain/test_inference_contracts.py` if the typed edges above are
   selected.

A new protocol/type production path is disfavored and may be approved only if
fresh evaluation proves the typed callable cannot preserve clarity or policy.
These are candidate paths for evaluation, not implementation authority.

## Project Owner approval

I, as Project Owner, approve the following Stage 0.16 runtime-wiring boundary
decisions:

1. correlation ID originates once at application ingress and is preserved;
2. application/ingestion orchestration owns provider-neutral projection;
3. provenance is bounded, opaque, authoritative, and never dereferenced;
4. exact `InferenceResult` returns unchanged and causes no business action;
5. `AIOSCore` remains unaware of Brain implementation;
6. Universal Ingestion/application orchestration owns continuation after Core;
7. continuation is native async;
8. Mapper and Brain boundary dependency are externally assembled/injected;
9. schema binding and production composition precede activation, not Level A;
10. Stage 0.16 proceeds first as inactive Level A repository wiring only;
11. real Telegram/production/business semantic inference remains unauthorized;
    and
12. retry, fallback, persistence, Memory, Specialist routing, and business
    action remain prohibited.

No runtime implementation or activation occurs in this package. Architecture
meaning remains unchanged; the potential port is a narrow dependency seam, not
a new layer.

## Remaining blockers and next action

The former ownership decisions are resolved. Exact implementation paths and
the policy expansion are intentionally pending one fresh Runtime Wiring
Boundary Evaluation / Implementation-Approval decision. Before Level B, exact
runtime semantic fields, schema binding, and staging composition remain
separate blockers.

The next official action is to rerun the Stage 0.16 wiring boundary evaluation
against these frozen decisions and, if the candidate four-path Level A scope is
confirmed, create a bounded Runtime Wiring Implementation Approval. No wiring,
inference, production activation, or temporary-asset cleanup is authorized.
