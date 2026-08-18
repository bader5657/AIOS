# Call Count and No-Event Evidence

- Registry failure: zero Event Engine calls.
- Registry success with no DomainEvent: zero Event Engine calls.
- Registry success with one approved DomainEvent: exactly one Process call.

No batching, pending-event drain, fallback publication, or retry exists.
No-DomainEvent preserves successful registration and reports
`event_publication_attempted=False`, `event_delivery_succeeded=False`, and
`event_delivery_failure_code=None`; it is not `NO_HANDLER`,
`INVALID_ENVELOPE`, or a lifecycle failure.
