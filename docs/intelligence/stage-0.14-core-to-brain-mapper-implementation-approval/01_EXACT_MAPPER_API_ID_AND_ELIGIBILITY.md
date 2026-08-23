# Exact Mapper API, Identifier, and Eligibility Contract

## Class and constructor

The exact class is `CoreToBrainMapper` in `core/core_to_brain_mapper.py`. It is
the neutral Core-to-Brain integration boundary and has one optional dependency:

`request_id_factory: Callable[[], uuid.UUID] = uuid.uuid4`

The implementation may use a repository-conformant equivalent signature, but
the factory contract and behavior may not change. A non-callable factory raises
`TypeError`. Construction never calls the factory.

## Public method

Expose one synchronous, pure `map(...) -> BrainInput` method with keyword-only
arguments where practical:

- `route_result: CoreRouteResult`;
- `correlation_id: str`;
- `data: Mapping[str, object]`;
- `input_reference: str | None = None`; and
- `context_references: tuple[str, ...] = ()`.

There is no caller-supplied request ID or intent, and no prompt, instruction,
timeout, schema, provider, model, envelope, context, or runtime argument.

## Exact Core eligibility

The route result must be an exact `CoreRouteResult` instance satisfying all:

- `success is True`;
- `route_target is CoreRouteTarget.AIOS_BRAIN_BOUNDARY`;
- `failure_code is None`; and
- `failure_reason is None`.

A wrong route-result type raises `TypeError`. Every other route-result state
raises `ValueError` before BrainInput construction. Eligibility is neither
normalized nor partially accepted. No request ID is generated for an
ineligible result.

## Identifier ownership

The originating caller owns `correlation_id`; the mapper passes the exact value
unchanged to BrainInput. It does not trim, normalize, regenerate, or substitute
the value. BrainInput remains authoritative for its validation.

The mapper exclusively generates one request ID for each eligible mapping
attempt. The factory is called exactly once and must return a UUIDv4. Any
non-UUID or non-v4 result raises `ValueError` before BrainInput construction.
The exact format is:

`brain-<uuid.UUID.hex>`

The prefix is exactly `brain-`; the UUID portion is 32 lowercase hexadecimal
characters without hyphens. It contains no provider or model semantics.
