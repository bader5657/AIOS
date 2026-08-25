# Production Preflight, Identity, and Stop Gates

The expected target is PostgreSQL service/container `aios-postgres`, database
`aios`, schema `public`, PostgreSQL 17.x, and the established persistent
production volume. These values are expectations, not evidence gathered during
authority publication. The future executor must independently verify actual
service, container, database, server version, volume identity, and connection
target before any transaction begins.

The single attempt is eligible only if preflight proves all of the following:

1. `HEAD`, local `main`, and `origin/main` equal frozen commit
   `41bef3015c82c73bbe918807d27c6fbbd1180985`;
2. the worktree is clean;
3. both migration files match their frozen SHA-256 values;
4. PostgreSQL is healthy and its restart count is recorded;
5. database `aios`, schema `public`, server, and persistent-volume identity pass;
6. `public.material_stock` exists and exactly matches its approved contract;
7. a bounded material-stock schema, constraint, index, owner, ACL, row-count, and
   content fingerprint is captured;
8. `public.material_receipts`, `public.material_receipt_items`, and
   `public.inventory_movements` are all absent;
9. no migration-number or target-identifier collision exists;
10. bounded unrelated-schema, ownership, role, grant, routine, trigger, and
    extension fingerprints are captured;
11. `aios_material_stock_reader` attributes, memberships, ownership absence, and
    effective privileges are recorded unchanged;
12. all writer role and runtime-login identifiers remain outside this execution
    scope.

An unexpected target relation or identifier, hash mismatch, dirty source,
identity ambiguity, dependency mismatch, unhealthy server, restart anomaly, or
fingerprint failure requires STOP before mutation. The executor must not repair,
drop, rename, reuse, reconcile, or retry under this authority.

No writer role, login, credential, grant, revoke, default privilege, ownership,
runtime configuration, or business data may be created or changed during the
attempt.
