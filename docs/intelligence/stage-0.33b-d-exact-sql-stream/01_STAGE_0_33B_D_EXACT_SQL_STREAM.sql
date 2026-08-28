-- T01 BEGIN
BEGIN;

-- T02 lock timeout
SET LOCAL lock_timeout = '5s';

-- T03 statement timeout
SET LOCAL statement_timeout = '30s';

-- T04 time zone
SET LOCAL TIME ZONE 'UTC';

-- T05 date style
SET LOCAL DateStyle = 'ISO, YMD';

-- T06 interval style
SET LOCAL IntervalStyle = 'iso_8601';

-- T07 bytea output
SET LOCAL bytea_output = 'hex';

SELECT
    'AIOS_FRAME'::text,
    'T01-T07'::text,
    'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- L01 material_receipts
LOCK TABLE public.material_receipts
IN ACCESS EXCLUSIVE MODE;

SELECT 'AIOS_FRAME'::text, 'L01'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- L02 material_receipt_items
LOCK TABLE public.material_receipt_items
IN SHARE MODE;

SELECT 'AIOS_FRAME'::text, 'L02'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- L03 inventory_movements
LOCK TABLE public.inventory_movements
IN SHARE MODE;

SELECT 'AIOS_FRAME'::text, 'L03'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- L04 material_stock
LOCK TABLE public.material_stock
IN SHARE MODE;

SELECT 'AIOS_FRAME'::text, 'L04'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- I01 target identity and PostgreSQL version
SELECT current_database() AS database_name,
       current_user AS session_user,
       current_schema() AS schema_name,
       current_setting('server_version') AS server_version;

SELECT 'AIOS_FRAME'::text, 'I01'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- I02 database, schema, and relation identity and ownership
SELECT d.datname AS database_name, dr.rolname AS database_owner,
       n.nspname AS schema_name, nr.rolname AS schema_owner,
       c.relname AS relation_name, c.relkind AS relation_kind,
       cr.rolname AS relation_owner
FROM pg_catalog.pg_database AS d
JOIN pg_catalog.pg_roles AS dr ON dr.oid = d.datdba
JOIN pg_catalog.pg_namespace AS n ON n.nspname = 'public'
JOIN pg_catalog.pg_roles AS nr ON nr.oid = n.nspowner
JOIN pg_catalog.pg_class AS c
  ON c.relnamespace = n.oid AND c.relname = 'material_receipts'
JOIN pg_catalog.pg_roles AS cr ON cr.oid = c.relowner
WHERE d.datname = current_database()
ORDER BY d.datname, n.nspname, c.relname;

SELECT 'AIOS_FRAME'::text, 'I02'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- M01 Migration 0005 creator-column absence
SELECT a.attname AS column_name
FROM pg_catalog.pg_attribute AS a
JOIN pg_catalog.pg_class AS c ON c.oid = a.attrelid
JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relname = 'material_receipts'
  AND a.attname = 'created_by_actor_reference'
  AND a.attnum > 0 AND NOT a.attisdropped
ORDER BY a.attname;

SELECT 'AIOS_FRAME'::text, 'M01'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- M02 Migration 0005 creator-constraint absence
SELECT con.conname AS constraint_name
FROM pg_catalog.pg_constraint AS con
JOIN pg_catalog.pg_class AS c ON c.oid = con.conrelid
JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relname = 'material_receipts'
  AND con.conname = 'material_receipts_created_by_actor_reference_valid'
ORDER BY con.conname;

SELECT 'AIOS_FRAME'::text, 'M02'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- S01 Stage 0.32 exact index
SELECT ci.relname AS index_name, i.indisvalid, i.indisready, i.indisunique,
       i.indnkeyatts,
       pg_catalog.pg_get_indexdef(i.indexrelid, 1, false) AS first_key_definition,
       pg_catalog.pg_get_expr(i.indpred, i.indrelid, false) AS predicate_definition
