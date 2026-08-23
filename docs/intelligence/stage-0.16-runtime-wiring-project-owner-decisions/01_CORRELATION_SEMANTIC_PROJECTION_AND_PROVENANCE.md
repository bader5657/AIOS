# Correlation, Semantic Projection, and Provenance Decisions

## Correlation identity

The application ingress/origination boundary owns one correlation ID for each
accepted inbound processing attempt. It generates the value exactly once with
the standard-library UUIDv4 source in this exact format:

`corr-<uuid4.hex>`

The value is provider-neutral, immutable after creation, no longer than 128
characters, and contains no Telegram, provider, model, or business semantics.
It flows unchanged through internal runtime context, semantic projection, Core
routing, Mapper, BrainInput, Receiver, Invoker, and InferenceResult. Mapper,
Receiver, provider, and business Domain must not generate or replace it.

This package freezes ownership and semantics only. It does not add a field to
`RequestContext`, alter `EventEnvelope`, or implement generation.

## Semantic projection

Application/Universal Ingestion orchestration owns the explicit semantic
projection before `CoreToBrainMapper`. The Mapper accepts an already-approved
provider-neutral `Mapping[str, object]` and does not derive it.

Level A authorizes synthetic repository-test semantics only, including the
minimal form:

`{"text": "synthetic normalized content"}`

No real Telegram, user, production, or business content is authorized.
RequestContext, Telegram objects, provider/model settings, instructions,
timeouts, schema names, route objects, database/session objects, and secrets
must not enter the mapping. Before Level B, a separate runtime semantic
projection authority must freeze the exact normalized fields allowed for every
eligible input class.

## Provenance

Application/ingestion orchestration supplies bounded opaque provenance strings;
the Mapper only forwards them.

- `input_reference` uses the stable logical asset/Manifest identifier when one
  is authoritatively available, otherwise a separately approved opaque ingress
  identifier. A filesystem path is prohibited when a stable logical ID exists.
- `context_references` defaults to `()` for Level A unless explicitly supplied
  by its caller as already-authoritative bounded identifiers.

Wiring and Mapper perform no Registry lookup, dereference, content embedding,
or provenance reconstruction.
