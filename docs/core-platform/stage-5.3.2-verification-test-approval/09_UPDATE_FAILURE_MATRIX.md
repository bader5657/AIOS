# Update Failure Matrix

Required cases:

- missing row returns `None`;
- empty `RegistryUpdate` raises `ValueError` before opening a connection;
- a multi-field update through a disposable read-only transaction raises
  `RegistryPersistenceError`;
- every previously committed field remains unchanged after failure;
- no partially updated state is visible from a later independent operation;
- a later valid operation succeeds; and
- no retry occurs.

At least two mutable fields must be present in the failed update so atomic
rollback is demonstrated.
