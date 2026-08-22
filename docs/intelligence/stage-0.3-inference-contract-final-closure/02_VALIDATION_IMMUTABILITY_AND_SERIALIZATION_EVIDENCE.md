# Validation, Immutability, and Serialization Evidence

## Exact bounds

| Value | Implemented bound |
|---|---|
| `schema_version` | exact integer `1`; booleans rejected |
| `correlation_id` | 1–128 characters |
| `request_id` | 1–128 characters |
| `input_reference` | `None` or 1–512 characters |
| `context_references` | 0–32 values |
| each context reference | 1–512 characters |
| `timeout_ms` | 1–300,000 inclusive |
| `output_schema_ref` | 1–256 characters |
| `provider_id`, `model_id` | `None` or 1–128 characters |
| `duration_ms` | 0–300,000 inclusive |
| `failure_detail` | `None` or 1–1,024 characters |
| `warnings` | 0–16 values |
| each warning code | 1–64 characters; `[a-z][a-z0-9_]{0,63}` |

Bounded identifier/reference validation rejects blank values and ASCII control
characters. Unsupported schema versions fail closed.

## JSON policy and immutable snapshot

`input_payload` and successful `structured_output` require a top-level mapping
with string keys. Recursion permits only null, exact booleans, integers, finite
floats, strings, mappings, and list/tuple sequences. Bytes, arbitrary objects,
non-string keys, NaN, and infinities are rejected.

Each mapping/sequence has at most 256 direct members; maximum container depth
is 16; compact deterministic UTF-8 JSON is limited to 1,048,576 bytes.

Every accepted mapping is defensively copied into a fresh
`MappingProxyType`; list/tuple sequences are defensively copied into tuples.
Frozen slotted dataclasses prevent field replacement and instance dictionaries.
Caller mutation cannot change constructed request/result snapshots.

## Serialization

Both contracts expose explicit `to_dict()` and `from_dict()` methods.
Serialization preserves stable field names, integer schema version, optional
`None`, enum string values, and converts mapping proxies/tuples into JSON
objects/arrays. Deserialization reconstructs immutable validated snapshots.
Missing fields, unknown fields, invalid enum values, and unsupported versions
fail closed. No pickle, provider-native wire object, implicit object serializer,
or executable schema mechanism exists.
