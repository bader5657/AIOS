# Test Strategy, Project Owner Decisions, Blockers, and Next Action

## Future repository unit tests

Implementation approval should require deterministic tests using an injected
mock/fake HTTP transport and fake approved-schema validator. Unit tests must
not require live Ollama or network access and must prove:

1. exact descriptor identity, model, `LOCAL` kind, and sole capability;
2. `infer` remains async and executes one request only;
3. exact request translation, prompt boundary, endpoint, and body allowlist;
4. effective timeout propagation and no extension;
5. runtime-unreachable and HTTP/provider-failure mapping;
6. malformed response-envelope JSON and content JSON rejection;
7. independent schema-mismatch rejection;
8. valid structured output and exact provider/model metadata;
9. bounded monotonic duration;
10. raw response/error containment;
11. no persistence and no request/result history;
12. metadata-only logging with no content leakage;
13. no retry, fallback, second call, or health preflight;
14. normal cancellation propagation;
15. no Core reverse dependency;
16. no production configuration, service wiring, or Brain integration; and
17. no dependency or resource-ceiling expansion.

Tests must also cover unknown `output_schema_ref`, provider model mismatch,
`done != true`, non-object structured output, sanitized failure detail, and
the original benchmark-invalid confidence value mapping to
`MALFORMED_OUTPUT`.

## Separate live staging integration test

A later, separately authorized controlled test should prove exactly:

`InferenceRequest → OllamaInferenceProvider → Qwen → independently validated InferenceResult`

It must run from an approved isolated staging peer, use synthetic data,
concurrency `1`, existing ceilings, no retry/fallback, production safety checks,
and retained evidence. It must not be part of unit tests, contact production,
or silently reuse Stage 0.6.4 inference authority.

## Project Owner decisions required

Before implementation approval, the Project Owner must explicitly accept:

1. `core/brain/providers/ollama.py` and its organizational `providers/`
   subpackage;
2. frozen constructor-injected `OllamaProviderConfig` with external
   environment-backed composition and no adapter-owned environment reads;
3. existing `httpx.AsyncClient` async transport with no new dependency;
4. the injected provider-neutral approved-schema resolver/validator seam and
   initial static allowlist; and
5. standalone adapter implementation/unit tests first, followed by a separately
   authorized isolated live staging integration test before any Brain wiring.

These are implementation-boundary decisions only. Production activation is
not requested.

## Remaining blockers

- Stage 0.7 implementation approval must freeze exact source/test paths,
  payload envelope, validator interface and schema allowlist, HTTP/body limits,
  exception mapping, logging behavior, rollback, and stop conditions.
- Adapter implementation remains unauthorized until that approval is merged.
- Live staging integration requires separate execution authority after
  repository implementation and verification.
- Brain orchestration/wiring and every production action remain later,
  separately governed work.

None of these requires an architecture change. They are authority gates.

## Recommended next action

`Intelligence Stage 0.7 — Ollama Provider Adapter Implementation Approval`

That governance package should approve the five Project Owner decisions and
freeze an exact implementation/test contract. It must not itself implement the
adapter, execute inference, connect Brain, or alter staging/production.

`INTELLIGENCE STAGE 0.7 OLLAMA ADAPTER BOUNDARY IDENTIFIED — READY FOR GOVERNANCE APPROVAL`
