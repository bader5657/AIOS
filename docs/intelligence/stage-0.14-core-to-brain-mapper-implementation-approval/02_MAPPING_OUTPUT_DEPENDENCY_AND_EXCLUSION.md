# Mapping, Output, Dependency, and Exclusion Contract

## Exact BrainInput construction

After eligibility and UUID validation, construct and return exactly one
`BrainInput` with:

- `schema_version=BRAIN_INPUT_SCHEMA_VERSION`;
- the unchanged caller `correlation_id`;
- the generated request ID;
- `intent=BrainIntent.STRUCTURED_INFERENCE`;
- the caller's `data` mapping;
- the supplied `input_reference`; and
- the supplied `context_references`.

The mapper performs no enrichment or business interpretation. BrainInput owns
the immutable snapshot, JSON compatibility, depth, member, encoded-size,
identifier, and reference validation. Empty data is accepted. Natural
BrainInput `TypeError` and `ValueError` exceptions are not caught or rewritten.

Provenance values are already-authoritative opaque strings. The mapper passes
them through without coercion, lookup, dereference, logging, or persistence.
Neither CoreRouteResult nor any routing state is embedded in data or
provenance. EventEnvelope and RequestContext are excluded from the API and
imports; callers may separately pass an authoritative opaque reference.

## Exact dependency boundary

The production mapper may import only:

- `CoreRouteResult` and `CoreRouteTarget` from their existing accepted Core
  contract module;
- `BRAIN_INPUT_SCHEMA_VERSION`, `BrainInput`, and `BrainIntent` from
  `core.brain.input_contracts`; and
- `uuid` and standard-library callable/mapping types as needed.

It must not import AIOSCore, EventEnvelope, RequestContext, ingestion, Event
Engine, Registry, Storage, adapters, BrainSemanticReceiver,
BrainInferenceInvoker, provider interfaces/adapters, httpx, runtime/config,
Memory, Specialist, or business/domain modules.

No Stage 8 allowlist expansion is authorized or expected because this neutral
boundary module is outside Stage 8 runtime pipeline roots. Verification must
confirm the existing Stage 8 gates pass. If they reject the two exact approved
edges, stop for narrow governance review rather than weakening policy.

## Side-effect and responsibility boundary

Local UUID generation is the sole allowed effect. Database, Registry, Storage,
filesystem, environment lookup, network, logging, persistence, receiver,
provider, inference, Memory, Specialist, and business action are absent.

The mapper owns Core eligibility, correlation preservation, request-ID
creation, static intent assignment, semantic data/provenance mapping, and
BrainInput construction. BrainSemanticReceiver continues to own instruction,
timeout, output-schema reference, and inference invocation. There is no overlap.
