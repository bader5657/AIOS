# Receipt and Item Schema Contract

## `public.material_receipts`

The frozen columns are:

| Column | PostgreSQL type | Nullability/default |
|---|---|---|
| `receipt_id` | `UUID` | primary key, not null, externally generated, no default |
| `supplier_name` | `TEXT` | not null |
| `document_number` | `TEXT` | null |
| `document_date` | `DATE` | null |
| `received_at` | `TIMESTAMPTZ` | not null, explicitly supplied |
| `source_asset_reference` | `TEXT` | not null |
| `status` | `TEXT` | not null, default `EXTRACTED` |
| `version` | `INTEGER` | not null, default `1` |
| `confirmed_version` | `INTEGER` | null |
| `confirmed_at` | `TIMESTAMPTZ` | null |
| `confirmation_actor_reference` | `TEXT` | null |
| `created_at` | `TIMESTAMPTZ` | not null, default `CURRENT_TIMESTAMP` |
| `updated_at` | `TIMESTAMPTZ` | not null, default `CURRENT_TIMESTAMP` |

The closed receipt status vocabulary is `EXTRACTED`, `NEEDS_REVIEW`,
`CONFIRMED`, `POSTED`, `REJECTED`, and `CANCELLED`, implemented later as `TEXT`
plus a check constraint rather than a PostgreSQL enum.

Database checks must enforce:

- trimmed nonblank `supplier_name` with at most 128 characters;
- nullable `document_number`, but when present it is trimmed, nonblank, and at
  most 128 characters;
- nonblank opaque `source_asset_reference`, with no binary and no ingestion FK;
- `version > 0` and, when present, `0 < confirmed_version <= version`;
- confirmation version, timestamp, and actor reference are either all present
  or all absent;
- `CONFIRMED` and `POSTED` require complete confirmation metadata and
  `confirmed_version = version`;
- `EXTRACTED` and `NEEDS_REVIEW` require confirmation metadata to be absent.

`REJECTED` and `CANCELLED` may retain complete confirmation evidence if the
terminal decision follows confirmation. Partial confirmation evidence is always
invalid. `document_date` is never substituted from another timestamp.

## Aggregate version and confirmation

There is one version counter on the receipt and no independent item version in
v1. Every editable header or item mutation locks the parent receipt, increments
`receipt.version`, returns the affected candidate lifecycle to `NEEDS_REVIEW` as
required, clears `confirmed_version`, `confirmed_at`, and
`confirmation_actor_reference`, and explicitly updates timestamps.

Confirmation atomically sets `confirmed_version = version` with the confirmation
timestamp and opaque operator reference. Posting requires equality while holding
the receipt row lock. This is the authoritative stale-confirmation mechanism.

## `public.material_receipt_items`

The frozen columns are:

| Column | PostgreSQL type | Nullability/default |
|---|---|---|
| `receipt_item_id` | `UUID` | primary key, not null, externally generated, no default |
| `receipt_id` | `UUID` | not null |
| `line_number` | `INTEGER` | not null |
| `candidate_material_description` | `TEXT` | null |
| `canonical_display_name` | `TEXT` | null |
| `size_description` | `TEXT` | null |
| `specification` | `TEXT` | null |
| `material_id` | `UUID` | null before resolution |
| `full_colly_count` | `INTEGER` | not null, default `0` |
| `qty_per_full_colly` | `NUMERIC(20,6)` | null |
| `partial_qty` | `NUMERIC(20,6)` | not null, default `0` |
| `total_qty` | `NUMERIC(20,6)` | not null |
| `unit` | `TEXT` | not null |
| `status` | `TEXT` | not null, default `EXTRACTED` |
| `created_at` | `TIMESTAMPTZ` | not null, default `CURRENT_TIMESTAMP` |
| `updated_at` | `TIMESTAMPTZ` | not null, default `CURRENT_TIMESTAMP` |

The item uses the same six-state vocabulary because individual lines require
independent review, resolution, exclusion, and posting evidence. Receipt status
is the aggregate lifecycle; the service coordinates header and item transitions
transactionally.

The receipt FK targets `public.material_receipts(receipt_id)`. The nullable
material FK targets `public.material_stock(material_id)`. Both use `ON UPDATE NO
ACTION` and `ON DELETE NO ACTION`. The table requires `line_number > 0` and
`UNIQUE (receipt_id, line_number)`. Optional descriptive values must be nonblank
when present.

`material_id` may be null for an unresolved candidate but must be non-null for
`CONFIRMED` and `POSTED`. Free text alone never authorizes stock posting.

## Packaging, formula, and units

V1 has no `partial_colly_count`. Database checks enforce:

- `full_colly_count >= 0`;
- when `full_colly_count = 0`, `qty_per_full_colly IS NULL`;
- when `full_colly_count > 0`, `qty_per_full_colly > 0`;
- `partial_qty >= 0`;
- `total_qty > 0`;
- exact `total_qty = (full_colly_count *
  COALESCE(qty_per_full_colly, 0)) + partial_qty`.

The closed unit vocabulary is `sheet`, `pcs`, `kg`, `roll`, and `pack`. For
`sheet`, `qty_per_full_colly` when present, `partial_qty`, and `total_qty` must be
integral. All arithmetic uses exact NUMERIC semantics. Item-to-stock unit equality
is validated inside the posting transaction because an ordinary check constraint
cannot safely enforce a cross-table rule.

The design-only examples pass the contract: `125 * 50 + 0 = 6250 sheet` and
`62 * 50 + 38 = 3138 sheet`. They must not be inserted into production.
