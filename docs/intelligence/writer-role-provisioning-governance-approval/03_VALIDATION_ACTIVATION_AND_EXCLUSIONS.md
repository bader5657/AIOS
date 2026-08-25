# Validation, Activation, and Exclusions

## Controlled provisioning order

1. merge this governance approval;
2. verify clean approved main;
3. verify production identity, health, schema, empty row counts, and reader;
4. verify role collisions, PUBLIC access, ownership, grants, and secure-secret
   capability;
5. stage two independent pending secrets;
6. begin the single PostgreSQL provisioning transaction;
7. create privilege roles, LOGIN identities, exact grants, and memberships;
8. validate attributes, ownership, membership, and effective privileges;
9. commit only when all transaction-visible gates pass;
10. run bounded authentication probes and read-only postflight;
11. activate secrets only after both probes and postflight pass;
12. verify zero data mutation and unchanged health/restart count.

## Required validation

Use `has_database_privilege`, `has_schema_privilege`, `has_table_privilege`,
`has_column_privilege`, `pg_roles`, `pg_auth_members`, ownership catalogs, and
ACL inspection. Reports distinguish dedicated grants, inherited membership,
and PUBLIC/environmental access.

Candidate validation proves CONNECT/USAGE, governed receipt/item SELECT and
only the frozen INSERT/UPDATE columns, stock SELECT only, no movement access,
no immutable-key updates, and no unrelated-table access.

Posting validation proves receipt/item SELECT and only status/timestamp updates,
movement SELECT and only the frozen INSERT columns, no movement mutation,
stock SELECT and only `stock_qty`/`updated_at` updates, no stock insertion or
deletion, and no unrelated-table access.

Authentication probes may connect as each runtime, select a constant, and read
authorized metadata or counts. They may not insert, update, or delete business
rows.

## Preservation and isolation

After provisioning, receipt/item/movement counts remain `0 / 0 / 0` and
`material_stock` count/content remains unchanged. The existing reader remains
read-only with no writer membership. Writer runtimes receive no reader
membership.

Brain receives no credential, DB handle, generic SQL, or writer authority.
Runtime-service use, business data population, Telegram, OCR, LLM, and inference
remain unauthorized.

## Activation

Exactly one controlled production provisioning session becomes active only
after this governance PR merges normally, clean-main is established, and every
fresh production and secure-secret preflight passes. Publication of this file
does not provision any database identity or credential.

Next official action after merge is a separately executed, evidence-producing
controlled provisioning session under this exact authority.