FROM pg_catalog.pg_index AS i
JOIN pg_catalog.pg_class AS ci ON ci.oid = i.indexrelid
JOIN pg_catalog.pg_class AS ct ON ct.oid = i.indrelid
JOIN pg_catalog.pg_namespace AS n ON n.oid = ct.relnamespace
WHERE n.nspname = 'public'
  AND ct.relname = 'material_receipts'
  AND ci.relname = 'material_receipts_source_asset_active_uidx'
ORDER BY ci.relname;

SELECT 'AIOS_FRAME'::text, 'S01'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- Z01 zero-row hard gate
SELECT COUNT(*) AS material_receipts_count
FROM public.material_receipts;

SELECT 'AIOS_FRAME'::text, 'Z01'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- F01 material_receipts fingerprint
SELECT COUNT(*) AS row_count,
       md5(COALESCE(string_agg(row_to_json(t)::text, E'\n'
                               ORDER BY receipt_id), '')) AS row_digest
FROM public.material_receipts AS t;

SELECT 'AIOS_FRAME'::text, 'F01'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- F02 material_receipt_items fingerprint
SELECT COUNT(*) AS row_count,
       md5(COALESCE(string_agg(row_to_json(t)::text, E'\n'
                               ORDER BY receipt_item_id), '')) AS row_digest
FROM public.material_receipt_items AS t;

SELECT 'AIOS_FRAME'::text, 'F02'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- F03 inventory_movements fingerprint
SELECT COUNT(*) AS row_count,
       md5(COALESCE(string_agg(row_to_json(t)::text, E'\n'
                               ORDER BY movement_id), '')) AS row_digest
FROM public.inventory_movements AS t;

SELECT 'AIOS_FRAME'::text, 'F03'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- F04 material_stock fingerprint
SELECT COUNT(*) AS row_count,
       md5(COALESCE(string_agg(row_to_json(t)::text, E'\n'
                               ORDER BY material_id), '')) AS row_digest
FROM public.material_stock AS t;

SELECT 'AIOS_FRAME'::text, 'F04'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- O01 four-table columns, types, nullability, and defaults
SELECT c.relname AS table_name, a.attnum AS ordinal_position,
       a.attname AS column_name,
       pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
       a.attnotnull AS not_null,
       pg_catalog.pg_get_expr(ad.adbin, ad.adrelid, false) AS default_definition
FROM pg_catalog.pg_attribute AS a
JOIN pg_catalog.pg_class AS c ON c.oid = a.attrelid
JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
LEFT JOIN pg_catalog.pg_attrdef AS ad
  ON ad.adrelid = a.attrelid AND ad.adnum = a.attnum
WHERE n.nspname = 'public'
  AND c.relname IN ('material_receipts', 'material_receipt_items',
                    'inventory_movements', 'material_stock')
  AND a.attnum > 0 AND NOT a.attisdropped
ORDER BY c.relname, a.attnum;

SELECT 'AIOS_FRAME'::text, 'O01'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- O02 four-table constraints
SELECT c.relname AS table_name, con.conname AS constraint_name,
       con.contype AS constraint_type,
       pg_catalog.pg_get_constraintdef(con.oid, false) AS constraint_definition
FROM pg_catalog.pg_constraint AS con
JOIN pg_catalog.pg_class AS c ON c.oid = con.conrelid
JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relname IN ('material_receipts', 'material_receipt_items',
                    'inventory_movements', 'material_stock')
ORDER BY c.relname, con.conname;

SELECT 'AIOS_FRAME'::text, 'O02'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- O03 four-table indexes
SELECT ct.relname AS table_name, ci.relname AS index_name,
       i.indisvalid, i.indisready, i.indisunique,
       pg_catalog.pg_get_indexdef(i.indexrelid) AS index_definition,
       pg_catalog.pg_get_expr(i.indpred, i.indrelid, false) AS predicate_definition
FROM pg_catalog.pg_index AS i
JOIN pg_catalog.pg_class AS ci ON ci.oid = i.indexrelid
JOIN pg_catalog.pg_class AS ct ON ct.oid = i.indrelid
JOIN pg_catalog.pg_namespace AS n ON n.oid = ct.relnamespace
WHERE n.nspname = 'public'
  AND ct.relname IN ('material_receipts', 'material_receipt_items',
                     'inventory_movements', 'material_stock')
