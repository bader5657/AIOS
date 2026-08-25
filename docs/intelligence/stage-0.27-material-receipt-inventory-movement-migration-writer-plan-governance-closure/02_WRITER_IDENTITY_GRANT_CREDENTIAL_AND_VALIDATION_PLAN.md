# Writer Identity, Grant, Credential, and Validation Plan

## Frozen identities and attributes

The candidate privilege role is
`aios_material_receipt_candidate_writer`. It is `NOLOGIN`, `NOSUPERUSER`,
`NOCREATEDB`, `NOCREATEROLE`, `NOREPLICATION`, and `NOBYPASSRLS`, with no
ownership or admin membership.

Its runtime identity is `aios_material_receipt_candidate_runtime`. It is a
`LOGIN` with `INHERIT`, `NOSUPERUSER`, `NOCREATEDB`, `NOCREATEROLE`,
`NOREPLICATION`, and `NOBYPASSRLS`, owns nothing, has no direct table privileges,
and belongs only to its matching candidate privilege role.

The posting privilege role is
`aios_material_inventory_posting_writer`, with the same restricted NOLOGIN
attributes. Its runtime identity is
`aios_material_inventory_posting_runtime`, with the same restricted LOGIN and
INHERIT attributes, no direct table privileges, and membership only in the
matching posting privilege role.

INHERIT is approved because each runtime login has exactly one isolated
privilege-role membership. Cross-membership, admin option, broad shared
identities, and application role switching are prohibited.

## Candidate grant matrix

The candidate privilege role receives only database `CONNECT`, schema `USAGE`,
table-level `SELECT` on receipts and items, column-bounded creation and update
access for candidate/review/version/confirmation fields, and read-only `SELECT`
on `material_stock` for exact material resolution and unit review.

Creation-time insert lists may contain externally generated IDs and parent links.
Post-creation update lists exclude `receipt_id`, `receipt_item_id`, and an
existing item's parent `receipt_id`. Exact insert and update column lists must be
frozen alongside the future repository and provisioning implementation. Full
table update must not be substituted.

The candidate role has no privilege on `inventory_movements` by default, no
stock insert/update/delete, and no unrelated-table access. Movement access may
not be added without new evidence and governance approval.

## Posting grant matrix

The posting privilege role receives only database `CONNECT`, schema `USAGE`, and:

- receipt `SELECT` plus column-level update of `status` and `updated_at`;
- item `SELECT` plus column-level update of `status` and `updated_at`;
- movement `SELECT` and `INSERT`;
- material-stock `SELECT` plus column-level update of `stock_qty` and
  `updated_at`.

It receives no stock insert/delete/truncate; no movement update/delete/truncate;
no receipt/item delete; no unrelated-table access; and no DDL, ownership, default
privilege, role-management, or grant authority. This makes it technically unable
to rewrite source, confirmation, material, packaging, unit, or movement history.
Movement immutability requires no v1 trigger.

## Ownership, defaults, reader, and PUBLIC

The existing controlled database/schema/table owner remains unchanged. Neither
privilege role nor runtime login owns a database, schema, table, sequence,
routine, or other object. Default privileges are not modified, so future tables
do not become accessible automatically.

`aios_material_stock_reader` remains unchanged and has no writer membership; no
writer receives reader membership. Future verification records environmental
PUBLIC defaults separately and neither silently revokes nor broadens them.
Effective-access reports distinguish dedicated grants, inherited-role access,
and PUBLIC/environmental access.

## Credentials, collision, provisioning, and validation

Each runtime login receives an independent strong secret only during separately
authorized provisioning. Secrets live only in the runtime secret facility and
never in source control, GitHub, governance documents, command output, logs,
Telegram, Brain, or session journals.

The candidate service uses only the candidate runtime identity; authoritative
posting uses only the posting runtime identity; current-stock retrieval keeps its
dedicated reader. Brain receives no database credential, handle, generic SQL, or
writer authority.

Provisioning first verifies absence of all four frozen identifiers. An unexpected
collision stops the operation without reuse, alteration, rename, membership, or
drop. A later controlled authority may create privilege roles, securely create
runtime identities, apply exact grants, grant one-to-one membership, and validate
attributes and effective permissions. No business-row mutation probe is allowed.

Validation uses database-, schema-, table-, and column-privilege functions plus
role-membership, ownership, and ACL catalogs. It proves every expected allow and
deny cell, distinguishes PUBLIC access, and verifies the absence of ownership,
cross-membership, grant option, admin option, and unrelated-table access.
