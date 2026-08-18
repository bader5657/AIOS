# Dispatch, Snapshot, and Ordering

For one valid envelope, Process must:

1. read exact `envelope.event_name`;
2. obtain current matching registration entries;
3. create a defensive immutable snapshot before invocation;
4. return `NO_HANDLER` when the snapshot is empty;
5. await each entry sequentially in registration order;
6. increment count only after successful completion;
7. stop and return `HANDLER_FAILURE` on the first ordinary handler exception;
8. return success only after every snapshot entry completes.

A handler registered during delivery is excluded from the current snapshot and
may participate in a later invocation. Handlers are never sorted.

No `asyncio.gather`, `create_task`, task group, worker pool, fan-out, or hidden
parallelism is authorized. Ordering is in-process invocation order only, not a
global or durable guarantee.
