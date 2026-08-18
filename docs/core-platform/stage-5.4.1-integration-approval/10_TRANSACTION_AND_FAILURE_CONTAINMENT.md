# Transaction and Failure Containment

The transaction remains entirely inside `PostgresRegistry.register(...)` under
the accepted Registry-local `READ COMMITTED` contract. Universal Ingestion must
not open, receive, pass, commit, or roll back SQL transactions and must not span
Storage, Metadata, Manifest, and Registry in one transaction.

A persistence failure rolls back only the Registry transaction. Stored
originals and completed Manifest artifacts remain owned and preserved by their
existing components. Automatic retry remains prohibited.
