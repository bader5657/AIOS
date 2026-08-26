# Frozen Filesystem, Identities, and Privileges

## Filesystem contract

Before lock mutation, secret generation, staging, or database mutation, the
helper must validate exactly:

- `/opt/aios`: directory, `root:aiosadmin`, mode `0755`;
- `/opt/aios/runtime`: directory, `root:aiosadmin`, mode `0755`;
- `/opt/aios/runtime/config`: directory, `root:aiosadmin`, mode `0750`;
- `/opt/aios/runtime/config/runtime.env`: regular non-symlink file,
  `root:aiosadmin`, mode `0640`, link count exactly one.

The retained lock is fixed at
`/opt/aios/runtime/config/.runtime.env.writer-bootstrap.lock`. It must be a
regular non-symlink, single-link `root:aiosadmin` object at mode `0600` and must
be exclusively locked and revalidated. Any mismatch stops execution.

Only these assignments may be added or replaced, preserving all unrelated bytes
and ordering:

- `AIOS_MATERIAL_RECEIPT_CANDIDATE_DB_PASSWORD`
- `AIOS_MATERIAL_INVENTORY_POSTING_DB_PASSWORD`

The installed environment file must remain `root:aiosadmin`, mode `0640`,
single-link, and durably installed by same-directory atomic replacement with the
governed fsync and installed-file revalidation sequence.

## Exact identities and attributes

Only these identities may be created:

- `aios_material_receipt_candidate_writer`: NOLOGIN;
- `aios_material_receipt_candidate_runtime`: LOGIN, INHERIT;
- `aios_material_inventory_posting_writer`: NOLOGIN;
- `aios_material_inventory_posting_runtime`: LOGIN, INHERIT.

All four are NOSUPERUSER, NOCREATEDB, NOCREATEROLE, NOREPLICATION, and
NOBYPASSRLS. Membership is exactly candidate writer granted to candidate runtime
and posting writer granted to posting runtime, without ADMIN OPTION. All four
must own zero database, schema, relation, sequence, routine, or other
ownership-dependent objects.

## Exact candidate matrix

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

It receives no `inventory_movements` privilege, stock write privilege, grant
option, ownership, or unrelated privilege.

## Exact posting matrix

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
stock INSERT/DELETE, stock identity/name/unit/is_active update, grant option,
ownership, or unrelated privilege. PUBLIC must have no governed table or column
privilege, including effective or default ACL paths accepted by the helper.