ORDER BY ct.relname, ci.relname;

SELECT 'AIOS_FRAME'::text, 'O03'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- O04 four-table owners and ACLs
SELECT c.relname AS table_name, r.rolname AS table_owner, c.relacl AS table_acl
FROM pg_catalog.pg_class AS c
JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
JOIN pg_catalog.pg_roles AS r ON r.oid = c.relowner
WHERE n.nspname = 'public'
  AND c.relname IN ('material_receipts', 'material_receipt_items',
                    'inventory_movements', 'material_stock')
ORDER BY c.relname;

SELECT 'AIOS_FRAME'::text, 'O04'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- O05 four-table non-internal triggers
SELECT c.relname AS table_name, t.tgname AS trigger_name,
       pg_catalog.pg_get_triggerdef(t.oid, false) AS trigger_definition
FROM pg_catalog.pg_trigger AS t
JOIN pg_catalog.pg_class AS c ON c.oid = t.tgrelid
JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relname IN ('material_receipts', 'material_receipt_items',
                    'inventory_movements', 'material_stock')
  AND NOT t.tgisinternal
ORDER BY c.relname, t.tgname;

SELECT 'AIOS_FRAME'::text, 'O05'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- O06 relevant trigger functions
SELECT c.relname AS table_name, t.tgname AS trigger_name,
       pn.nspname AS function_schema, p.proname AS function_name,
       pg_catalog.pg_get_functiondef(p.oid) AS function_definition
FROM pg_catalog.pg_trigger AS t
JOIN pg_catalog.pg_class AS c ON c.oid = t.tgrelid
JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
JOIN pg_catalog.pg_proc AS p ON p.oid = t.tgfoid
JOIN pg_catalog.pg_namespace AS pn ON pn.oid = p.pronamespace
WHERE n.nspname = 'public'
  AND c.relname IN ('material_receipts', 'material_receipt_items',
                    'inventory_movements', 'material_stock')
  AND NOT t.tgisinternal
ORDER BY c.relname, t.tgname, pn.nspname, p.proname;

SELECT 'AIOS_FRAME'::text, 'O06'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- O07 public schema owner and ACL
SELECT n.nspname AS schema_name, r.rolname AS schema_owner,
       n.nspacl AS schema_acl
FROM pg_catalog.pg_namespace AS n
JOIN pg_catalog.pg_roles AS r ON r.oid = n.nspowner
WHERE n.nspname = 'public'
ORDER BY n.nspname;

SELECT 'AIOS_FRAME'::text, 'O07'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- O08 extensions
SELECT e.extname AS extension_name, e.extversion AS extension_version,
       n.nspname AS extension_schema
FROM pg_catalog.pg_extension AS e
JOIN pg_catalog.pg_namespace AS n ON n.oid = e.extnamespace
ORDER BY e.extname;

SELECT 'AIOS_FRAME'::text, 'O08'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- R01 frozen role attributes
SELECT r.rolname, r.rolsuper, r.rolinherit, r.rolcreaterole,
       r.rolcreatedb, r.rolcanlogin, r.rolreplication, r.rolbypassrls
FROM pg_catalog.pg_roles AS r
WHERE r.rolname IN (
 'aios', 'aios_material_receipt_candidate_runtime',
 'aios_material_receipt_candidate_writer',
 'aios_material_inventory_posting_runtime',
 'aios_material_inventory_posting_writer', 'aios_material_stock_reader')
ORDER BY r.rolname;

