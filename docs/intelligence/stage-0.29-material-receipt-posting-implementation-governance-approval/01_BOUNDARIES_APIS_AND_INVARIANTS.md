# Candidate and Posting Boundaries, APIs, and Invariants

## Approved package boundary

The future implementation is limited to:

- `core/material_receipts/` with `__init__.py`, `models.py`, `errors.py`,
  `repository.py`, and `service.py`;
- `core/inventory_posting/` with the same five narrow module roles;
- the unit and integration test paths enumerated in the Stage 0.29 authority.

Repository-native path adjustment requires reviewer confirmation. No ORM,
generic repository framework, generic SQL API, broad business-context engine,
or new dependency is approved. The implementation must use existing async
Python, frozen/slotted dataclass, Psycopg 3, parameterized-SQL, transaction
ownership, and sanitized-error conventions.

## Candidate boundary

The approved conceptual API is:

- `create_receipt_candidate(request)`;
- `revise_receipt_candidate(request, expected_version)`;
- `get_receipt_for_review(receipt_id)`;
- `confirm_receipt(receipt_id, expected_version, actor_reference)`;
- `reject_receipt(receipt_id, expected_version, actor_reference)`;
- `cancel_receipt(receipt_id, expected_version, actor_reference)`;
- `cancel_receipt_item(receipt_id, receipt_item_id, expected_version, actor_reference)`.

There is no `patch`, row-update, item-delete, or arbitrary-SQL API. Every
effective candidate-content or item-cancellation mutation locks or
optimistically conditions the receipt, verifies the expected version,
increments the aggregate version exactly once, and invalidates any earlier
confirmation fields.

An erroneous line is retained with `status = CANCELLED`. It remains linked to
its receipt and may retain original extraction/review evidence. It cannot be
reactivated, confirmed, posted, generate a movement, or mutate stock. No DELETE
method or DELETE privilege is approved.

Candidate review may display nonterminal candidate rows. Confirmation may move
only intended active candidate items to `CONFIRMED`; `CANCELLED` and `REJECTED`
items are excluded. Posting applicability is exactly an item belonging to the
locked receipt with `status = CONFIRMED`, resolved `material_id`, and a valid
receipt/version confirmation. At least one applicable item is required.

## DTO and business contracts

The frozen receipt request contains only receipt ID, supplier name, optional
document number/date, received timestamp, source asset reference, and an
immutable item tuple. Each item contains only its ID, line number, optional
candidate/canonical/size/specification descriptions, optional review-time
material ID, packaging quantities, total quantity, and unit. Callers cannot
supply status, credentials, SQL, connection state, posting authority, movement
facts, or balances.

All quantities use exact decimal semantics. The authoritative formula is:

`total_qty = (full_colly_count * qty_per_full_colly) + partial_qty`

For current EF examples the base unit is `sheet`; `colly` is packaging evidence,
not an inventory unit. The test-only examples are `125 * 50 + 0 = 6250` and
`62 * 50 + 38 = 3138`. Fractional sheet quantities are invalid.

Review may retain a null material ID. Confirmation requires an exact existing,
active material and exact equality between item and stock units. Fuzzy or
LLM-selected authority and automatic material-master creation are prohibited.

## Lifecycle and confirmation

The lifecycle is `EXTRACTED -> NEEDS_REVIEW -> CONFIRMED -> POSTED`, with
terminal `REJECTED` and `CANCELLED` alternatives. Reverse transitions and edits
to posted business facts are prohibited. Confirmation binds the exact
`receipt_id` and `version` by setting `confirmed_version = version`. Posting
requires `expected_version == version == confirmed_version`; stale state fails
closed.

## Posting boundary

The sole public operation is
`post_confirmed_receipt(receipt_id, expected_version, actor_reference)`. All
movement IDs, deltas, types, balances, and stock mutations are internally
derived from locked authoritative state.

One all-or-nothing transaction must lock the receipt; validate state, version,
and confirmation; select and validate at least one applicable item; validate
material existence/activity, unit, packaging, and positive quantity; reconcile
idempotency; lock distinct stock rows by ascending material ID; process items
by `(material_id, line_number, receipt_item_id)`; insert one `RECEIPT` movement
per item; atomically increment stock; record exact balances; and only then mark
applicable items and the receipt `POSTED`. Any failure rolls back all effects.

Stock mutation must use `stock_qty = stock_qty + quantity_delta` with
`RETURNING`. The captured evidence must satisfy
`balance_after = balance_before + quantity_delta`. Same-material lines execute
sequentially and each line consumes the balance returned by its predecessor.

`UNIQUE(source_receipt_item_id)` remains the database idempotency authority. An
exact retry of a completely posted receipt/version returns typed
`ALREADY_POSTED` evidence without stock mutation. A movement conflicting with
authoritative material, quantity, unit, source, or aggregate completeness fails
as `CONFLICTING_POSTING`. Movement history has no update, delete, or truncate
repository surface.
