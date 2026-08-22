# Failure, Cancellation, State, Boundary, and Rollback

## Exact failure mapping

| Condition | Existing `FailureCode` |
|---|---|
| capability mismatch, payload failure, schema-ref resolution failure | `INVALID_REQUEST` |
| `httpx` connect/DNS/socket failure before reaching the approved local runtime | `RUNTIME_UNAVAILABLE` |
| effective async operation timeout | `TIMEOUT` |
| non-success HTTP, provider error, model mismatch, incomplete `done` state, or other execution failure without narrower evidence | `PROVIDER_FAILURE` |
| malformed/oversized envelope, missing/invalid content, content JSON failure/non-object, or independent schema mismatch | `MALFORMED_OUTPUT` |
| future injected approved policy rejection only | `POLICY_DENIED` |
| explicitly typed/positively identified approved runtime resource rejection only | `RESOURCE_LIMIT` |

V1 adds no policy seam and invents no resource/error-body heuristic. Therefore
ordinary HTTP status/error text maps to `PROVIDER_FAILURE`, not
`POLICY_DENIED` or `RESOURCE_LIMIT`. The latter codes remain reachable only
under later explicit authority or a transport signal whose exact semantics are
separately approved and tested.

All provider/httpx/JSON/schema exceptions are contained as sanitized failed
`InferenceResult` values under the narrowest approved mapping. No exception
detail may contain endpoint, request, instruction, data, schema, output, raw
body, credential, or business/user content.

Caller `asyncio.CancelledError` is the sole control-flow exception: it
propagates normally, is not translated, and triggers no follow-on work.

## Retry, state, logging, and lifecycle

- retry and fallback: `NONE`; exactly one POST maximum;
- persistence/cache/history/session/embedding/conversation: `NONE`;
- logging: only correlation ID, request ID, provider ID, model ID, bounded
  duration, success/failure, and failure code;
- content logging: prohibited; and
- runtime lifecycle: adapter must not start/stop Ollama, download/preload a
  model, manage containers/network/firewall/filesystem, or alter resource
  limits.

## Architecture, Core, and Brain boundary

Core remains unchanged at `AIOS_BRAIN_BOUNDARY`. Core must not import the
provider abstraction or adapter; the adapter must not import Core. The adapter
is independently constructible and testable and is not wired into any live
Brain orchestration, service, production path, or business flow.

`ARCHITECTURE CHANGE REQUIRED = NO`

## Dependencies, resources, and rollback

No dependency may be added; use pinned `httpx==0.28.1` and the standard
library. Adapter overhead must remain negligible. Existing Ollama ceilings
remain `3 GiB`, `1 vCPU`, concurrency `1`, approved disk, model, and runtime.

Rollback is repository-only revert/removal of the exact three authorized
paths. It requires no database or staging-runtime rollback.

Stop immediately and return for authority if implementation needs a fourth
path, new dependency, Core change, Brain orchestration, canonical contract
change, full schema registry, provider persistence, dynamic routing, public/
production endpoint, runtime mutation, or live inference.