SELECT 'AIOS_FRAME'::text, 'R01'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- R02 frozen role memberships and ADMIN OPTION
SELECT mr.rolname AS member_name, gr.rolname AS granted_role_name, m.admin_option
FROM pg_catalog.pg_auth_members AS m
JOIN pg_catalog.pg_roles AS gr ON gr.oid = m.roleid
JOIN pg_catalog.pg_roles AS mr ON mr.oid = m.member
WHERE mr.rolname IN (
 'aios', 'aios_material_receipt_candidate_runtime',
 'aios_material_receipt_candidate_writer',
 'aios_material_inventory_posting_runtime',
 'aios_material_inventory_posting_writer', 'aios_material_stock_reader')
   OR gr.rolname IN (
 'aios', 'aios_material_receipt_candidate_runtime',
 'aios_material_receipt_candidate_writer',
 'aios_material_inventory_posting_runtime',
 'aios_material_inventory_posting_writer', 'aios_material_stock_reader')
ORDER BY mr.rolname, gr.rolname;

SELECT 'AIOS_FRAME'::text, 'R02'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- R03 frozen role table privileges
SELECT g.grantee, g.table_schema, g.table_name,
       g.privilege_type, g.is_grantable
FROM information_schema.role_table_grants AS g
WHERE g.grantee IN (
 'aios', 'aios_material_receipt_candidate_runtime',
 'aios_material_receipt_candidate_writer',
 'aios_material_inventory_posting_runtime',
 'aios_material_inventory_posting_writer', 'aios_material_stock_reader')
  AND g.table_schema = 'public'
  AND g.table_name IN ('material_receipts', 'material_receipt_items',
                       'inventory_movements', 'material_stock')
ORDER BY g.grantee, g.table_name, g.privilege_type;

SELECT 'AIOS_FRAME'::text, 'R03'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- R04 frozen role column privileges
SELECT p.grantee, p.table_schema, p.table_name, p.column_name,
       p.privilege_type, p.is_grantable
FROM information_schema.column_privileges AS p
WHERE p.grantee IN (
 'aios', 'aios_material_receipt_candidate_runtime',
 'aios_material_receipt_candidate_writer',
 'aios_material_inventory_posting_runtime',
 'aios_material_inventory_posting_writer', 'aios_material_stock_reader')
  AND p.table_schema = 'public'
  AND p.table_name IN ('material_receipts', 'material_receipt_items',
                       'inventory_movements', 'material_stock')
ORDER BY p.grantee, p.table_name, p.column_name, p.privilege_type;

SELECT 'AIOS_FRAME'::text, 'R04'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- X01 exact Migration 0005 UP artifact insertion
-- AIOS_MIGRATION_0005_UP_EXACT_ARTIFACT_INSERTION_POINT

SELECT 'AIOS_FRAME'::text, 'X01'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- V01 creator column structural verifier
SELECT a.attname AS column_name,
       pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
       a.attnotnull AS not_null,
       pg_catalog.pg_get_expr(ad.adbin, ad.adrelid, false) AS default_definition
FROM pg_catalog.pg_attribute AS a
JOIN pg_catalog.pg_class AS c ON c.oid = a.attrelid
JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
LEFT JOIN pg_catalog.pg_attrdef AS ad
  ON ad.adrelid = a.attrelid AND ad.adnum = a.attnum
WHERE n.nspname = 'public'
  AND c.relname = 'material_receipts'
  AND a.attname = 'created_by_actor_reference'
  AND a.attnum > 0 AND NOT a.attisdropped
ORDER BY a.attname;

SELECT 'AIOS_FRAME'::text, 'V01'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- V02 creator CHECK structural verifier
SELECT con.conname AS constraint_name, con.contype AS constraint_type,
       pg_catalog.pg_get_constraintdef(con.oid, false) AS constraint_definition
FROM pg_catalog.pg_constraint AS con
JOIN pg_catalog.pg_class AS c ON c.oid = con.conrelid
JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relname = 'material_receipts'
  AND con.conname = 'material_receipts_created_by_actor_reference_valid'
ORDER BY con.conname;

SELECT 'AIOS_FRAME'::text, 'V02'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- V03 no creator-provenance index verifier
SELECT ci.relname AS index_name,
       pg_catalog.pg_get_indexdef(i.indexrelid) AS index_definition
