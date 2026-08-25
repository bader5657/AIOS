# AIOS Intelligence Migration 0003 — Package Control, Hashes, and Authority

| Control | Frozen value |
|---|---|
| Implementation PR | `#212`, merged normally |
| Implementation commit | `1a8b64b0c86e9025d6512443718c6485d35c2cd6` |
| Authoritative main commit | `41bef3015c82c73bbe918807d27c6fbbd1180985` |
| Up path | `migrations/postgres/0003_create_material_receipt_inventory_movement.up.sql` |
| Up SHA-256 | `e858f5ad210aca2d7e6a2badf3dab2585cf33eacdcf46e6b6bf839dcea7d37eb` |
| Down path | `migrations/postgres/0003_create_material_receipt_inventory_movement.down.sql` |
| Down SHA-256 | `c374837cad14df82126ab56ae487766694911ed89cbdace1382faeb40aebb8fe` |
| Production attempts | exactly one fresh attempt |
| Retry | none |
| Authority publication execution | prohibited |

PR `#212` contained only the two migration files and their isolated PostgreSQL
integration-test module. Review found no contract drift, unrelated file, writer
role or grant SQL, seed data, runtime code, Telegram change, or production
operation. The reported focused, existing-migration, compile, static, and broader
test evidence is consistent with the merged artifacts.

This package publishes one future production DDL authority bound to the exact
main commit and file hashes above. Any commit or hash mismatch invalidates the
authority. Publication itself performs no PostgreSQL connection, preflight, DDL,
role provisioning, data population, runtime action, receipt processing, stock
posting, or inference.

The only authorized future mutation is one transaction applying the exact up
migration. The down migration hash is frozen for package identity and rollback
traceability but down execution is not authorized.

`MIGRATION 0003 PRODUCTION DEPLOYMENT AUTHORIZED — READY FOR ONE CONTROLLED EXECUTION ATTEMPT`
