# Read-Only Preflight and Zero-Row Hard Gate

## Separate, bounded authority

The canonical sequence is **0.33B-G → 0.33B-P → 0.33B-A → 0.33B-D →
0.33B-V**: governance review and merge; separately authorized production
READ-ONLY preflight; separately reviewed and merged one-shot Migration 0005
execution authorization; exactly one controlled production Migration 0005
execution attempt; and separately authorized new-session READ-ONLY
post-deployment verification. No stage may be omitted or combined.

After 0.33B-G is independently reviewed and merged, 0.33B-P may authorize one
bounded production read-only preflight session. Governance publication itself
does not authorize that session. A PASS makes a one-shot authorization request
eligible; it never authorizes DDL.

The preflight uses `BEGIN READ ONLY`, makes no lock request, and performs no
write, DDL, role/grant operation, configuration change, or mutation-capable
transaction. It verifies:

- clean synchronized repository source and both frozen Migration 0005 hashes;
- running/healthy `aios-postgres`, expected image/storage identity, PostgreSQL
  17.x, database/user `aios`, schema `public`, and fixed container-local control
  plane;
- Migration 0005 has not already been applied: creator column and named CHECK
  are both absent;
- `public.material_receipts_source_asset_active_uidx` exists, is valid, ready,
  unique, has sole key `source_asset_reference`, and retains predicate
  `(status <> ALL (ARRAY['REJECTED'::text, 'CANCELLED'::text]))` (semantic
  equivalent catalog rendering is acceptable only when structured fields prove
  the same expression);
- row counts for receipts, receipt items, movements, and stock;
- relevant columns, constraints, indexes, non-internal triggers, public
  functions, relations, schemas/extensions, owners, role attributes,
  memberships, ADMIN OPTION values, and ACLs; and
- unchanged runtime/service identity and continued absence of production
  candidate activation, using bounded non-secret operational evidence only.

No secret value, password, credential-bearing DSN, runtime environment content,
Telegram token, or connection string may be emitted.

## Zero-row hard gate

The authoritative scalar query is:

```sql
SELECT COUNT(*) FROM public.material_receipts;
```

Only the exact result `0` passes. Any positive value produces:

```text
PRODUCTION ACTOR-PROVENANCE PREFLIGHT BLOCKED
— EXISTING MATERIAL RECEIPTS REQUIRE HISTORICAL PROVENANCE GOVERNANCE
```

The preflight then stops. It may not set a default, introduce a nullable phase,
rewrite/delete/cancel rows, or assign `system`, `admin`, `aios`, `migration`,
`unknown`, `unknown-operator`, `default-operator`,
`operator:00000000-0000-4000-8000-000000000000`, or any equivalent synthetic
identity. Historical rows require separate governance.

## Reproducible data baseline

Inside `BEGIN READ ONLY`, establish exactly:

```sql
SET LOCAL TIME ZONE 'UTC';
SET LOCAL DateStyle = 'ISO, YMD';
SET LOCAL IntervalStyle = 'iso_8601';
SET LOCAL bytea_output = 'hex';
```

For each governed table capture only its name, row count, and deterministic
digest:

```sql
SELECT COUNT(*) AS row_count,
       md5(COALESCE(string_agg(row_to_json(t)::text, E'\n'
                               ORDER BY <PRIMARY_KEY>), '')) AS row_digest
FROM <TABLE> AS t;
```

Frozen substitutions are:

| Table | Stable order |
|---|---|
| `public.material_receipts` | `receipt_id` |
| `public.material_receipt_items` | `receipt_item_id` |
| `public.inventory_movements` | `movement_id` |
| `public.material_stock` | `material_id` |

The serialized rows never leave PostgreSQL. The same settings and query shape
must be used for preflight, locked execution snapshots, and post-deployment
verification. An unavailable or incomparable fingerprint is
`PRESERVATION VERIFICATION INCONCLUSIVE — STOP`.

## Security/object and role baseline

Capture structured, deterministically ordered non-secret snapshots/digests for:

- all indexes, columns, and constraints on the four governed tables;
- non-internal triggers and relevant `public` functions;
- database/schema/table owners, `public` schema and extensions, and relevant
  relations;
- relevant role attributes for candidate runtime/writer, posting
  runtime/writer, material-stock reader, and directly governed `aios` roles;
- memberships with ADMIN OPTION and relevant ACL/column-privilege rows.

The expected later delta is only candidate-writer INSERT privilege on the new
creator column. No creator UPDATE, posting creator UPDATE, reader write, role,
membership, ADMIN OPTION, ownership, password, or credential delta is allowed.

## Preflight classifications

- **PASS** — identity/health/source/schema/index/baselines pass, creator objects
  are absent, and receipt count is exactly zero. Eligible only to request
  0.33B-A.
- **BLOCKED** — existing receipts or a substantive safety/schema/security
  mismatch. Stop without mutation.
- **INCONCLUSIVE** — target, evidence, fingerprint, source, or identity cannot
  be proven. Stop without mutation.
