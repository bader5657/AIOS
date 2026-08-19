# Evidence Inventory and Ownership

## Accepted evidence

- **8.1.1:** Adapter constructs zero RequestContext objects; Universal Ingestion constructs exactly one; the original Telegram message is delegated; acknowledgement boundary is verified.
- **8.1.2:** the same RequestContext reaches Asset Pipeline; Store → Metadata → Manifest ordering is verified; Registry is outside this endpoint.
- **8.1.3:** real disposable PostgreSQL proves Registry COMMIT and independent row visibility before Event handling; DomainEvent is caller supplied; failures preserve upstream state.
- **8.1.4:** Event success alone gates one Core route call with the identical EventEnvelope; Event failure yields zero Core calls; endpoint is AIOS_BRAIN_BOUNDARY readiness.
- **8.2.1:** the Adapter-starting full lifecycle, owner matrix, real commit, Route-before-Respond ordering, file/text/URL paths, and representative failures are verified.
- **8.3.1:** prohibited reverse edges, import cycles, Brain, Memory, Specialist Router, and official business imports are zero; Psycopg remains Registry-local.
- **8.4.1:** all mandatory failures, suppression, preservation, component-local transaction boundaries, and false-success distinctions are verified.

## Authoritative ownership

| Action | Owner |
|---|---|
| Receive transport | Telegram Adapter |
| Receiving-side orchestration | Universal Ingestion |
| RequestContext | Universal Ingestion |
| Store Original | Storage capability |
| Extract Metadata | Metadata Engine |
| Create Manifest | Document Manifest capability |
| Register | PostgreSQL Registry |
| Process | Event Engine |
| Route | AIOS Core |
| Respond | Telegram Adapter |

Universal Ingestion coordinates bounded calls; orchestration does not transfer semantic ownership.

## Full lifecycle

`Receive → RequestContext → Asset Pipeline → Store Original where applicable → Metadata → Manifest → Registry → Registry COMMIT → Event Engine → AIOS Core → AIOS_BRAIN_BOUNDARY readiness → Respond`

`FULL LIFECYCLE ORDER = PASS`
