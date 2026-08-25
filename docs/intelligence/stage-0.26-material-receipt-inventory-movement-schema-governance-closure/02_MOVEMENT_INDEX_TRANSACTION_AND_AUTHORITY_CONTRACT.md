# Movement, Index, Transaction, and Authority Contract

## `public.inventory_movements`

The frozen columns are:

| Column | PostgreSQL type | Nullability/default |
|---|---|---|
| `movement_id` | `UUID` | primary key, not null, externally generated, no default |
| `material_id` | `UUID` | not null |
| `movement_type` | `TEXT` | not null |
| `quantity_delta` | `NUMERIC(20,6)` | not null |
| `unit` | `TEXT` | not null |
| `source_receipt_item_id` | `UUID` | not null |
| `occurred_at` | `TIMESTAMPTZ` | not null, explicitly supplied |
| `posted_at` | `TIMESTAMPTZ` | not null, default `CURRENT_TIMESTAMP` |
| `posting_actor_reference` | `TEXT` | not null |
| `balance_before` | `NUMERIC(20,6)` | not null |
| `balance_after` | `NUMERIC(20,6)` | not null |
| `created_at` | `TIMESTAMPTZ` | not null, default `CURRENT_TIMESTAMP` |

The material FK targets `public.material_stock(material_id)`. The source FK
targets `public.material_receipt_items(receipt_item_id)`. Both use `ON UPDATE NO
ACTION` and `ON DELETE NO ACTION`.

V1 permits only movement type `RECEIPT`; `ADJUSTMENT`, `ISSUE`, and `REVERSAL`
remain separately governed. Checks require positive `quantity_delta`, a nonblank
opaque posting actor, the same closed unit vocabulary, nonnegative balances, and
exact `balance_after = balance_before + quantity_delta`. For `sheet`, the delta
and both balances must be integral.

`occurred_at` is the business receipt occurrence time and normally uses the
governed receipt `received_at`. It is not silently replaced by document,
confirmation, or posting time. The posting service validates that movement
material, unit, and quantity exactly equal the confirmed source item.

`UNIQUE (source_receipt_item_id)` is the authoritative database idempotency
guard. Exact retries return already-posted without changing stock; conflicting
content fails closed.

## Minimum indexes

Only the following are approved beyond primary-key and unique-constraint indexes:

- receipt status;
- partial non-unique receipt `(supplier_name, document_number)` where the number
  is not null;
- receipt `source_asset_reference`;
- partial item `material_id` where not null;
- movement `(material_id, posted_at DESC)`.

The supplier/document index is a duplicate-review lookup, never a uniqueness
rule. Receipt identity remains `receipt_id`. No speculative item-status or
standalone movement-time index is approved.

## Atomic posting and concurrency

One confirmed receipt posts all applicable lines in one transaction; partial
successful posting is prohibited. The governed transaction must:

1. begin and lock the exact receipt;
2. verify `CONFIRMED` and `confirmed_version = version`;
3. lock applicable items and require at least one eligible item;
4. validate item state, resolved material, formula, and unit;
5. gather distinct material IDs;
6. lock target `material_stock` rows in ascending `material_id` order;
7. verify every material is active and every item unit equals its stock unit;
8. detect an existing movement and distinguish exact retry from conflict;
9. obtain stable `balance_before` values;
10. insert one movement per eligible item;
11. atomically increment stock and use database `RETURNING` for each
    `balance_after`;
12. verify and retain exact movement balance evidence;
13. mark all applicable items and the receipt `POSTED`, updating timestamps;
14. commit.

Any failure rolls back every effect. Receipt, applicable item, and stock rows use
`SELECT ... FOR UPDATE`. Multiple lines for one material are processed in
deterministic `(material_id, line_number)` order. There is no unprotected
application read-calculate-overwrite. OCR, LLM, provider, Telegram, network, and
operator interaction are prohibited inside the transaction.

## Immutability and authority

Movement rows are immutable after insert. The future posting writer receives
only `SELECT` and `INSERT` on `inventory_movements`, with no `UPDATE`, `DELETE`,
or `TRUNCATE`. Ownership remains separate; no immutability trigger is required in
v1.

Candidate writing and authoritative posting use separate future boundaries:

- candidate authority may select, insert, and perform bounded pre-posting updates
  on receipts and items, but cannot insert movements or update stock;
- posting authority may select receipt/item state, perform bounded lifecycle and
  version updates, select and insert movements, and select and update
  `material_stock` only through governed posting operations.

Future database design uses separate `NOLOGIN` privilege roles backed by separate
runtime `LOGIN` identities. Exact names are deferred. Neither boundary receives
unrelated-table access, delete, truncate, DDL, ownership, default privileges,
role management, or credential visibility outside its runtime secret facility.

`aios_material_stock_reader` is unchanged and has no writer membership. Brain
permanently receives no database credential, connection handle, generic SQL, or
writer authority. A future Telegram confirmation binds to `receipt_id` and exact
`version`; a mismatch under the receipt lock returns stale confirmation and does
not post.
