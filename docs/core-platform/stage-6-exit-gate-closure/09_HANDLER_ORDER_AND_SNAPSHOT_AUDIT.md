# Handler Order and Snapshot Audit

Handlers are awaited sequentially in deterministic registration order within
one EventEngine instance and one invocation. The matching list is snapshotted
before the first handler runs. Registration during dispatch is excluded from
the active snapshot and eligible for a later explicit invocation.

No global, durable, cross-process, distributed, or broker ordering guarantee is
claimed.
