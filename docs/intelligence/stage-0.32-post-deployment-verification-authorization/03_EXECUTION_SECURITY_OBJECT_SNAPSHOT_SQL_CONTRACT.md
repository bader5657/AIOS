# Original Execution Security/Object Snapshot SQL Contract

## Historical evidence and authority

This is the single authoritative SQL definition for the eight security/object
snapshot digests recorded during the successful Stage 0.32 Migration 0004
execution. It is recovered verbatim from the retained Codex execution transcript:

```text
/home/aiosadmin/.codex/sessions/2026/08/27/
rollout-2026-08-27T20-52-14-01a0437e-1f82-7c53-87a0-a548950de701.jsonl
```

- JSONL line 1419, ordinal 1418, completed tool-call ID
  `call_Bo5qqr263vLlekUN1Veb01tm` contains the exact production execution command
  and the after-DDL snapshot SQL below.
- JSONL line 1421, ordinal 1420 contains the matching execution output, all eight
  frozen digests, successful preservation assertion, final pre-COMMIT PASS,
  COMMIT, and post-COMMIT index presence.

These queries are historical recovery, not newly inferred or equivalent-looking
replacements. The post-deployment verifier must use these exact after-state
queries. It must not use the execution's pre-DDL index exclusion expression,
because the new index did not yet exist in that pre-state; Snapshot 1 below is
the exact after-DDL exclusion contract that produced the frozen index digest.

## Canonical session representation

The execution established these settings transaction-locally before both the
before- and after-DDL snapshots:

```sql
SET LOCAL TIME ZONE 'UTC';
SET LOCAL DateStyle = 'ISO, YMD';
SET LOCAL IntervalStyle = 'iso_8601';
SET LOCAL bytea_output = 'hex';
```

The future read-only verifier must establish the same four settings before the
queries below. There is no additional normalization. Every snapshot serializes
the selected subquery row with `row_to_json(x)::text`, aggregates rows with the
exact delimiter `E'\n'` in the stated `ORDER BY`, maps an empty aggregate to
`''` using `COALESCE`, and hashes that exact text with `md5`.

SQL NULL values remain JSON `null` inside `row_to_json`. Explicit casts in the
projections—such as `::regclass::text`, `::text`, and `NULL::text`—are part of
the contract. Catalog-native booleans, integers, timestamps, internal `char`
values, arrays, and text returned by named functions retain PostgreSQL 17's
`row_to_json(... )::text` representation. No column, cast, filter, join, sort
key, exclusion, delimiter, or hash expression may be added, removed, reordered,
or substituted.

## Snapshot 1 — governed indexes excluding the new index

Frozen digest: `7df74340faad2243bc1d882b01041e75`

```sql
SELECT md5(COALESCE(string_agg(row_to_json(x)::text,E'\n' ORDER BY x.index_name),'')) AS digest
FROM (SELECT i.indexrelid::regclass::text AS index_name,i.indrelid::regclass::text AS relation,
             i.indisunique,i.indisvalid,i.indisready,i.indnkeyatts,pg_get_indexdef(i.indexrelid) AS definition
      FROM pg_index i WHERE i.indrelid IN ('public.material_receipts'::regclass,'public.material_receipt_items'::regclass,
        'public.inventory_movements'::regclass,'public.material_stock'::regclass)
        AND i.indexrelid <> 'public.material_receipts_source_asset_active_uidx'::regclass) x
\gset after_indexes_
```

The exclusion above is exactly the execution after-state exclusion. No other
index exclusion is authorized.

## Snapshot 2 — database/schema/table ownership and ACLs

Frozen digest: `3477e5fbfeca35e7aed45bae17990467`

```sql
SELECT md5(COALESCE(string_agg(row_to_json(x)::text,E'\n' ORDER BY x.object_type,x.object_name),'')) AS digest
FROM (SELECT 'database' AS object_type,d.datname AS object_name,pg_get_userbyid(d.datdba) AS owner,NULL::text AS acl
      FROM pg_database d WHERE d.datname=current_database()
      UNION ALL SELECT 'schema',n.nspname,pg_get_userbyid(n.nspowner),n.nspacl::text FROM pg_namespace n WHERE n.nspname='public'
      UNION ALL SELECT 'table',c.oid::regclass::text,pg_get_userbyid(c.relowner),c.relacl::text FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
      WHERE n.nspname='public' AND c.relname IN ('material_receipts','material_receipt_items','inventory_movements','material_stock')) x
\gset after_ownership_
```

## Snapshot 3 — relevant role attributes

Frozen digest: `65cbf0f753fc942d636edba8bf443f75`

