# Writer Identities, Attributes, and Exact Grant Matrix

## Identity model

The candidate privilege role is
`aios_material_receipt_candidate_writer`; its sole runtime login is
`aios_material_receipt_candidate_runtime`. The posting privilege role is
`aios_material_inventory_posting_writer`; its sole runtime login is
`aios_material_inventory_posting_runtime`.

Privilege roles are `NOLOGIN`, `NOSUPERUSER`, `NOCREATEDB`, `NOCREATEROLE`,
`NOREPLICATION`, and `NOBYPASSRLS`, with no ownership or admin membership.
Runtime identities are `LOGIN`, `INHERIT`, `NOSUPERUSER`, `NOCREATEDB`,
`NOCREATEROLE`, `NOREPLICATION`, and `NOBYPASSRLS`, with no ownership or direct
object privileges. Each runtime identity belongs only to its corresponding
NOLOGIN role, without admin option. Cross-membership and reader-role membership
are prohibited.

## Candidate privilege role

The role receives database `CONNECT`, schema `USAGE`, table-level `SELECT` on
`material_receipts` and `material_receipt_items`, and table-level `SELECT` on
`material_stock` for exact material resolution and unit review. It receives no
privilege on `inventory_movements` and no unrelated-table access.

The exact receipt INSERT columns are:

- `receipt_id`;
- `supplier_name`;
- `document_number`;
- `document_date`;
- `received_at`;
- `source_asset_reference`.

`status`, `version`, confirmation fields, `created_at`, and `updated_at` use their
deployed database defaults on creation. The exact receipt UPDATE columns are:

- `supplier_name`, `document_number`, `document_date`, `received_at`;
- `source_asset_reference`, `status`, `version`, `confirmed_version`;
- `confirmed_at`, `confirmation_actor_reference`, `updated_at`.

`receipt_id` and `created_at` are not updateable.

The exact receipt-item INSERT columns are:

- `receipt_item_id`, `receipt_id`, `line_number`;
- `candidate_material_description`, `canonical_display_name`;
- `size_description`, `specification`, `material_id`;
- `full_colly_count`, `qty_per_full_colly`, `partial_qty`, `total_qty`, `unit`.

Item `status`, `created_at`, and `updated_at` use database defaults on creation.
The exact item UPDATE columns are:

- `line_number`;
- `candidate_material_description`, `canonical_display_name`;
- `size_description`, `specification`, `material_id`;
- `full_colly_count`, `qty_per_full_colly`, `partial_qty`, `total_qty`;
- `unit`, `status`, `updated_at`.

`line_number` is editable only through the governed pre-confirmation candidate
workflow so an operator can correct line ordering. The repository must reject
such edits after confirmation or posting. `receipt_item_id`, parent `receipt_id`,
and `created_at` are never updateable.

The candidate role receives no stock INSERT/UPDATE/DELETE, movement privilege,
delete, truncate, DDL, role management, or ownership.

## Posting privilege role

The posting role receives database `CONNECT`, schema `USAGE`, and:

- `SELECT` on `material_receipts`, with column UPDATE only for `status` and
  `updated_at`;
- `SELECT` on `material_receipt_items`, with column UPDATE only for `status` and
  `updated_at`;
- `SELECT` on `inventory_movements`;
- column INSERT on `inventory_movements` only for `movement_id`, `material_id`,
  `movement_type`, `quantity_delta`, `unit`, `source_receipt_item_id`,
  `occurred_at`, `posting_actor_reference`, `balance_before`, and
  `balance_after`;
- `SELECT` on `material_stock`, with column UPDATE only for `stock_qty` and
  `updated_at`.

Movement `posted_at` and `created_at` use database defaults. The posting role has
no receipt/item delete, movement update/delete/truncate, stock insert/delete/
truncate, update of another stock column, unrelated-table access, DDL, ownership,
role management, or grant authority.
