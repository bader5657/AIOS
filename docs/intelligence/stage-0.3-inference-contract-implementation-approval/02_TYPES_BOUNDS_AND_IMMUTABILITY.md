# Types, Bounds, and Recursive Immutability

## Exact scalar and collection bounds

All lengths are Python string character counts after requiring an actual
`str`; whitespace is preserved, but whitespace-only values fail where
non-empty identifiers are required.

| Value | Stage 0.3 bound |
|---|---|
| `schema_version` | exact integer `1`; `bool` rejected |
| `correlation_id` | 1–128 characters |
| `request_id` | 1–128 characters |
| `capability` | exact `InferenceCapability.STRUCTURED_INFERENCE` |
| `input_reference` | `None` or 1–512 characters |
| `context_references` | tuple of 0–32 references |
| each context reference | 1–512 characters |
| `timeout_ms` | integer 1–300,000 inclusive; `bool` rejected |
| `output_schema_ref` | 1–256 characters |
| `provider_id` | `None` or 1–128 characters |
| `model_id` | `None` or 1–128 characters |
| `duration_ms` | integer 0–300,000 inclusive; `bool` rejected |
| `failure_detail` | `None` or 1–1,024 characters |
| `warnings` | tuple of 0–16 codes |
| each warning code | 1–64 characters |

Opaque identifiers and references reject ASCII control characters U+0000
through U+001F and U+007F. Warning codes are machine-readable strings limited
to ASCII lowercase letters, digits, and underscore, must start with a letter,
and must match `[a-z][a-z0-9_]{0,63}`. This is structural authority for
bounded warnings, not a warning taxonomy or enum; an empty tuple remains the
default.

The timeout ceiling is provider-neutral and bounds one invocation. A future
runtime may enforce a shorter timeout and may not extend it. There is no
automatic retry. The duration bound is a DTO bound, not authority to exceed
the request timeout.

## JSON-compatible value policy

`input_payload` and non-null `structured_output` must each be a top-level
string-keyed mapping. Nested values may contain only:

- `None`;
- exact `bool`;
- exact `int` (excluding `bool`);
- finite exact `float` (NaN and infinities rejected);
- `str`;
- mappings whose keys are strings; and
- list/tuple sequences.

Bytes, bytearray, sets, non-string keys, arbitrary mapping/sequence or Python
objects, enum instances as payload values, and non-finite floats are rejected.
Every mapping or sequence may contain at most 256 direct members. Maximum
container nesting is 16 levels, counting the top-level mapping as level 1.
After conversion to plain JSON primitives using compact UTF-8 JSON, each
payload must be at most 1,048,576 bytes. `ensure_ascii=False` and
`allow_nan=False` define this size check; key sorting is not required for the
bound. This deliberately avoids a complex aggregate object-count algorithm.

## Immutable internal representation

Construction performs a defensive recursive snapshot:

- mappings become fresh `MappingProxyType` instances over fresh dictionaries;
- list/tuple sequences become tuples; and
- allowed scalar primitives remain scalar values.

Caller-owned containers are never retained. The same conversion is applied by
constructors and `from_dict()`. `context_references` and `warnings` are fresh
tuples. Frozen dataclasses plus slots prevent field replacement and instance
`__dict__`; mapping proxies and tuples prevent nested mutation.
