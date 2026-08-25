# AIOS Intelligence Stage 0.25 — Package Control, Baseline, and Decision

| Control | Frozen value |
|---|---|
| Baseline | `26841db` on `main` |
| Assessment result | boundary identified and ready for governance approval |
| Stage classification | governance approval and closure only |
| Production data mutation | prohibited |
| Schema or migration change | prohibited |
| Runtime, Telegram, or ingestion change | prohibited |
| OCR or inference | prohibited |
| Inventory posting | prohibited |

Stage 0.25 approves and freezes the Material Receipt / Inventory Movement v1
boundary. It introduces no database object or runtime behavior. Exact PostgreSQL
design and posting authority remain Stage 0.26 work.

The v1 domain contains exactly three business entities and they must not be
merged:

1. `material_receipts`, for source-document lifecycle;
2. `material_receipt_items`, for extracted and reviewed packaging and quantity
   evidence;
3. `inventory_movements`, for authoritative stock-mutation records.

`public.material_stock` remains the authoritative stored current-stock balance.
Current-stock retrieval reads that table and does not require replay of movement
history. A future governed movement posting updates the balance transactionally.

Supplier delivery notes are immutable source evidence. They are neither current
stock balances nor stock-mutation authority. The receipt retains an opaque
Universal Ingestion asset reference; it does not duplicate the document binary.

The original Telegram or file asset and its metadata remain governed by the
Universal Ingestion retention policy after extraction, confirmation, posting,
rejection, or cancellation.

`INTELLIGENCE STAGE 0.25 MATERIAL RECEIPT / INVENTORY MOVEMENT V1 GOVERNANCE APPROVED — READY FOR STAGE 0.26 SCHEMA DESIGN`
