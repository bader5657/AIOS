# Contract Ownership, Fields, and Validation

## Name, ownership, and location

The proposed name is `BrainInput`. It is a Brain-facing, non-canonical,
provider-neutral boundary DTO owned by AIOS Brain's receiving boundary. The
future repository location is:

`core/brain/input_contracts.py`

This uses the existing Brain package and creates no neutral architecture layer.
The type is a contract only, not Brain implementation behavior.

## Exact v1 field decision

Required fields:

1. `schema_version: int`
2. `correlation_id: str`
3. `request_id: str`
4. `intent: str`
5. `data: Mapping[str, object]`

Optional fields:

1. `input_reference: str | None = None`
2. `context_references: tuple[str, ...] = ()`

`instruction`, `timeout_ms`, and `output_schema_ref` are deliberately absent.
Provider/model/runtime configuration, `EventEnvelope`, `CoreRouteResult`,
Manifest, Registry rows, Memory, Specialists, and business objects are
prohibited.

## Bounds and validation

- `schema_version` is exact integer `1`; Boolean is rejected;
- identifiers and `intent` are non-blank strings of 1–128 characters;
- all strings reject ASCII control characters;
- `data` is a JSON-compatible mapping, at most 1,048,576 UTF-8 JSON bytes,
  recursively bounded to 16 container levels and 256 direct members;
- `input_reference`, when present, is 1–512 characters;
- `context_references` is an exact tuple with at most 32 strings, each 1–512
  characters;
- unknown top-level constructor fields are rejected; `data` keys remain semantic content subject to the mapping and size bounds;
- no coercion, trimming, default insertion, inference, or silent repair occurs.

`intent` is a bounded semantic task label/context, not provider prompt text or
a business command. A later approval must freeze any allowed intent vocabulary
before production use.

## Immutability and serialization

The future type must be frozen and slotted with recursive immutable snapshots:
mappings become read-only mappings and sequences become tuples. Caller mutation
must not change it.

V1 is in-process only. No `to_dict`/`from_dict`, wire protocol, persistence, or
transport serialization is approved. Deterministic validation remains fully
unit-testable. Wire semantics require separate evidence and authority.
