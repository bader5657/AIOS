# Happy Path and Test Harness

The primary focused case starts at `handle_update(...)` with fake Telegram
Update, Message, context, bot, and file/download doubles. A test-only wrapper at
the existing ingestion call boundary may supply the current Registry, Event
Engine, AIOS Core, one caller-owned DomainEvent, schema version, and controlled
storage behavior. Production Adapter construction of these dependencies is
prohibited.

The file-backed trace must prove:

`Receive → RequestContext → Asset Pipeline → Store Original → Metadata → Manifest → Registry transaction/COMMIT → EventEnvelope → Event Engine success → AIOS Core with the same envelope → AIOS_BRAIN_BOUNDARY readiness → IngestionResult return → Telegram acknowledgement`

RequestContext is constructed exactly once after receipt and before Asset
Pipeline. Storage precedes Metadata; Metadata precedes Manifest; completed
Manifest precedes Register; committed Registry state is independently visible
when the test-local async Event handler begins. Event success precedes exactly
one Core call. Route completes before Respond.

The DomainEvent is test-local, caller-supplied, and already approved. Registry,
Manifest, Metadata, and Adapter do not synthesize it. The real current AIOSCore
is used. The Event handler has no business or Brain semantics.
