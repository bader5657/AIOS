# READ COMMITTED Isolation Scope

Verification must prove:

1. the actual Registry transaction isolation is PostgreSQL `READ COMMITTED`;
2. a committed Registry write is visible from a later independent Registry
   operation and connection;
3. uncommitted state is not visible as committed state;
4. rolled-back state is absent from a later independent operation;
5. each Registry operation has independent transaction state; and
6. rollback in one operation does not poison a later operation.

No stronger isolation, explicit locking, version field, or application-level
conflict guarantee may be inferred.
