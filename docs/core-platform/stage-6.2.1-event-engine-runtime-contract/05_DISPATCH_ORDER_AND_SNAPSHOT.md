# Dispatch, Ordering, and Snapshot Contract

For one valid envelope, Process must:

1. validate boundary compatibility;
2. read exact `envelope.event_name`;
3. resolve the current matching in-memory handler registrations;
4. create an immutable defensive snapshot of those registrations before the
   first handler invocation;
5. await each snapshot entry sequentially in registration order; and
6. return one bounded `EventDeliveryResult`.

Changes to registration state after snapshot creation do not alter the active
invocation. Each matched snapshot entry is attempted at most once during that
invocation. Process uses no `asyncio.gather`, task spawning, parallel fan-out,
background worker, or hidden concurrency.

Registration-order invocation is deterministic only inside one EventEngine
instance and one Process invocation. It is not global event ordering, durable
ordering, cross-process ordering, or a broker guarantee.
