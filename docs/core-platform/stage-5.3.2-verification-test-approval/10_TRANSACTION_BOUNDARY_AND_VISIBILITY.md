# Transaction Boundary and Visibility

Register and update remain one Registry-local transaction per operation.
Commit occurs only on full success; persistence failure rolls back the complete
operation.

Visibility evidence must use later independent Registry operations/connections,
not the cursor or transaction that performed the write.

No Registry transaction may span or call:

- Storage;
- Metadata Engine;
- Document Manifest;
- Asset Pipeline;
- Universal Ingestion; or
- an external service.

Test source and runtime-source inspection provide the containment evidence.
