# Preserved Authority Gaps

Stage 5.1.2 deliberately leaves all of the following unresolved:

- Registry Entry;
- concrete record representation;
- runtime Register/read/update API;
- persistence interface;
- PostgreSQL schema, tables, columns, constraints, and indexes;
- migrations and reversibility procedure;
- ORM or database driver;
- transaction and isolation behavior;
- commit, rollback, retry, and failure semantics;
- identifier format and generation strategy;
- status vocabulary and transitions;
- database testing and integration behavior; and
- production connection and deployment.

No historical implementation detail resolves any gap. Absence of a decision
is a gate, not permission to infer one.
