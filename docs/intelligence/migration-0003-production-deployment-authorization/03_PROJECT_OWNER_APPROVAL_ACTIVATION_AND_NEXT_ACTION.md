# Project Owner Approval, Activation, and Next Action

I approve one fresh controlled production execution attempt for AIOS Intelligence
Migration 0003.

The authority is bound to main commit
`41bef3015c82c73bbe918807d27c6fbbd1180985`, up-migration SHA-256
`e858f5ad210aca2d7e6a2badf3dab2585cf33eacdcf46e6b6bf839dcea7d37eb`, and
down-migration SHA-256
`c374837cad14df82126ab56ae487766694911ed89cbdace1382faeb40aebb8fe`.

The future executor may make exactly one attempt, inside one explicit transaction,
after every source, identity, dependency, absence, health, fingerprint, and
preservation preflight gate passes. Commit is allowed only after the corrected
structured verifier proves the exact schema, empty new tables, unchanged
`material_stock`, unchanged reader, and no unrelated object or privilege change.

Failure requires rollback and STOP and consumes this authority. Retry and normal
down-migration execution are not authorized.

Writer role or login creation, credentials, grants or revokes, data population,
runtime implementation, Telegram, retrieval changes, receipt processing,
inventory posting, and inference remain unauthorized.

## Activation

Publication of this documentation does not activate execution from a feature
branch. The one-attempt authority activates only after this governance-only
package is reviewed and merged normally to `main`, followed by a fresh clean-main
preflight proving the exact frozen source and production identity.

The next official action after activation is one controlled production execution
session for the frozen up migration and verifier. It must not include role
provisioning or data population.

`MIGRATION 0003 PRODUCTION DEPLOYMENT AUTHORIZED — READY FOR ONE CONTROLLED EXECUTION ATTEMPT`
