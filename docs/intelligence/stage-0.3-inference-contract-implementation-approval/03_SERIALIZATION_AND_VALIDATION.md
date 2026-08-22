# Serialization and Validation Contract

## Wire API

Both dataclasses must expose:

- `to_dict() -> dict[str, object]`; and
- `@classmethod from_dict(cls, value: Mapping[str, object])`.

`to_dict()` returns a fresh, mutable, JSON-compatible tree containing every
declared field, including optional fields as `None` and empty tuple fields as
JSON arrays. Enums serialize to their lowercase string values; tuples and
mapping proxies serialize to arrays and objects; `schema_version` remains the
integer `1`. The returned tree must be directly accepted by
`json.dumps(..., allow_nan=False)` and mutation of it cannot mutate the DTO.
Field names are exactly the approved Python field names. No pickle, implicit
dataclass dump, provider-native encoding, or alternate wire aliases exist.

`from_dict()` requires a mapping, requires the exact complete declared field
set, rejects missing or unknown fields, parses enum values from their exact
wire strings, rejects unsupported schema versions, and reconstructs the
approved immutable representation. It does not coerce strings, numbers,
booleans, enum objects, or general iterables into another type. Constructor and
deserializer failures use `TypeError` for wrong Python types and `ValueError`
for invalid values/invariants.

## Request validation ownership

The constructor and `from_dict()` enforce required/optional field presence,
exact schema version, exact enum membership, identifier/reference bounds,
JSON policy, immutable snapshot, timeout range, and output-schema-reference
shape. `output_schema_ref` is an opaque approved identifier only: Stage 0.3
performs no registry lookup, schema loading, dereference, or executable schema
validation. A future authorized inference implementation owns lookup of the
approved local schema and validation of output against it.

## Result validation ownership and invariants

`success` must be an exact boolean. Impossible states fail construction:

- success: `success is True`, `failure_code is None`, `structured_output` is a
  present mapping, and both non-null `provider_id` and `model_id` are required;
- failure: `success is False`, `failure_code` is present,
  `structured_output is None`; provider/model identifiers may independently be
  `None` when their boundary was not reached.

Successful `{}` structured output is present and valid at the DTO level. The
contract guarantees only bounded JSON-compatible structure; the future
inference execution layer must establish conformance to `output_schema_ref`
before constructing success. Partial or malformed content therefore cannot be
represented as success: it must become failure with
`FailureCode.MALFORMED_OUTPUT`, discard content, and set
`structured_output=None`.

Duration and optional metadata use the exact bounds in this package.
`failure_detail` validation is structural only (optional, string, bounded,
non-blank, no control characters); semantic sanitization and prevention of
secrets, prompts, outputs, credentials, or business/user content remain the
caller/adapter responsibility. Contract validation does not implement secret
detection.

## Field exclusion

The dataclass fields and wire keys are closed. Consequently deadline,
provider/model configuration, token/cost data, raw provider response, retry,
tools/functions/tool results, session, persistence, Memory, Specialist, and
business/completion state are absent and rejected as unknown wire fields.
