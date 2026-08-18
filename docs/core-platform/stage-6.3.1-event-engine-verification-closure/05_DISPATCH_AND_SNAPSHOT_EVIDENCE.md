# Dispatch and Snapshot Evidence

For a valid envelope, the runtime snapshots matching handlers as a tuple before
the first invocation, then awaits each handler sequentially in registration
order. A handler registered during dispatch is excluded from the current
invocation and becomes eligible for a later invocation.

No gather, task spawning, task group, fan-out, worker pool, thread, or process
execution exists.
