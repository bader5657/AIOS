# Execution, Result, Schema, and Failure Boundaries

## Minimum execution purpose

The complete conceptual flow is:

`InferenceRequest → InferenceProvider → bounded adapter execution → InferenceResult`

The abstraction neither transforms Brain intent into business semantics nor
owns Brain orchestration. One future configured adapter is bound to one future
approved provider/model outside each request.

## Result construction and schema validation

The provider adapter directly constructs the final validated
`InferenceResult`, after:

1. provider-specific execution;
2. transient response translation/parsing;
3. provider-neutral validation; and
4. output-schema conformance validation.

No intermediate canonical or provider-neutral `ProviderExecutionResult` DTO is
added because it would duplicate approved result semantics and expand the
provider-data surface.

Responsibility is split as follows:

- `InferenceRequest`/`InferenceResult`: contract-structure validation only;
- future provider-neutral validation layer: `output_schema_ref` resolution and
  parsed-result conformance validation; and
- provider adapter: provider-native response parsing/translation.

Stage 0.4 creates no schema registry, resolver implementation, executable
schema, or provider-specific schema object.

## Raw response containment

A raw provider response may exist only transiently inside adapter execution.
It is discarded after validated translation and must never enter
`InferenceResult`, persistence, default logs, AIOS Core, Registry, Memory, or a
canonical object.

## Exact failure mapping

Provider/runtime failures map only to the existing seven `FailureCode` values:

| Code | Approved mapping |
|---|---|
| `INVALID_REQUEST` | Request is incompatible with the configured adapter/provider contract. |
| `RUNTIME_UNAVAILABLE` | Required provider/runtime is unavailable before execution. |
| `TIMEOUT` | Effective inference timeout expires. |
| `PROVIDER_FAILURE` | Execution fails and no narrower approved classification applies. |
| `MALFORMED_OUTPUT` | Parsing or output-schema conformance fails. |
| `POLICY_DENIED` | Approved policy rejects execution before provider invocation. |
| `RESOURCE_LIMIT` | Approved resource ceiling prevents or terminates execution. |

No new failure code is approved. Provider-specific exceptions must be
translated into a failed `InferenceResult`; they cannot cross the abstraction
boundary. Caller cancellation is the sole control-flow exception and follows
normal async cancellation propagation.
