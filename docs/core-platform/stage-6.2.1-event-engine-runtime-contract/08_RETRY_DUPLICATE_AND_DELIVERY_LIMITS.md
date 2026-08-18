# Retry, Duplicate, and Delivery Limits

## Retry

**NO AUTOMATIC RETRY.** No loop, retry counter, maximum, backoff, reconnect, or
second handler attempt exists. Config claims `retry: true` and `max_retry: 3`
remain non-authoritative.

## Duplicate and idempotency

**DUPLICATE / IDEMPOTENCY POLICY = NOT AUTHORIZED.** There is no event
deduplication, idempotency-key storage, processed-event ledger, inbox, or
duplicate suppression.

## Truthful v1 guarantee

One in-process Process invocation attempts each matched handler snapshot entry
at most once during that invocation. This is not exactly-once, at-least-once,
durable at-most-once, acknowledgement, eventual delivery, or any distributed
delivery guarantee. Previously completed handler side effects are not
transactionally reversed if a later handler fails.
