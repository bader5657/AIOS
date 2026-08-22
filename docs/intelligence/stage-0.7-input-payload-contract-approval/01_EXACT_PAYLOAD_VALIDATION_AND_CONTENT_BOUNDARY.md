# Exact Payload, Validation, and Content Boundary

## Closed top-level shape

`input_payload` must contain exactly the two top-level keys `instruction` and
`data`. Both are required. Missing or unknown keys fail closed as
`FailureCode.INVALID_REQUEST`; unknown keys are never ignored.

The following provider/native/configuration keys are consequently prohibited
at the top level: `model`, `messages`, `prompt`, `system`, `role`, `stream`,
`format`, `options`, `keep_alive`, `base_url`, `endpoint`, `temperature`,
`seed`, `num_ctx`, `num_predict`, `tools`, `functions`, `provider`, and
`credentials`. This list is explanatory, not an alternate allowlist: every key
other than `instruction` and `data` is rejected.

## Instruction

`instruction` is owned by Brain/request construction and represents one
bounded task instruction for one invocation. It must be:

- an exact Python string;
- between 1 and 4096 characters inclusive;
- non-empty and non-blank;
- already trimmed, meaning `value == value.strip()`; and
- subject to the existing JSON and total payload bounds.

Leading/trailing whitespace is rejected rather than silently normalized. This
preserves one canonical value for deterministic rendering.

The instruction grants no provider/system role, tool execution, credential,
persistence/session, Specialist, business-action, or automated-decision
authority. Brain applies content/security policy before request construction.
Structural validation cannot reliably detect every embedded secret or semantic
instruction, so this contract does not claim secret scanning; the adapter must
not add hidden intent or authority.

## Data

`data` is owned by Brain/request construction and must be a top-level mapping.
It remains JSON-compatible, recursively immutable, and bounded by the existing
Stage 0.3 policy: maximum depth/members and maximum 1 MiB serialized
`input_payload` representation.

An empty mapping is explicitly allowed. It supports valid instruction-only
structured inference without inventing placeholder data and remains
unambiguously represented as `{}`.

Nested JSON-compatible mappings and sequences are allowed. Data content grants
no provider configuration, model selection, timeout, schema, credential,
tool/function, session, persistence, Memory, or business-action authority.
Brain policy is responsible for excluding unauthorized sensitive/business
content before construction. Nested key names are treated as data rather than
provider controls; adapter configuration can only come from its separate
immutable configuration.

## Validation ownership

Payload-profile validation is an adapter-local private helper in the already
proposed `core/brain/providers/ollama.py`. It runs before schema resolution or
network execution and returns validated instruction/data values for rendering.
Keeping the helper local avoids a fourth production module or premature shared
payload registry. The existing `InferenceRequest` constructor continues to own
generic bounded JSON validation and immutability.

Invalid shape/type/bounds/prohibited top-level semantics map to
`FailureCode.INVALID_REQUEST`. Validation never coerces, trims, defaults,
repairs, or silently removes content.
