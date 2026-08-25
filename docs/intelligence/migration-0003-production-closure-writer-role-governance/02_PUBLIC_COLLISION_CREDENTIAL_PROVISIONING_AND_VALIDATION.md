# PUBLIC, Collision, Credential, Provisioning, and Validation Controls

## Environmental access and ownership

Read-only production inspection found no PUBLIC table privilege on any regular
table in schema `public`. PUBLIC has environmental database `CONNECT` and
`TEMPORARY`, plus schema `USAGE`, but these do not confer receipt, movement,
material-stock, or unrelated business-table access. The isolation design is
therefore eligible. No automatic revoke or environmental privilege change is
authorized.

All four planned identifiers were absent. Future preflight repeats this collision
check; any unexpected role or login causes STOP without reuse, alteration,
rename, membership, or drop.

The existing controlled owner `aios` retains table ownership. New roles and
logins own no database, schema, table, sequence, routine, or other object. Default
privileges remain unchanged; future tables do not become available automatically.

`aios_material_stock_reader` remains unchanged. It receives no candidate or
posting membership; neither writer runtime receives reader membership.

## Credential and connection boundaries

Each runtime login receives a separate strong random secret generated only during
separately authorized provisioning. Secrets exist only in the runtime secret
facility and never in Git, GitHub, governance files, output, logs, Telegram,
Brain, or session journals.

Candidate processing connects only as
`aios_material_receipt_candidate_runtime`; authoritative posting connects only as
`aios_material_inventory_posting_runtime`; current-stock retrieval retains its
dedicated reader. Brain receives no database credential, connection handle,
generic SQL, or writer authority.

## Controlled provisioning and validation

Future provisioning proceeds only after governance merge, clean-main and
production identity checks, exact table/schema checks, collision checks, and
fresh PUBLIC/effective-access review. It then creates the two NOLOGIN roles,
generates secrets out of band, creates the two restricted LOGIN identities,
applies the exact database/schema/table/column grants, grants one-to-one
membership, validates the complete matrix, performs bounded authentication
probes, proves zero business-row mutation, and checks PostgreSQL health.

Validation uses database-, schema-, table-, and column-privilege functions plus
ACL, role-membership, ownership, and default-ACL catalogs. It must prove every
approved privilege and every denial, including immutable identifiers, parent
links, candidate inability to write stock or movements, posting inability to
rewrite business content or movements, absence of delete/truncate/DDL, reader
isolation, and unrelated-table denial.

Authentication probes may establish login and connection only. There are no
production INSERT, UPDATE, or DELETE probes. All four business tables must remain
at their pre-provisioning row counts.

This governance package creates no role, login, secret, membership, grant,
revoke, or data effect.
