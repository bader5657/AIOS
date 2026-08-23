# Validation, Immutability, and Failure Rules

## Scalar and reference validation

- `schema_version` must be exact integer `1`; Boolean and other versions fail;
- `correlation_id` and `request_id` must be actual non-blank strings of 1–128
  characters;
- `input_reference` is `None` or an actual non-blank string of 1–512
  characters;
- identifiers and references preserve whitespace but reject whitespace-only
  values, U+0000–U+001F, and U+007F;
- no value is coerced, stripped, regenerated, repaired, or defaulted beyond the
  declared optional-field defaults;
- list or tuple input is accepted for `context_references`, defensively copied
  to a tuple, limited to 32 entries, with each entry validated as a 1–512
  character reference.

## Data validation

`data` must be a top-level mapping with string keys. Empty `{}` is valid.
Nested values may contain only `None`, exact Boolean, exact integer, finite
exact float, string, string-keyed mappings, and list/tuple sequences. Bytes,
sets, arbitrary objects, enum values, non-string keys, NaN, and infinities are
rejected.

The top-level mapping counts as depth 1. Maximum nesting is 16; every mapping
or sequence has at most 256 direct members. A detached plain JSON rendering
using compact separators, `ensure_ascii=False`, `allow_nan=False`, and UTF-8
encoding must not exceed 1,048,576 bytes. This rendering is validation only
and creates no public serialization API.

## Recursive immutability

Construction makes a defensive recursive snapshot. Mappings become fresh
`MappingProxyType` values over fresh dictionaries; list/tuple values become
tuples; allowed scalars remain scalars. Caller containers are not retained.
Together with frozen/slotted dataclass semantics, no field or nested container
can be mutated and no instance `__dict__` exists.

## Constructor, serialization, and failures

The generated explicit dataclass constructor rejects unknown named fields. No
`**kwargs`, dynamic field container, `to_dict`, `from_dict`, JSON wire form,
logging, or persistence method is authorized.

Wrong types raise `TypeError`; invalid values raise `ValueError`. No new error
hierarchy and no provider `FailureCode` are used. Construction must be
side-effect free. Future mapper/receiver failures remain separately governed
and must fail before inference with zero provider requests.
