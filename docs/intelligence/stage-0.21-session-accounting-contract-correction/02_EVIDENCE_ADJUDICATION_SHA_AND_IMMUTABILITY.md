# Evidence Adjudication, SHA Correction, and Immutability

## Immutable evidence identity

| Field | Value |
|---|---|
| Session ID | `stage-0.21-level-b-session-20260824T125420320720Z-e636371870544f708fd156721006561f` |
| Journal | `/opt/aios/runtime/intelligence/staging/level-b-sessions/stage-0.21-level-b-session-20260824T125420320720Z-e636371870544f708fd156721006561f.jsonl` |
| Verified SHA-256 | `4ef169dc774a5a6f65bfebf742af2a640314bac616253769317de4ee36de0835` |
| Historical final state | `FAILED_CLOSED` |
| Mutation authority | `NONE` |

The journal name, bytes, timestamps, metadata, events, and historical
`final_state` must remain unchanged. This governance record supplements the
history; it does not rewrite it.

A previously supplied expected digest used `4ef169dc7745...` rather than the
verified `4ef169dc774a...`. The discrepancy is classified
`GOVERNANCE_SHA_TRANSCRIPTION_ERROR`. The digest was independently recomputed
from the retained journal, so this is not an evidence-integrity failure.

## Technical evidence adjudication

The retained evidence establishes:

- one composition, AsyncClient, provider, invoker, receiver, and mapper
  lifecycle;
- two admitted synthetic requests in that same lifecycle;
- two projector, mapper, Brain, provider, and `/api/chat` calls;
- two distinct successful structured results with schema validation passing;
- request 2 spacing of `70.56281184998807` seconds, passing the frozen gate;
- request 1 latency of `68562.275 ms` and request 2 latency of `1709.708 ms`;
- zero retry, zero fallback, no third request, and deterministic cleanup; and
- preserved source, production, network, and runtime safety boundaries.

The latency change is observational evidence consistent with natural warm
reuse. Latency is not a functional pass criterion. Reuse is accepted because
both requests traversed the same single composition/provider lifecycle.

The incorrect finalized `mapper = 3` is exactly explained by adding the mapper
instance count of one to the mapper call count of two. It does not establish or
imply a third mapper, Brain, provider, or HTTP invocation. The accepted failure
classification is `NON_SEMANTIC_HARNESS_ACCOUNTING_VARIANCE`, with no semantic,
safety, provider, request-count, or runtime impact.

No duplicate live inference is technically required or authorized solely to
correct this accounting presentation.

