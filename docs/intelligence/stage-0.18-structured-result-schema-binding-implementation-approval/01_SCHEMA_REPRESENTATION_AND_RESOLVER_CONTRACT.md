# Schema Representation and Resolver Contract

Support exactly one reference:

`brain_structured_inference_result_v1`

It identifies exactly:

```json
{
  "type": "object",
  "properties": {
    "result": {
      "type": "string"
    }
  },
  "required": ["result"],
  "additionalProperties": false
}
```

Do not add minLength, maxLength, non-blank, trimming, or provider-specific
keywords. Empty result strings are valid. The existing structured-output JSON
size contract remains the sole result-size bound.

The authoritative schema must be recursively immutable using standard-library
`MappingProxyType` mappings and immutable tuple/frozen values where applicable.
Callers must be unable to mutate the top level, properties mapping, nested
result definition, or required collection. No DTO, generalized registry,
dynamic registration, wildcard, alias, or caller-supplied schema exists.

Implement:

`resolve_schema(schema_ref: str) -> Mapping[str, object]`

The resolver accepts an exact unmodified string. A non-string raises TypeError;
an unknown string raises ValueError. It returns the authoritative immutable
mapping deterministically and performs no trimming, normalization, copy-based
mutation exposure, or I/O.
