# Dependency Policy and Exact Scope

## Typed async boundary

`universal_ingestion.py` may define a local single-method Protocol named
`BrainBoundaryHandler` with one async call equivalent to:

`async __call__(brain_input: BrainInput) -> InferenceResult`

With `from __future__ import annotations`, `BrainInput` and `InferenceResult`
must be imported only under `TYPE_CHECKING`. Runtime construction or type checks
against Brain Receiver/provider classes are prohibited. The injected bound
`BrainSemanticReceiver.receive` method may satisfy this structural seam in a
future assembly, but Universal Ingestion never imports that class.

The Mapper object itself is injected explicitly for readable lifecycle and is
not reduced to an opaque mapping callable.

## Exact allowed new edges

Only these new source/target edges are approved:

1. runtime edge
   `core.ingestion.universal_ingestion → core.core_to_brain_mapper`, importing
   exactly `CoreToBrainMapper`;
2. `TYPE_CHECKING` contract edge
   `core.ingestion.universal_ingestion → core.brain.input_contracts`, importing
   exactly `BrainInput`; and
3. `TYPE_CHECKING` contract edge
   `core.ingestion.universal_ingestion → core.brain.inference_contracts`,
   importing exactly `InferenceResult`.

No import of Receiver, Invoker, provider abstraction/implementation, Ollama,
httpx, model/endpoint/configuration, schema resolver, Memory, Specialist, or
business modules is permitted.

## Exact four-path closed world

Implementation authority is limited to exactly:

1. `core/ingestion/universal_ingestion.py`;
2. `tests/unit/core_platform/test_universal_ingestion.py`;
3. `tests/unit/core_platform/test_stage8_import_boundaries.py`; and
4. `tests/unit/brain/test_inference_contracts.py`.

The two policy tests may change only to encode the exact three-edge exception
above while retaining default-deny for every other Core-to-Brain path. No new
protocol production file, `RequestContext`, EventEnvelope, AIOSCore, Mapper,
Brain contract/receiver/invoker/provider, adapter, service, dependency, config,
or production path is authorized.
