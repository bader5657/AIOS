# Routing Identity, Input, and Immutability

The exact authoritative routing field is:

`EventEnvelope.event_name`

It is not a second vocabulary. Active Domain Foundation requires it to mirror
`EventEnvelope.event.event_name`, which is `DomainEvent.event_name`, exactly:
it is not independently supplied, generated, or normalized.

One Process invocation accepts exactly one `EventEnvelope` containing exactly
one `DomainEvent`. It does not accept a raw dictionary, Registry/PostgreSQL
row, Request Context, Manifest, original file, or business model.

Event Engine may validate envelope type/compatibility and read `event_name` for
routing. It must preserve the envelope, wrapped event, and every published
field unchanged. It must not reconstruct the event/envelope, enrich payload,
replace identity, normalize event name, generate timestamps, or create domain
facts.