FROM pg_catalog.pg_index AS i
JOIN pg_catalog.pg_class AS ci ON ci.oid = i.indexrelid
JOIN pg_catalog.pg_class AS ct ON ct.oid = i.indrelid
JOIN pg_catalog.pg_namespace AS n ON n.oid = ct.relnamespace
WHERE n.nspname = 'public'
  AND ct.relname = 'material_receipts'
  AND pg_catalog.pg_get_indexdef(i.indexrelid) LIKE '%created_by_actor_reference%'
ORDER BY ci.relname;

SELECT 'AIOS_FRAME'::text, 'V03'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- V04 Stage 0.32 exact index preservation verifier
SELECT ci.relname AS index_name, i.indisvalid, i.indisready, i.indisunique,
       i.indnkeyatts,
       pg_catalog.pg_get_indexdef(i.indexrelid, 1, false) AS first_key_definition,
       pg_catalog.pg_get_expr(i.indpred, i.indrelid, false) AS predicate_definition
FROM pg_catalog.pg_index AS i
JOIN pg_catalog.pg_class AS ci ON ci.oid = i.indexrelid
JOIN pg_catalog.pg_class AS ct ON ct.oid = i.indrelid
JOIN pg_catalog.pg_namespace AS n ON n.oid = ct.relnamespace
WHERE n.nspname = 'public'
  AND ct.relname = 'material_receipts'
  AND ci.relname = 'material_receipts_source_asset_active_uidx'
ORDER BY ci.relname;

SELECT 'AIOS_FRAME'::text, 'V04'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- V05 exact creator-column privilege verifier
SELECT p.grantee, p.table_schema, p.table_name, p.column_name,
       p.privilege_type, p.is_grantable
FROM information_schema.column_privileges AS p
WHERE p.grantee IN (
 'aios_material_receipt_candidate_writer',
 'aios_material_inventory_posting_runtime',
 'aios_material_inventory_posting_writer', 'aios_material_stock_reader')
  AND p.table_schema = 'public'
  AND p.table_name = 'material_receipts'
  AND p.column_name = 'created_by_actor_reference'
ORDER BY p.grantee, p.privilege_type;

SELECT 'AIOS_FRAME'::text, 'V05'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- PF01 material_receipts fingerprint
SELECT COUNT(*) AS row_count,
       md5(COALESCE(string_agg(row_to_json(t)::text, E'\n'
                               ORDER BY receipt_id), '')) AS row_digest
FROM public.material_receipts AS t;

SELECT 'AIOS_FRAME'::text, 'PF01'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- PF02 material_receipt_items fingerprint
SELECT COUNT(*) AS row_count,
       md5(COALESCE(string_agg(row_to_json(t)::text, E'\n'
                               ORDER BY receipt_item_id), '')) AS row_digest
FROM public.material_receipt_items AS t;

SELECT 'AIOS_FRAME'::text, 'PF02'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- PF03 inventory_movements fingerprint
SELECT COUNT(*) AS row_count,
       md5(COALESCE(string_agg(row_to_json(t)::text, E'\n'
                               ORDER BY movement_id), '')) AS row_digest
FROM public.inventory_movements AS t;

SELECT 'AIOS_FRAME'::text, 'PF03'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- PF04 material_stock fingerprint
SELECT COUNT(*) AS row_count,
       md5(COALESCE(string_agg(row_to_json(t)::text, E'\n'
                               ORDER BY material_id), '')) AS row_digest
FROM public.material_stock AS t;

SELECT 'AIOS_FRAME'::text, 'PF04'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- PO01 four-table columns, types, nullability, and defaults
SELECT c.relname AS table_name, a.attnum AS ordinal_position,
       a.attname AS column_name,
       pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
       a.attnotnull AS not_null,
       pg_catalog.pg_get_expr(ad.adbin, ad.adrelid, false) AS default_definition
FROM pg_catalog.pg_attribute AS a
JOIN pg_catalog.pg_class AS c ON c.oid = a.attrelid
JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
LEFT JOIN pg_catalog.pg_attrdef AS ad
  ON ad.adrelid = a.attrelid AND ad.adnum = a.attnum
