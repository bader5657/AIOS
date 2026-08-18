# Integration Owner and Caller Boundary

**Universal Ingestion is the sole Stage 5.4.1 Registry integration owner and
caller.**

Universal Ingestion owns only:

1. receiving the successful Asset Pipeline / completed Manifest disposition;
2. constructing `RegistryPersistenceInput` from already-approved values;
3. calling `PostgresRegistry.register(...)` exactly once;
4. translating success or `RegistryPersistenceError` into the bounded final
   ingestion result.

Document Manifest must not import or call Registry. Asset Pipeline must not
import or call Registry. The active Pipeline → Registry prohibition remains
unchanged. Registry owns persistence semantics and its local transaction; it
does not acquire ingestion, Request Context, Storage, Metadata, Manifest, or
Pipeline ownership.
