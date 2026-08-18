# Duplicate and Repeated-Invocation Contract

The active Stage 6.3.1 approval controls duplicate handler registration: each
valid registration appends one ordinary entry. Registering the exact same
callable twice creates two positions and one Process invocation attempts both
positions in registration order. No deduplication or handler-identity policy is
introduced.

Calling `process(the_same_envelope)` twice is two independent caller-initiated
in-memory invocations. Matching handlers may run once per invocation. This is
not exactly-once, at-least-once, durable at-most-once, acknowledgement, or any
distributed delivery guarantee.

`IDEMPOTENCY = NOT AUTHORIZED`. No event-ID cache, ledger, key, inbox, store, or
suppression mechanism may exist.