WHERE n.nspname = 'public'
  AND c.relname IN ('material_receipts', 'material_receipt_items',
                    'inventory_movements', 'material_stock')
  AND a.attnum > 0 AND NOT a.attisdropped
ORDER BY c.relname, a.attnum;

SELECT 'AIOS_FRAME'::text, 'PO01'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- PO02 four-table constraints
SELECT c.relname AS table_name, con.conname AS constraint_name,
       con.contype AS constraint_type,
       pg_catalog.pg_get_constraintdef(con.oid, false) AS constraint_definition
FROM pg_catalog.pg_constraint AS con
JOIN pg_catalog.pg_class AS c ON c.oid = con.conrelid
JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relname IN ('material_receipts', 'material_receipt_items',
                    'inventory_movements', 'material_stock')
ORDER BY c.relname, con.conname;

SELECT 'AIOS_FRAME'::text, 'PO02'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- PO03 four-table indexes
SELECT ct.relname AS table_name, ci.relname AS index_name,
       i.indisvalid, i.indisready, i.indisunique,
       pg_catalog.pg_get_indexdef(i.indexrelid) AS index_definition,
       pg_catalog.pg_get_expr(i.indpred, i.indrelid, false) AS predicate_definition
FROM pg_catalog.pg_index AS i
JOIN pg_catalog.pg_class AS ci ON ci.oid = i.indexrelid
JOIN pg_catalog.pg_class AS ct ON ct.oid = i.indrelid
JOIN pg_catalog.pg_namespace AS n ON n.oid = ct.relnamespace
WHERE n.nspname = 'public'
  AND ct.relname IN ('material_receipts', 'material_receipt_items',
                     'inventory_movements', 'material_stock')
ORDER BY ct.relname, ci.relname;

SELECT 'AIOS_FRAME'::text, 'PO03'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- PO04 four-table owners and ACLs
SELECT c.relname AS table_name, r.rolname AS table_owner, c.relacl AS table_acl
FROM pg_catalog.pg_class AS c
JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
JOIN pg_catalog.pg_roles AS r ON r.oid = c.relowner
WHERE n.nspname = 'public'
  AND c.relname IN ('material_receipts', 'material_receipt_items',
                    'inventory_movements', 'material_stock')
ORDER BY c.relname;

SELECT 'AIOS_FRAME'::text, 'PO04'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- PO05 four-table non-internal triggers
SELECT c.relname AS table_name, t.tgname AS trigger_name,
       pg_catalog.pg_get_triggerdef(t.oid, false) AS trigger_definition
FROM pg_catalog.pg_trigger AS t
JOIN pg_catalog.pg_class AS c ON c.oid = t.tgrelid
JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relname IN ('material_receipts', 'material_receipt_items',
                    'inventory_movements', 'material_stock')
  AND NOT t.tgisinternal
ORDER BY c.relname, t.tgname;

SELECT 'AIOS_FRAME'::text, 'PO05'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- PO06 relevant trigger functions
SELECT c.relname AS table_name, t.tgname AS trigger_name,
       pn.nspname AS function_schema, p.proname AS function_name,
       pg_catalog.pg_get_functiondef(p.oid) AS function_definition
FROM pg_catalog.pg_trigger AS t
JOIN pg_catalog.pg_class AS c ON c.oid = t.tgrelid
JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
JOIN pg_catalog.pg_proc AS p ON p.oid = t.tgfoid
JOIN pg_catalog.pg_namespace AS pn ON pn.oid = p.pronamespace
WHERE n.nspname = 'public'
  AND c.relname IN ('material_receipts', 'material_receipt_items',
                    'inventory_movements', 'material_stock')
  AND NOT t.tgisinternal
ORDER BY c.relname, t.tgname, pn.nspname, p.proname;

SELECT 'AIOS_FRAME'::text, 'PO06'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- PO07 public schema owner and ACL
SELECT n.nspname AS schema_name, r.rolname AS schema_owner,
       n.nspacl AS schema_acl
