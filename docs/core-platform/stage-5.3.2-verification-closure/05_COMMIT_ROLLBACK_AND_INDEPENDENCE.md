# Commit Visibility, Rollback Invisibility, and Independence

Evidence proved:

- a successful register committed and a later independent Registry connection
  read the complete row;
- a multi-field update through a disposable read-only transaction failed with
  `RegistryPersistenceError`;
- a later independent read observed every previously committed field and none
  of the failed values;
- a failed register left zero rows;
- a new Registry register/read operation succeeded after rollback; and
- failed transaction state did not leak between operations.

The Registry-local atomicity and transaction-independence gates pass.
