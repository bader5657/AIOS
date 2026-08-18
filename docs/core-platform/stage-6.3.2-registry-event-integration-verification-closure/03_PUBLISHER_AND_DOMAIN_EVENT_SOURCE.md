# Publisher and DomainEvent Source Evidence

Universal Ingestion is the sole Stage 6.3.2 publisher. It accepts
`domain_event: DomainEvent | None = None` and at most one already-produced
Domain Foundation event from the approved caller.

No DomainEvent is constructed from a Registry row, `registry_record_id`,
Manifest path, metadata, storage path, source URL, registration status, or any
generic synthetic source. Registry, Asset Pipeline, Document Manifest, Event
Engine, and Domain Foundation publish nothing for this integration.
