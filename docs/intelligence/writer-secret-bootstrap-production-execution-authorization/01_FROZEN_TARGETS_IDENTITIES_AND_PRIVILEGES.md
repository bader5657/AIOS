# Frozen Targets, Identities, and Privileges

## Filesystem contract

The authorized helper must validate these exact existing objects before any
lock mutation, secret generation, tempfile creation, or database mutation:

- `/opt/aios`: directory, `root:aiosadmin`, mode `0755`;
- `/opt/aios/runtime`: directory, `root:aiosadmin`, mode `0755`;
- `/opt/aios/runtime/config`: directory, `root:aiosadmin`, mode `0750`;
- `/opt/aios/runtime/config/runtime.env`: regular non-symlink file,
  `root:aiosadmin`, mode `0640`, link count exactly one.

The retained lock is fixed at
`/opt/aios/runtime/config/.runtime.env.writer-bootstrap.lock`, must be a regular
non-symlink single-link `root:aiosadmin` object with mode `0600`, and is used
with an exclusive nonblocking lock. A malicious or mismatched existing object
is a stop condition.

Only these two byte assignments may be replaced or appended while all unrelated
bytes and ordering remain unchanged:

- `AIOS_MATERIAL_RECEIPT_CANDIDATE_DB_PASSWORD`
- `AIOS_MATERIAL_INVENTORY_POSTING_DB_PASSWORD`

The installed file remains `root:aiosadmin` mode `0640` after same-directory
atomic replacement and durability verification.

## PostgreSQL target and identities

Every connection is frozen to Unix socket directory `/var/run/postgresql`, port
`5432`, database `aios`; TCP, `localhost`, `127.0.0.1`, wildcard hosts, and
environment overrides are prohibited.

The only identities authorized for creation are:

- `aios_material_receipt_candidate_writer`: NOLOGIN;
- `aios_material_receipt_candidate_runtime`: LOGIN, INHERIT;
- `aios_material_inventory_posting_writer`: NOLOGIN;
- `aios_material_inventory_posting_runtime`: LOGIN, INHERIT.

All four must be NOSUPERUSER, NOCREATEDB, NOCREATEROLE, NOREPLICATION, and
NOBYPASSRLS. Membership is exactly candidate writer to candidate runtime and
posting writer to posting runtime, with no ADMIN OPTION or additional role.
All four own zero database, schema, relation, sequence, routine, or other
ownership-dependent objects.

## Candidate matrix

`aios_material_receipt_candidate_writer` receives only:

- CONNECT on database `aios` and USAGE on schema `public`;
- SELECT on `public.material_receipts`, `public.material_receipt_items`, and
  `public.material_stock`;
- INSERT on `public.material_receipts` columns `receipt_id`, `supplier_name`,
  `document_number`, `document_date`, `received_at`, `source_asset_reference`;
- UPDATE on `public.material_receipts` columns `supplier_name`,
  `document_number`, `document_date`, `received_at`, `source_asset_reference`,
  `status`, `version`, `confirmed_version`, `confirmed_at`,
  `confirmation_actor_reference`, `updated_at`;
- INSERT on `public.material_receipt_items` columns `receipt_item_id`,
  `receipt_id`, `line_number`, `candidate_material_description`,
  `canonical_display_name`, `size_description`, `specification`, `material_id`,
  `full_colly_count`, `qty_per_full_colly`, `partial_qty`, `total_qty`, `unit`;
- UPDATE on `public.material_receipt_items` columns `line_number`,
  `candidate_material_description`, `canonical_display_name`,
  `size_description`, `specification`, `material_id`, `full_colly_count`,
  `qty_per_full_colly`, `partial_qty`, `total_qty`, `unit`, `status`,
  `updated_at`.

It receives no `inventory_movements` access, no stock write access, no grant
option, and no unrelated privilege.

## Posting matrix

`aios_material_inventory_posting_writer` receives only:

- CONNECT on database `aios` and USAGE on schema `public`;
- SELECT on all four governed tables;
- UPDATE of `status`, `updated_at` on `public.material_receipts` and
  `public.material_receipt_items`;
- INSERT on `public.inventory_movements` columns `movement_id`, `material_id`,
  `movement_type`, `quantity_delta`, `unit`, `source_receipt_item_id`,
  `occurred_at`, `posting_actor_reference`, `balance_before`, `balance_after`;
- UPDATE of `stock_qty`, `updated_at` on `public.material_stock`.

It receives no broader receipt/item edit, movement UPDATE/DELETE/TRUNCATE,
stock INSERT/DELETE, stock identity/name/unit/is_active update, grant option, or
unrelated privilege. PUBLIC receives no governed table or column privilege.