FROM pg_catalog.pg_namespace AS n
JOIN pg_catalog.pg_roles AS r ON r.oid = n.nspowner
WHERE n.nspname = 'public'
ORDER BY n.nspname;

SELECT 'AIOS_FRAME'::text, 'PO07'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- PO08 extensions
SELECT e.extname AS extension_name, e.extversion AS extension_version,
       n.nspname AS extension_schema
FROM pg_catalog.pg_extension AS e
JOIN pg_catalog.pg_namespace AS n ON n.oid = e.extnamespace
ORDER BY e.extname;

SELECT 'AIOS_FRAME'::text, 'PO08'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- PR01 frozen role attributes
SELECT r.rolname, r.rolsuper, r.rolinherit, r.rolcreaterole,
       r.rolcreatedb, r.rolcanlogin, r.rolreplication, r.rolbypassrls
FROM pg_catalog.pg_roles AS r
WHERE r.rolname IN (
 'aios', 'aios_material_receipt_candidate_runtime',
 'aios_material_receipt_candidate_writer',
 'aios_material_inventory_posting_runtime',
 'aios_material_inventory_posting_writer', 'aios_material_stock_reader')
ORDER BY r.rolname;

SELECT 'AIOS_FRAME'::text, 'PR01'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- PR02 frozen role memberships and ADMIN OPTION
SELECT mr.rolname AS member_name, gr.rolname AS granted_role_name, m.admin_option
FROM pg_catalog.pg_auth_members AS m
JOIN pg_catalog.pg_roles AS gr ON gr.oid = m.roleid
JOIN pg_catalog.pg_roles AS mr ON mr.oid = m.member
WHERE mr.rolname IN (
 'aios', 'aios_material_receipt_candidate_runtime',
 'aios_material_receipt_candidate_writer',
 'aios_material_inventory_posting_runtime',
 'aios_material_inventory_posting_writer', 'aios_material_stock_reader')
   OR gr.rolname IN (
 'aios', 'aios_material_receipt_candidate_runtime',
 'aios_material_receipt_candidate_writer',
 'aios_material_inventory_posting_runtime',
 'aios_material_inventory_posting_writer', 'aios_material_stock_reader')
ORDER BY mr.rolname, gr.rolname;

SELECT 'AIOS_FRAME'::text, 'PR02'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- PR03 frozen role table privileges
SELECT g.grantee, g.table_schema, g.table_name,
       g.privilege_type, g.is_grantable
FROM information_schema.role_table_grants AS g
WHERE g.grantee IN (
 'aios', 'aios_material_receipt_candidate_runtime',
 'aios_material_receipt_candidate_writer',
 'aios_material_inventory_posting_runtime',
 'aios_material_inventory_posting_writer', 'aios_material_stock_reader')
  AND g.table_schema = 'public'
  AND g.table_name IN ('material_receipts', 'material_receipt_items',
                       'inventory_movements', 'material_stock')
ORDER BY g.grantee, g.table_name, g.privilege_type;

SELECT 'AIOS_FRAME'::text, 'PR03'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- PR04 frozen role column privileges
SELECT p.grantee, p.table_schema, p.table_name, p.column_name,
       p.privilege_type, p.is_grantable
FROM information_schema.column_privileges AS p
WHERE p.grantee IN (
 'aios', 'aios_material_receipt_candidate_runtime',
 'aios_material_receipt_candidate_writer',
 'aios_material_inventory_posting_runtime',
 'aios_material_inventory_posting_writer', 'aios_material_stock_reader')
  AND p.table_schema = 'public'
  AND p.table_name IN ('material_receipts', 'material_receipt_items',
                       'inventory_movements', 'material_stock')
ORDER BY p.grantee, p.table_name, p.column_name, p.privilege_type;

SELECT 'AIOS_FRAME'::text, 'PR04'::text,
       'a3e1a015-c078-44b4-a618-f6c7f49831f7'::text;

-- C01 success transaction close
COMMIT;
