# Transaction, Isolation, and Failure Policy

## Transaction Boundary

One future registration persistence operation equals one PostgreSQL
transaction. All persistence for that single registration succeeds atomically
or the Registry transaction rolls back. No partial successful Registry row is
permitted.

The transaction begins only at the future PostgreSQL Registry persistence
boundary. It does not span Storage, Metadata, Document Manifest, another
service, or a distributed transaction.

## Isolation

Initial isolation is PostgreSQL `READ COMMITTED`. Stronger isolation, explicit
locking, or `SERIALIZABLE` is not authorized without later evidence.

## Commit and Rollback

Commit occurs only after the complete Registry write succeeds. A persistence
error rolls back the Registry transaction. Rollback must not delete or mutate
Storage-owned originals or completed Manifest artifacts.

## Retry

Automatic retry is not authorized. No hidden retry loop or retry count is
implied. Retry policy remains unresolved for later failure/implementation
authority.
