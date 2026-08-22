# InferenceResult Contract

## Identity and purpose

`InferenceResult` is a Brain-owned, runtime-local, non-canonical,
provider-neutral result for exactly one bounded inference invocation. It does
not represent a Brain decision, transport response, persistence outcome, tool
action, Specialist result, or business completion.

It must be a frozen, slotted dataclass. Any nested structured output must be an
immutable snapshot after construction.

## Field disposition

| Field | Disposition | Approved semantics |
|---|---|---|
| `schema_version` | REQUIRED | positive integer; initial and sole accepted v1 value `1`; unsupported value fails closed |
| `correlation_id` | REQUIRED | exact request value |
| `request_id` | REQUIRED | exact request value |
| `success` | REQUIRED | boolean with exact invariants below |
| `failure_code` | REQUIRED field | `InferenceFailureCode` on failure; `None` on success |
| `structured_output` | REQUIRED field | recursively immutable bounded JSON-compatible mapping on success; `None` on failure |
| `provider_id` | REQUIRED field | bounded provider-neutral string when selected; `None` if failure precedes provider selection/execution |
| `model_id` | REQUIRED field | bounded approved model identifier when invoked; `None` if execution did not reach model invocation |
| `duration_ms` | REQUIRED | bounded non-negative integer measuring only this invocation boundary |
| `failure_detail` | OPTIONAL | nullable bounded sanitized string; no secrets, prompt/output, credentials, or full user/business content |
| `warnings` | OPTIONAL | immutable bounded tuple of machine-readable codes; default empty; non-empty taxonomy deferred |
| token metadata | DEFERRED | absent from v1 |
| cost metadata | DEFERRED | absent from v1 |
| raw provider response | PROHIBITED | provider-native content never enters result |
| tool/Specialist/Memory/business state | PROHIBITED | no downstream capability or completion semantics |

Exact maximum identifier/detail length, warning count, output depth/size, and
duration bound must be named by future implementation approval. Non-empty
warning values are not authorized until a warning taxonomy is separately
approved; v1 implementations may expose only the empty tuple.

## Success invariant

`success=True` means exactly one bounded inference invocation completed and
produced output conforming to the requested `output_schema_ref`.

On success:

- `failure_code is None`;
- `structured_output` is present and schema-conforming;
- `provider_id` and `model_id` are present; and
- no Brain acceptance or downstream completion is implied.

## Failure invariant

On failure:

- `success=False`;
- `failure_code` is present;
- `structured_output is None`;
- provider/model IDs are present only if their respective boundary was
  reached; and
- no false-success representation is permitted.

## Structured and raw output

Structured output is a bounded, recursively immutable, JSON-compatible mapping
validated against the approved schema reference. It contains no arbitrary
Python or executable object and no provider-native response object.

Raw provider content may exist transiently inside a future adapter solely for
validation/translation. It is discarded after translation/failure handling
and is prohibited from `InferenceResult`, default logs, persistence, and Core
Platform exposure.
