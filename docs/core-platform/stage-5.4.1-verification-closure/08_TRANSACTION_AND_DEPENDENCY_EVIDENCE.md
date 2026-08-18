# Transaction and Dependency Evidence

Universal Ingestion opens, commits, and rolls back no SQL transaction. The
accepted Registry-local READ COMMITTED transaction remains entirely inside
`PostgresRegistry.register()`.

The only new dependency direction is the approved Ingestion → Registry
boundary. Registry does not depend on Ingestion, Pipeline, Manifest, Storage,
or Request Context ownership.
