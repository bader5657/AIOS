# Duplicate and Idempotency Audit

Registering the same callable twice creates two ordinary registration entries
and two attempts in their positions. Processing the same envelope twice through
two explicit calls creates two independent in-memory invocations.

No deduplication, suppression, processed-event cache, event-ID cache, ledger,
inbox, idempotency key/store, or exactly-once machinery exists. This behavior is
not a distributed delivery guarantee.
