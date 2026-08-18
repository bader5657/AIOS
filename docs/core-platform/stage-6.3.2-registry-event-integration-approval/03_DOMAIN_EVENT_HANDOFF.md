# DomainEvent Handoff

The only valid source is one already-produced `DomainEvent` explicitly handed
to `ingest_telegram_message` by its approved caller. The minimum backward-
compatible keyword input is:

```python
domain_event: DomainEvent | None = None
```

Universal Ingestion must not search arbitrary aggregates, call Event Exposure,
pull pending events, or manufacture a domain fact. `None` means no publication
attempt. One invocation accepts at most one DomainEvent; collections, pending-
event draining, batching, and multi-event semantics are not authorized.
