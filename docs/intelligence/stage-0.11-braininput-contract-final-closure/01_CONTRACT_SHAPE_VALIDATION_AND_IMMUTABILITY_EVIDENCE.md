# Contract Shape, Validation, and Immutability Evidence

## Exact contract

`BRAIN_INPUT_SCHEMA_VERSION == 1` is local to the Brain input contract.
`BrainIntent` is a string enum with exactly one member:

`STRUCTURED_INFERENCE = "structured_inference"`

`BrainInput` is a frozen, slotted dataclass with exactly these seven ordered
fields:

1. `schema_version`
2. `correlation_id`
3. `request_id`
4. `intent`
5. `data`
6. `input_reference`
7. `context_references`

## Validation evidence

- schema version requires exact integer `1` and rejects Boolean;
- correlation and request IDs are non-blank, at most 128 characters, and reject
  ASCII control characters;
- intent requires an exact `BrainIntent` instance; raw strings fail closed;
- data requires a top-level string-keyed JSON-compatible mapping and allows an
  empty mapping;
- NaN, infinities, binary/set/arbitrary values, and non-string keys fail;
- JSON container depth is at most 16, each direct container has at most 256
  members, and compact sorted UTF-8 validation representation is at most
  1,048,576 bytes;
- input reference is `None` or one opaque bounded reference; and
- list/tuple context inputs become a tuple of at most 32 bounded opaque
  references without deduplication or dereference.

Mappings are defensively copied into fresh `MappingProxyType` values and
sequences into tuples. Nested data is recursively immutable and detached from
caller-owned mutable input.
