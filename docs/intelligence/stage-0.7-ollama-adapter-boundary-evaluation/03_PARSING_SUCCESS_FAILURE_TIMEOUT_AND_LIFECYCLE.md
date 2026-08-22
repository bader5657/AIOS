# Parsing, Success, Failure, Timeout, and Lifecycle

## Exact parsing sequence

1. Receive the non-streaming Ollama HTTP response.
2. Require a successful HTTP status and valid bounded response envelope.
3. Require matching configured `model`, `done is true`, and string
   `message.content`.
4. Extract `message.content` transiently.
5. Parse exactly one JSON object with bounded size/depth semantics.
6. Independently validate it against the approved schema resolved from
   `output_schema_ref`.
7. Construct one `InferenceResult` and discard all raw provider content.

## Success semantics

`success=True` is permitted only when provider execution completed, the
response envelope and JSON parsed, the output independently conforms to the
requested approved schema, provider/model identity is known and matches static
configuration, and `structured_output` is valid for `InferenceResult`.

Success means provider-boundary success only. It does not mean Brain decision,
business correctness, workflow completion, Specialist success, or production
success.

## Exact failure mapping

| Case | Existing `FailureCode` |
|---|---|
| unsupported capability, unknown schema ref, invalid adapter payload envelope | `INVALID_REQUEST` |
| connection refused/reset before execution, DNS/connect failure, runtime not reachable | `RUNTIME_UNAVAILABLE` |
| effective request deadline expires | `TIMEOUT` |
| non-success HTTP response, model missing/mismatch, incomplete response, provider/runtime error without narrower evidence | `PROVIDER_FAILURE` |
| invalid response envelope JSON, non-string content, content JSON failure, non-object output, schema mismatch | `MALFORMED_OUTPUT` |
| approved pre-invocation Brain/provider policy refuses execution | `POLICY_DENIED` |
| positively identified approved RAM/CPU/context/output/concurrency ceiling rejection | `RESOURCE_LIMIT` |

An HTTP status alone must not be guessed into `RESOURCE_LIMIT` or
`POLICY_DENIED`; those codes require explicit approved evidence. Provider
exceptions are sanitized into failed results. Raw provider error bodies never
cross the abstraction or enter logs.

## Benchmark limitation handling

The 20/21 limitation requires all three existing controls, not a hidden
reclassification:

- task/schema-specific Brain prompt construction clearly states bounded field
  semantics such as the `0.0–1.0` confidence scale;
- Ollama receives the approved schema through `format`; and
- AIOS independently validates and rejects any mismatch as
  `MALFORMED_OUTPUT`.

No coercion from percentages, repair, reinterpretation, retry, or success
downgrade is allowed. The invalid original cold result remains recorded.

## Timeout, cancellation, retry, and fallback

- timeout: enforce the effective minimum ceiling around the entire HTTP
  operation and response read; return `TIMEOUT` on expiry;
- cancellation: allow caller cancellation to propagate normally; do not catch
  or translate `asyncio.CancelledError` and do not perform work afterward;
- retry: `NONE`;
- provider/model fallback: `NONE`.

## Runtime health and model lifecycle

Do not call `/api/version` before every inference. A failed connection to the
single inference call is sufficient `RUNTIME_UNAVAILABLE` evidence and avoids
an extra race and roundtrip. Health/readiness probes, if later operationally
needed, belong to separately approved staging operations rather than
`infer()`.

Inference may trigger Ollama's normal single-model load. The adapter must not
preload at service boot, load another model, manage a model pool, or control
long-lived lifecycle beyond the approved `keep_alive: 5m` request setting.
