# Upstream Input Direction

The input must use the smallest already-authorized upstream representation.
`EventEnvelope` is the preferred candidate because it is canonical, immutable,
contains one approved DomainEvent, and is already accepted by Event Engine.

Event Engine success gates eligibility for Route. `EventDeliveryResult` remains
runtime-local upstream execution evidence and must not automatically become the
semantic routing payload. Stage 7.2.1 must decide whether EventEnvelope alone
is sufficient and finalize the exact input; this package does not.

Registry rows/connections, Storage, Manifest, wholesale Request Context,
business aggregates, and Specialist data are prohibited inputs.
