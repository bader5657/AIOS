# Transaction and Recovery Evidence

The verified transaction model is:

Storage independent → Metadata independent → Manifest locally atomic → one
Registry-local SQL transaction → Registry commit → Event Engine → successful
Event completion → AIOS Core.

No SQL transaction spans Event Engine or AIOS Core. No distributed transaction
or distributed rollback exists. Event and Core failure leave the committed
Registry row visible and intact.

`RETRY = NONE`: no Storage, Registry, handler, Event publication, Core Route,
reroute, acknowledgement, or backoff retry exists.

`COMPENSATION = NONE`: no completed artifact deletion, Registry reversal,
Event compensation, or cross-component compensation exists.

`DEDUPLICATION / IDEMPOTENCY = NONE`: no idempotency key, failure ledger,
processed-event cache, route ledger, or duplicate suppression exists.
