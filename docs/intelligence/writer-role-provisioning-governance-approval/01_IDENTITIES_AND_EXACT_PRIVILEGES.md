# Frozen Identities and Exact Privileges

## Identities

Privilege roles:

- `aios_material_receipt_candidate_writer`
- `aios_material_inventory_posting_writer`

Both are `NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION
NOBYPASSRLS`, own nothing, and have no administrative memberships.

Runtime identities:

- `aios_material_receipt_candidate_runtime`
- `aios_material_inventory_posting_runtime`

Both are `LOGIN INHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION
NOBYPASSRLS` and own nothing. Each runtime is a member only of its corresponding
NOLOGIN role. Cross-membership and reader-role membership are prohibited.

## Candidate writer

Grant `CONNECT` on database `aios`, `USAGE` on schema `public`, and table-level
`SELECT` on `material_receipts`, `material_receipt_items`, and `material_stock`.

Column-level `INSERT` on `material_receipts` is limited to:

`receipt_id`, `supplier_name`, `document_number`, `document_date`,
`received_at`, `source_asset_reference`.

Column-level `UPDATE` on `material_receipts` is limited to:

`supplier_name`, `document_number`, `document_date`, `received_at`,
`source_asset_reference`, `status`, `version`, `confirmed_version`,
`confirmed_at`, `confirmation_actor_reference`, `updated_at`.

Column-level `INSERT` on `material_receipt_items` is limited to:

`receipt_item_id`, `receipt_id`, `line_number`,
`candidate_material_description`, `canonical_display_name`,
`size_description`, `specification`, `material_id`, `full_colly_count`,
`qty_per_full_colly`, `partial_qty`, `total_qty`, `unit`.

Column-level `UPDATE` on `material_receipt_items` is limited to:

`line_number`, `candidate_material_description`, `canonical_display_name`,
`size_description`, `specification`, `material_id`, `full_colly_count`,
`qty_per_full_colly`, `partial_qty`, `total_qty`, `unit`, `status`,
`updated_at`.

Changing `line_number` remains a pre-confirmation application rule. No update is
granted on receipt/item identity, item parent link, or `created_at`. Database
defaults initialize omitted status, version, and timestamp fields. Candidate
authority has no privilege on `inventory_movements` and no write privilege on
`material_stock`.

## Posting writer

Grant `CONNECT` on `aios`, `USAGE` on `public`, and table-level `SELECT` on all
four governed tables.

Column-level `UPDATE` is limited to:

- `material_receipts`: `status`, `updated_at`
- `material_receipt_items`: `status`, `updated_at`
- `material_stock`: `stock_qty`, `updated_at`

Column-level `INSERT` on `inventory_movements` is limited to:

`movement_id`, `material_id`, `movement_type`, `quantity_delta`, `unit`,
`source_receipt_item_id`, `occurred_at`, `posting_actor_reference`,
`balance_before`, `balance_after`.

Defaults supply `posted_at` and `created_at`. No movement UPDATE, DELETE, or
TRUNCATE is granted. No stock INSERT, DELETE, TRUNCATE, or update of
`material_id`, `name`, `unit`, or `is_active` is granted. Neither writer gets
unrelated-table privileges, DDL, role administration, ownership, or default
privileges.
