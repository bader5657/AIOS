# Authority, Architecture Compatibility, and Ownership

## Authority trace

- Frozen Roadmap: `Intelligence` is the post-Core Platform major phase;
- Blueprint: runtime architecture remains AIOS Core → AIOS Brain → Specialist
  Router → Specialists;
- Active Layer Architecture: Brain Layer exists; Intelligence Layer does not;
- accepted Core contract: `EventEnvelope` input and `AIOS_BRAIN_BOUNDARY`
  readiness remain unchanged;
- Stage 10 closure: Core Platform is completed and must not be reopened;
- Stage 0.1: Intelligence is the implementation/governance phase within the
  existing Brain architecture; inference is bounded and subordinate.

## Ownership

| Contract/boundary | Owner | Status | Explicit non-ownership |
|---|---|---|---|
| `InferenceRequest` | AIOS Brain | runtime-local, non-canonical | not AIOS Core, provider, domain/business, Memory, persistence |
| `InferenceResult` | AIOS Brain | runtime-local, non-canonical | not AIOS Core, provider-native response, business result |
| Provider adapter | future inference implementation | not selected/authorized | cannot own Brain orchestration or Core semantics |
| Core readiness | AIOS Core | accepted and unchanged | does not construct provider requests or interpret results |

Future approved package path:

`core/brain/inference_contracts.py`

Creating `core/brain/` as the Blueprint Brain implementation namespace does
not create a new architecture layer. The contracts must not be placed in
`core/aios_core/`, `core/intelligence/`, or a provider adapter package.

## Dependency direction

Future conceptual direction is Brain → inference contracts/provider
abstraction. Core Platform must not import Brain implementation. A provider
adapter may implement/consume the bounded inference contract but cannot depend
on AIOS Core to acquire semantic ownership or create a reverse Core dependency.

## Compatibility result

- new architecture layer: `NO`;
- new canonical object: `NO`;
- Core contract change: `NO`;
- Brain/Memory/Specialist/Business boundary change: `NO`;
- architecture change required: `NO`.
