# Preflight, Transaction, Attempt, and Stop Policy

## Fresh production preflight

Immediately before execution, retain a UTC timestamp and require:

- `HEAD == main == origin/main` after refreshing `origin/main`;
- a clean worktree;
- exact approved migration paths and SHA-256 values;
- the exact production container/service, database, host/socket, user, schema,
  and persistent data identity, without retaining credentials;
- PostgreSQL healthy and accepting connections;
- the target is production, not a test or isolated database;
- explicit transaction capability healthy;
- `to_regclass('material_stock') IS NULL` in the target schema context;
- no collision with `0002_create_material_stock` if a persistent production
  migration-history mechanism exists;
- bounded unrelated-schema identities and role/grant fingerprints.

The repository has no persistent migration-history mechanism. Do not invent
one. If production has no independent mechanism, rely on the immutable source
identity and strict absence gate.

If `material_stock` exists or any other gate fails, stop with
`PRODUCTION_MIGRATION_PREFLIGHT_BLOCKED`. Do not drop, alter, overwrite, repair,
or consume the execution attempt.

## Single-use execution

After every preflight gate passes, exactly one new production migration attempt
is authorized:

1. `BEGIN`.
2. Execute the exact verified up-migration contents once.
3. Run the corrected structured read-only verifier in the same transaction.
4. `COMMIT` only after every verification gate passes.

If migration SQL or verification fails, `ROLLBACK`, stop, retain evidence, and
do not retry under this authority. A verifier failure consumes the attempt even
when rollback leaves no persistent mutation.

After commit, repeat bounded read-only checks for table existence, exact schema,
zero rows, unrelated-schema preservation, role/grant preservation, and
PostgreSQL health.

The down migration is not authorized during normal deployment. A pre-commit
failure uses transaction rollback only. An unexpected post-commit inconsistency
requires stop and return to governance; do not automatically execute the down
migration or improvise schema repair.

No service restart, Docker/network change, role provisioning, grant/revoke,
data insertion, Registry mutation, retrieval, or inference is authorized.
