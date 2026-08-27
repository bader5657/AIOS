# Stage 0.32 Production Migration 0004 Governance — Package Control

Date: 2026-08-27 (Asia/Jakarta)

## Classification and non-execution boundary

This is a documentation-only governance package. It does not authorize or
perform a production PostgreSQL connection, duplicate preflight, migration,
schema/data mutation, credential operation, service restart, or application
activation. Publication and merge of this package are not migration authority.

| Control | Frozen value |
|---|---|
| Implementation PR | `#235`, merged and post-merge verified |
| Reviewed implementation commit | `b2c1f3b705c266b3024062e2132797be72e96746` |
| Authoritative main baseline | `f9cc68c950e6fdcf8fb3598aec186d4db6e60084` |
| UP path | `migrations/postgres/0004_add_material_receipt_source_active_uniqueness.up.sql` |
| UP SHA-256 | `90a009a33d4ca1cfcb3bd9b68170188f46626edc6789fba27f60c7b96f684baf` |
| DOWN path | `migrations/postgres/0004_add_material_receipt_source_active_uniqueness.down.sql` |
| DOWN SHA-256 | `4a702755c855c55f0300b9f57d8aa290846d413d2c7de88cb728f5e490225977` |

The frozen UP content is exactly:

```sql
CREATE UNIQUE INDEX material_receipts_source_asset_active_uidx
ON material_receipts (source_asset_reference)
WHERE status NOT IN ('REJECTED', 'CANCELLED');
```

The frozen DOWN content is exactly:

```sql
DROP INDEX material_receipts_source_asset_active_uidx;
```

Any source commit, path, hash, or SQL mismatch blocks later execution authority.
The UP migration contains no data rewrite, status mutation, `CASCADE`, role,
grant, ownership, trigger, function, or unrelated schema operation.

## Frozen target and control plane

The expected production target, based only on existing operational closure
records, is:

| Target | Frozen expectation |
|---|---|
| Container | `aios-postgres` |
| PostgreSQL | 17.x; last recorded production version 17.10 |
| Database / administrative identity | `aios` / `aios` |
| Schema / table | `public` / `public.material_receipts` |
| Existing index retained | `public.material_receipts_source_asset_idx` |
| New index | `public.material_receipts_source_asset_active_uidx` |

The only eligible future administration transport is the fixed argv shape:

```text
/usr/bin/docker exec -i aios-postgres /usr/local/bin/psql
    -X -v ON_ERROR_STOP=1 -U aios -d aios
```

SQL is delivered through stdin or an independently approved exact file-input
mechanism. Credentials must not appear in argv, a URI, logs, chat, or evidence.
There is no `sudo -u postgres`, host socket, host `psql`, external endpoint,
arbitrary container/database/role, or production fallback.

## Exact scope and preserved state

Only creation of the frozen partial unique index on
`public.material_receipts(source_asset_reference)` is eligible for later
authority. `material_receipts_source_asset_idx` remains non-unique and retained.
No role, membership, grant, owner, password, runtime configuration, business
row, Telegram path, Universal Ingestion path, confirmation/posting capability,
actor-provenance field, or service state may change.

Production candidate activation remains NOT AUTHORIZED. The source-idempotency
operational gate remains OPEN.
