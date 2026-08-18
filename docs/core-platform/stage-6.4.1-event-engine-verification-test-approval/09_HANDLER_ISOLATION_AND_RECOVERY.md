# Handler Isolation and Recovery

Handler isolation means only:

- defensive snapshot isolation;
- sequential awaited invocation;
- failure-stop containment;
- immutable EventEnvelope and DomainEvent boundaries;
- no parallel shared task; and
- an independent later invocation remains usable.

After a `HANDLER_FAILURE`, a later explicit Process invocation must prove the
instance remains usable. Similar later-valid coverage follows invalid input and
no-handler outcomes where applicable. This is invocation-local containment and
recovery, not retry, rollback, compensation, process/thread/sandbox isolation,
or transactional handler isolation.

Completed handler side effects are not transactionally reversed when a later
handler fails.
