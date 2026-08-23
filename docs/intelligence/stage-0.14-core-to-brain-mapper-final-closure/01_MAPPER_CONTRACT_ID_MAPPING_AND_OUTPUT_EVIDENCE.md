# Mapper Contract, Identifier, Mapping, and Output Evidence

`CoreToBrainMapper` exists in `core/core_to_brain_mapper.py` as the neutral
Core-to-Brain integration boundary. Its synchronous keyword-only `map(...)`
accepts exactly route evidence, originating correlation ID, provider-neutral
data, and optional opaque provenance. Its constructor has only an optional
callable UUID factory, defaulting to `uuid.uuid4`, and does not invoke it.

## Eligibility and identifiers

The mapper accepts only an exact `CoreRouteResult` whose state is precisely:

`(success is True, route_target is AIOS_BRAIN_BOUNDARY, failure_code is None, failure_reason is None)`

Wrong type raises `TypeError`; every ineligible state raises `ValueError`.
Eligibility is checked before UUID generation, so ineligible evidence consumes
no ID.

The originating correlation ID passes unchanged to BrainInput, with no
regeneration, trimming, lowercasing, or normalization. The mapper exclusively
calls its factory once per eligible attempt, requires an exact UUIDv4, and
formats the request ID as `brain-<uuid4.hex>`: 32 lowercase hexadecimal UUID
characters without internal hyphens. Callers cannot supply request ID or intent.

## Mapping and output

The mapper fixes `BrainIntent.STRUCTURED_INFERENCE`, passes semantic data
directly to BrainInput without enrichment or reinterpretation, and passes
`input_reference` and `context_references` as opaque references without lookup
or dereference. BrainInput remains authoritative for immutable snapshotting,
JSON compatibility, bounds, and validation.

It constructs and returns exactly one BrainInput with the accepted schema
version. There is no wrapper, EventEnvelope, RequestContext, CoreRouteResult
embedding, prompt, instruction, timeout, schema selection, provider/model
configuration, receiver call, invoker call, or inference.
