# Repeated Event and Idempotency Evidence

Processing the exact same EventEnvelope twice through two explicit calls
produces two independent in-memory attempts and one handler call per invocation.

`DEDUPLICATION = ABSENT` and `IDEMPOTENCY = NOT AUTHORIZED`. No event-ID cache,
processed-event set, ledger, inbox, key, store, or duplicate suppression exists.
This creates no exactly-once, at-least-once, or durable at-most-once guarantee.
