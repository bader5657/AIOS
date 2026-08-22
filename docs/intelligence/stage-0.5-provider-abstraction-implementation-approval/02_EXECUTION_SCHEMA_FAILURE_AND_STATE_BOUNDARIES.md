# Execution, Schema, Failure, and State Boundaries

## Result and schema ownership

Every future concrete provider implementation must ultimately return the
approved `InferenceResult`; provider-native response/error objects cannot
escape the adapter boundary.

The abstract module implements no execution, parsing, result construction,
schema lookup, schema registry, resolver, or validation framework. The frozen
future split remains:

- provider adapter parses/translates transient raw response;
- a separately approved provider-neutral validator resolves
  `output_schema_ref` and checks conformance; and
- after validation, the adapter constructs `InferenceResult`.

No `ProviderExecutionResult` is authorized.

## Failure and cancellation

The interface contract uses only the existing seven `FailureCode` semantics.
It creates no provider-specific exception type or failure taxonomy and
implements no failure mapping. Future adapters translate provider exceptions
into failed `InferenceResult` values under separate implementation authority.

Stage 0.5 adds no cancellation wrapper. Normal async caller cancellation
propagates and is neither swallowed nor converted into success/failure by the
abstract class.

## Timeout, retry, and persistence

Timeout authority remains solely `InferenceRequest.timeout_ms`. The interface
accepts no timeout override. Future adapters may shorten and never extend that
ceiling.

There are no retry fields, methods, helpers, backoff, fallback provider, or
fallback model. `PROVIDER RETRY = NONE` remains binding.

There are no state store, cache, session, history, embedding, conversation,
task, telemetry, or persistence fields/behaviors. `ProviderDescriptor` is
immutable metadata, not operational or lifecycle state.

## Descriptor closed field set

In addition to all undeclared fields, these are explicitly prohibited:

- `base_url`, endpoint, API key, credential, account ID, tenant;
- timeout, retry, concurrency, RAM/CPU/model-size controls, pricing;
- tool permissions, session, persistence, and mutable configuration; and
- provider/model selection or business metadata.

Runtime/configuration format, credentials, resource enforcement, provider
selection, and model selection remain separately governed.
