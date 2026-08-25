# Movement, Transaction, Authority, Privacy, and Audit

## Movement and idempotency

The only approved receipt movement type is `RECEIPT`. One confirmed receipt item
produces exactly one positive movement whose `quantity_delta` equals validated
`total_qty`. Zero and negative receipt movements are prohibited.

Stage 0.26 must enforce the database equivalent of:

```text
UNIQUE (source_receipt_item_id)
```

Retrying an exact already-posted item returns an idempotent already-posted result
and never increments stock again. Conflicting movement content for the same
source item fails closed.

The authoritative balance invariant is:

```text
balance_before + quantity_delta = balance_after
```

`balance_after` is the committed `public.material_stock.stock_qty`, and its
`updated_at` changes in the same transaction.

## Posting transaction and concurrency

One confirmed-receipt posting operation uses one database transaction. It must:

1. validate receipt state and confirmed version;
2. resolve and validate each active material;
3. validate exact unit agreement;
4. protect stock rows against concurrent update;
5. enforce absence of an existing movement for each receipt item;
6. create one inventory movement per item;
7. atomically update `material_stock`;
8. record `balance_before` and `balance_after`;
9. mark receipt items posted;
10. update receipt lifecycle as appropriate;
11. commit.

Any failure rolls back every effect. OCR, inference, provider calls, and operator
interaction are forbidden inside the transaction.

Posting uses an atomic SQL increment or equivalently safe row-locked operation.
An unprotected application read-calculate-overwrite sequence is prohibited.
Multi-material posting locks rows in deterministic order to reduce deadlock risk.

After `POSTED`, confirmed quantity, resolved material, unit, movement, balance
evidence, and source relationship are immutable. V1 does not introduce a generic
`ADJUSTMENT`. Future correction uses a separately governed reversal plus corrected
movement with causal links and explicit authority.

## Authority boundaries

`aios_material_stock_reader` remains strictly read-only and must never post a
receipt, create a movement, or update stock. Stage 0.26 must design a separate,
narrowly scoped application-controlled posting authority and credential boundary.

Brain receives no database credentials, writer handle, or generic SQL capability.
Inference permission is distinct from stock-mutation authority. Posting requires
both explicit operator confirmation and governed business-action authority; LLM
output cannot authorize mutation.

The approved future Telegram flow is:

```text
Telegram asset -> Universal Ingestion retention -> extraction candidate
-> operator review -> confirm/reject exact version
-> posting service revalidation -> transactional posting -> result
```

There is no automatic posting, and Telegram integration is outside Stage 0.25.

## Privacy, logging, and evidence

Processing minimizes document data and follows the applicable fail-closed DLP
policy. Logs may contain opaque identifiers, lifecycle states, timestamps,
outcome codes, actor or authority references, and transaction correlation IDs.
They must not contain document binaries, unnecessary OCR text, secrets, database
credentials, or irrelevant supplier content.

Future audit evidence must establish source asset, exact reviewed version,
operator confirmation, resolved material, packaging operands and calculation,
unit validation, movement identity and delta, previous and new balance, posting
authority, transaction result, idempotency outcome, and absence of duplicate
posting.
