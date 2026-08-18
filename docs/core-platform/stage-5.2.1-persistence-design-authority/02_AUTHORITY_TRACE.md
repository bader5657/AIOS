# Authority Trace

| Requirement | Active authority | Stage 5.2.1 result |
|---|---|---|
| PostgreSQL stores identity, metadata, relationships, status, and file location | Blueprint | Exactly five persistence categories |
| Original binary remains outside PostgreSQL Registry | Blueprint; Stage 5.1.1 | Binding exclusion |
| No roadmap or architecture expansion | Frozen Roadmap; Authority Hierarchy | Database-local design only |
| PostgreSQL Registry canonical; Registry Entry unresolved | Canonical Model | Table row is not a canonical object |
| Register enters Core Layer after completed Manifest | Layer Architecture; Core Platform Authority Decision | Transaction begins only at Registry boundary |
| Stage 5.2.1 approves schema/migration/transaction approach | Frozen Execution Plan | This package supplies the required persistence design record |
| Five-category responsibility contract Active | Stage 5.1.1 | Closed responsibility input |
| Historical component REJECT reaffirmed | Stage 5.1.2 | No historical field/model restoration |

The Blueprint does not prescribe a table, column, identifier mechanism, JSONB
representation, migration mechanism, or transaction isolation level. The
Project Owner decision supplies those narrower database-local choices without
altering higher authority.
