# Ownership and Authoritative Sequence

`Universal Ingestion = SOLE RequestContext constructor`.

The authorized sequence is:

`Telegram Update` → adapter transport validation/message extraction → original
Telegram `Message` delegated unchanged → existing Universal Ingestion
`ingest_telegram_message(message, context)` → recognition → exactly one
`RequestContext.from_telegram(...)` call by Universal Ingestion.

Stage 8.1.1 evidence ends with correct RequestContext construction/delegation.
Registry, Event Engine, and AIOS Core must be faked or bounded out of the focused
test and cannot be claimed as Stage 8.1.1 completion evidence.

The Telegram Adapter owns only receipt, minimum validation, preserved existing
command/special-case exclusion, delegation, and authorized transport response.
It owns no classification, RequestContext, storage, metadata, Manifest,
Registry, Event Engine, AIOS Core, or business semantics. Dependency direction
remains Telegram Adapter → Universal Ingestion. Domain Foundation, Registry,
Event Engine, and AIOS Core must not depend on the Telegram Adapter.
