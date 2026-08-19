# Accepted Import Graph and Positive Edges

The accepted baseline graph includes:

- Adapter → Universal Ingestion;
- Adapter → Mission Status for the exact historical command path;
- Ingestion → Input Classifier and RequestContext;
- Ingestion → Asset Pipeline;
- Asset Pipeline → Telegram Storage, Metadata, and Document Manifest;
- Telegram Storage → File Storage;
- Ingestion → Registry;
- Ingestion → `DomainEvent` and `EventEnvelope`;
- Ingestion → Event Engine;
- Ingestion → AIOS Core;
- Event Engine → Domain Foundation `EventEnvelope`; and
- AIOS Core → Domain Foundation `EventEnvelope`.

The focused test may verify stable positive edges where they demonstrate the
active architecture. It must not require every implementation import merely
because a capability direction is permitted, and it must avoid brittle source
format or import-order assertions.
