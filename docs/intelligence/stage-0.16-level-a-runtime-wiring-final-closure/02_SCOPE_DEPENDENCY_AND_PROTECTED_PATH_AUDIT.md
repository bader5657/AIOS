# Scope, Dependency, and Protected-Path Audit

The exact implementation diff is:

1. `core/ingestion/universal_ingestion.py`;
2. `tests/unit/core_platform/test_universal_ingestion.py`;
3. `tests/unit/core_platform/test_stage8_import_boundaries.py`; and
4. `tests/unit/brain/test_inference_contracts.py`.

AIOSCore, EventEngine, EventEnvelope schema, RequestContext,
CoreToBrainMapper, BrainInput, BrainSemanticReceiver, BrainInferenceInvoker,
provider abstraction and implementations, Ollama adapter, Telegram startup,
service/deployment files, and dependencies are unchanged from the corrected
approval baseline.

The Stage 8 policy permits only the exact Universal Ingestion runtime Mapper
edge and exact BrainInput/InferenceResult contract type edges. Default-deny is
retained. The reverse-dependency policy retains the Stage 0.14 Mapper exception
and adds only the exact type-only Universal Ingestion contract exceptions.
There is no broad Core-to-Brain allowlist and no Receiver, Invoker, provider,
Ollama, or httpx edge from Universal Ingestion.

Reviewer inspection found no unresolved activation, routing, provider,
side-effect, retry, fallback, logging, persistence, or scope violation. The
historical literal boundary compatibility adjustment remained inside the
authorized paths and did not weaken semantic import-policy enforcement.
