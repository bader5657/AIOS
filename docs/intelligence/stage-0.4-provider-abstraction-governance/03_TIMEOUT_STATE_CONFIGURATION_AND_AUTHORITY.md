# Timeout, State, Configuration, and Execution Authority

## Timeout and cancellation

Brain owns `InferenceRequest.timeout_ms`. A provider adapter may enforce a
shorter internal/configured timeout and must never extend the request timeout.
Timeout maps to `FailureCode.TIMEOUT`; it causes no retry.

Caller cancellation propagates normally through async cancellation. It is not
swallowed, translated into success, or followed by cancellation retry.

## Retry and persistence

`PROVIDER RETRY = NONE`.

No automatic retry, exponential backoff, fallback provider, or fallback model
is approved. Future retry/fallback requires separate authority.

The abstraction is stateless per invocation. It owns no prompt history,
response cache, session store, embedding state, task store, conversation state,
persisted telemetry, or provider-result persistence.

## Model and provider configuration

`MODEL SELECTION = STATIC CONFIGURATION ONLY` for the first runtime milestone.
One separately approved provider/model will be bound outside each
`InferenceRequest`. The abstraction performs no per-request override, dynamic
model selection, provider routing, or fallback.

Future separately approved runtime configuration may define:

- `provider_id`;
- `model_id`;
- runtime location/configuration;
- timeout ceiling; and
- operational/resource limits.

No configuration format is approved or implemented here.

## Credentials

Credentials are excluded from `InferenceRequest`, `InferenceResult`,
`ProviderDescriptor`, and `infer()` parameters. Future runtime/configuration
mechanisms may resolve credentials only under separate authority. Stage 0.4
defines no credential value, reference, source, secret store, or environment
variable.

## Network and local execution authority

The provider abstraction grants no network authority. `REMOTE` classification
does not permit outbound access. Remote execution requires separate
`OUTBOUND NETWORK / REMOTE PROVIDER APPROVAL`.

`LOCAL` classification grants no installation, model download, process
startup, or model invocation. Local-runtime activation requires separate
approval.

`OLLAMA = COMPATIBLE CANDIDATE / NOT SELECTED / NOT AUTHORIZED`.

The abstraction must be implementable without Ollama-specific imports or
types. It also remains compatible with generic remote providers without naming
or importing OpenAI, Anthropic, Gemini, or any provider SDK. No provider or
model is selected.
