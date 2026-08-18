# Process Responsibility and Lifecycle

AIOS Event Engine is the bounded owner of the official lifecycle action
`Process` only.

Its minimum responsibility is to:

1. accept one approved bounded Event Engine input;
2. consume one already-constructed `EventEnvelope` carrying one `DomainEvent`;
3. validate the minimum boundary contract; and
4. produce a bounded event-delivery disposition toward the AIOS Core boundary.

Conceptual position:

`PostgreSQL Registry / bounded registered disposition`
→ `Integration/Application publisher boundary`
→ `AIOS Event Engine / Process`
→ `bounded event-delivery disposition`
→ `AIOS Core boundary`

This is capability order, not a direct Registry publisher call or runtime
dependency. Registry ends at persistence. Process does not own event creation,
business logic, Storage, Metadata, Document Manifest, Registry persistence,
Brain/Intelligence, Specialist Router, or subscriber business behavior.

For Stage 6.1.1, valid boundary input permits a bounded success disposition;
invalid boundary input permits a bounded failure disposition. These words
make no delivery-guarantee, dispatch, acknowledgement, retry, or handler claim.