```sql
SELECT md5(COALESCE(string_agg(row_to_json(x)::text,E'\n' ORDER BY x.rolname),'')) AS digest
FROM (SELECT rolname,rolsuper,rolinherit,rolcreaterole,rolcreatedb,rolcanlogin,rolreplication,rolbypassrls,rolconnlimit,rolvaliduntil
      FROM pg_roles WHERE rolname LIKE 'aios%') x
\gset after_roles_
```

The exact historical role predicate is `rolname LIKE 'aios%'`; it must not be
replaced with a newly constructed allowlist.

## Snapshot 4 — relevant memberships

Frozen digest: `8882f55ea69746e789f960881f301818`

```sql
SELECT md5(COALESCE(string_agg(row_to_json(x)::text,E'\n' ORDER BY x.member,x.granted_role),'')) AS digest
FROM (SELECT m.rolname AS member,g.rolname AS granted_role,am.admin_option FROM pg_auth_members am
      JOIN pg_roles m ON m.oid=am.member JOIN pg_roles g ON g.oid=am.roleid
      WHERE m.rolname LIKE 'aios%' OR g.rolname LIKE 'aios%') x
\gset after_memberships_
```

No `inherit_option` or `set_option` field was selected by the original execution;
none may be added when comparing this historical digest.

## Snapshot 5 — non-internal governed-table triggers

Frozen digest: `d41d8cd98f00b204e9800998ecf8427e`

```sql
SELECT md5(COALESCE(string_agg(row_to_json(x)::text,E'\n' ORDER BY x.relation,x.trigger_name),'')) AS digest
FROM (SELECT tg.tgrelid::regclass::text AS relation,tg.tgname AS trigger_name,pn.nspname AS function_schema,p.proname AS function_name
      FROM pg_trigger tg JOIN pg_proc p ON p.oid=tg.tgfoid JOIN pg_namespace pn ON pn.oid=p.pronamespace
      WHERE NOT tg.tgisinternal AND tg.tgrelid IN ('public.material_receipts'::regclass,'public.material_receipt_items'::regclass,
        'public.inventory_movements'::regclass,'public.material_stock'::regclass)) x
\gset after_triggers_
```

The frozen digest is `md5('')`, proving the selected after-state set was empty
under this exact projection and scope.

## Snapshot 6 — relevant public user-defined functions

Frozen digest: `d41d8cd98f00b204e9800998ecf8427e`

```sql
SELECT md5(COALESCE(string_agg(row_to_json(x)::text,E'\n' ORDER BY x.schema_name,x.function_name,x.identity_args),'')) AS digest
FROM (SELECT n.nspname AS schema_name,p.proname AS function_name,pg_get_function_identity_arguments(p.oid) AS identity_args,
             p.prokind,pg_get_userbyid(p.proowner) AS owner,p.proacl::text AS acl
      FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public') x
\gset after_functions_
```

The frozen digest is `md5('')`, proving the selected after-state set was empty.
Function definitions/bodies were not selected by the original projection and
must not be added to this historical comparison.

## Snapshot 7 — public schema and extensions

Frozen digest: `093bc6d4016f7335c21b23f8789f9eff`

```sql
SELECT md5(COALESCE(string_agg(row_to_json(x)::text,E'\n' ORDER BY x.object_type,x.object_name),'')) AS digest
FROM (SELECT 'schema' AS object_type,n.nspname AS object_name,pg_get_userbyid(n.nspowner) AS owner,n.nspacl::text AS detail
      FROM pg_namespace n WHERE n.nspname='public'
      UNION ALL SELECT 'extension',e.extname,pg_get_userbyid(e.extowner),e.extversion FROM pg_extension e) x
\gset after_schema_ext_
```

All extension rows are included; the schema arm includes only `public`.

## Snapshot 8 — public non-index relations

Frozen digest: `a51c24af830e4f3ad62ec26172ed1dc3`

```sql
SELECT md5(COALESCE(string_agg(row_to_json(x)::text,E'\n' ORDER BY x.relation),'')) AS digest
FROM (SELECT c.oid::regclass::text AS relation,c.relkind,pg_get_userbyid(c.relowner) AS owner,c.relacl::text AS acl
      FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relkind <> 'i') x
\gset after_relations_
```

The exact historical relation predicate includes every `public` relation whose
`relkind` is not internal `char` value `'i'`; no other relkind is excluded.

## Comparison and fail-closed rule

The verifier must first verify this contract's repository path and frozen
SHA-256 recorded by the other authorization documents. It then runs these eight
queries unchanged inside the authorized read-only PostgreSQL 17 transaction.
Each resulting psql variable must equal its corresponding frozen digest.

If the contract path/hash differs, a query cannot execute unchanged, any
result differs, or any projection/representation detail requires inference,
classification is **POST-DEPLOYMENT VERIFICATION INCONCLUSIVE — STOP**. No
equivalent-looking query, baseline rewrite, corrective mutation, or digest waiver
is authorized.
