# Production Findings, Provisioning Gates, and Validation

## Read-only findings at approval

Production PostgreSQL 17.10 was healthy. Database `aios`, schema `public`, and
table `public.material_stock` were present; the table row count was zero.

Catalog inspection found:

- `aios_material_stock_reader` absent and eligible for creation;
- table owner remains `aios`;
- `relacl` is null and there are zero specific non-owner table grants;
- `PUBLIC` has no `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`,
  `REFERENCES`, or `TRIGGER` privilege on `public.material_stock`;
- `PUBLIC` has the existing PostgreSQL environmental defaults `CONNECT` and
  `TEMP` on databases `aios` and `postgres`, plus `USAGE` but not `CREATE` on
  schema `public`;
- `PUBLIC` has PostgreSQL default `EXECUTE` on built-in and system routines,
  while no material-stock-specific routine exists;
- no custom default-privilege rows exist;
- no routine depends on `public.material_stock`.

The inherited `PUBLIC TEMP` capability is explicitly accepted as a pre-existing
database-wide default for this approval. It is not a role-specific grant and
does not confer table access. Removing it would require broader database policy
authority and is not authorized here. The future provisioner must not issue a
role-specific `TEMP` grant.
The inherited `PUBLIC CONNECT` path to maintenance database `postgres` and
default built-in routine execution are also environmental baselines, not
dedicated-role grants. This approval grants `CONNECT` explicitly only on `aios`,
grants no routine `EXECUTE`, and requires runtime connections to target `aios`.
Tightening database-wide `PUBLIC` defaults or `pg_hba.conf` requires separate
authority; `PUBLIC` has no privilege on `public.material_stock`.

## Collision and stop gates

Immediately before future provisioning, repeat production identity/health,
table existence and zero-row, proposed-role collision, table ACL, ownership,
`PUBLIC`, membership, and default-privilege checks.

If the role exists, stop and inspect its exact attributes, memberships,
ownership, and grants. Do not alter or replace it automatically. If the table
has acquired a broader non-owner access path, stop and return the finding to
governance before provisioning.

## Post-provisioning validation

Use read-only catalog and privilege inspection to prove:

1. the role exists with exactly the approved conservative attributes;
2. it has no memberships or admin options;
3. `CONNECT` on `aios` and `USAGE` on `public` are effective;
4. `SELECT` on `public.material_stock` is effective;
5. `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `REFERENCES`, and `TRIGGER` are
   denied;
6. unrelated-table `SELECT` is denied except any separately adjudicated
   inherited `PUBLIC` path;
7. schema/database `CREATE`, role-management, replication, and bypass-RLS are
   denied;
8. it owns no object;
9. it has no sequence or material-stock-specific routine privilege;
10. default privileges are unchanged and no future-table access was introduced;
11. `public.material_stock` remains empty;
12. PostgreSQL remains healthy and no service was restarted.

Do not validate denial by inserting, updating, deleting, or truncating production
data. Prefer `has_*_privilege`, ACL, ownership, membership, and catalog queries.
Any live connection probe must remain read-only and must not expose its secret.
