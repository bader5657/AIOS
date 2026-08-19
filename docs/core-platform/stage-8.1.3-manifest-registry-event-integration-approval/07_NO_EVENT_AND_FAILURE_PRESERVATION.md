# No-Event and Failure Preservation

When Registry commits and `domain_event is None`, registration remains successful,
Event Engine receives zero calls, publication attempted is `False`, delivery
succeeded is `False`, and failure code is `None`. This is not a failure.

After Registry commit, a bounded Event Engine failure must preserve the committed
Registry row, stored original, metadata, and Manifest. It causes no compensation,
Registry rollback, Storage rollback, Manifest rollback, or retry.

If `EventEngine.process()` raises an unexpected exception, that exception propagates
under the existing contract. The already-committed Registry row and upstream
artifacts remain intact. No global exception mapping is introduced.

Repeated explicit calls remain independent operations. No deduplication,
idempotency key, event ledger, processed-event set, or duplicate suppression is
authorized.
