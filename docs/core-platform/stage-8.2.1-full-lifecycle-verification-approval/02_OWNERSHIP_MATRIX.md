# Authoritative Ownership Matrix

| Action | Execution owner | Integration/orchestration boundary |
|---|---|---|
| Receive | Telegram Adapter owns transport receipt | Universal Ingestion owns receiving-side acceptance |
| RequestContext | Universal Ingestion | Constructed once before Asset Pipeline |
| Store Original | Storage capability | Asset Pipeline requests storage where applicable |
| Extract Metadata | Metadata Engine | Asset Pipeline invokes it after applicable storage |
| Create Manifest | Document Manifest capability | Asset Pipeline invokes it after metadata |
| Register | PostgreSQL Registry | Universal Ingestion performs the bounded call |
| Process | Event Engine | Universal Ingestion gates it after Registry commit |
| Route | AIOS Core | Universal Ingestion gates it after Event success |
| Respond | Telegram Adapter, transport delivery only | Consumes Core Platform acknowledgement disposition |

The Adapter does not own ingestion semantics. Universal Ingestion orchestrates
but does not acquire Storage, Metadata, Manifest, Registry, Event Engine, or
AIOS Core semantics. Reverse ownership and later-phase execution are prohibited.
