# Corrected Execution Authority and Safety Boundary

Exactly one future controlled production attempt is reauthorized. The previous
blocked local hash preflight did not consume an attempt because no production
connection or transaction began.

The reauthorization is bound to:

- clean-main provenance baseline
  `dc567260c8f7c70f3e651531c2ab7ed8fcff7855` and the future normal merge of this
  documentation-only reconciliation;
- unchanged Migration 0003 blobs introduced by implementation commit
  `1a8b64b0c86e9025d6512443718c6485d35c2cd6`;
- up SHA-256
  `e858f5ad210aca2d7e6a2badf3dab2585cf33eacdcf46e6b6bf839dcea7d37eb`;
- corrected down SHA-256
  `c374837cad14df82126ab56ae487766694911ed89cbdace1382faeb40aebb8fe`;
- the preflight, structured verifier, empty-table, material-stock, unrelated-
  schema, role/grant, and postflight preservation gates approved in PR `#213`.

Activation requires this reconciliation PR to merge normally, fresh equality of
`HEAD`, `main`, and `origin/main`, a clean worktree, exact hashes, and a complete
fresh production preflight. Any migration-path change after the provenance
baseline invalidates this authority even if unrelated documentation is merged.

The future attempt follows preflight, target-absence checks, one explicit
transaction, exact up migration, structured verification, preservation
verification, and commit only on complete PASS. Failure after transaction start
requires rollback and STOP and consumes the authority. There is no retry.

This reauthorization does not execute or connect to PostgreSQL. It does not
authorize the down migration, writer roles, credentials, grants, data population,
runtime implementation, Telegram, retrieval changes, inventory posting, or
inference.
