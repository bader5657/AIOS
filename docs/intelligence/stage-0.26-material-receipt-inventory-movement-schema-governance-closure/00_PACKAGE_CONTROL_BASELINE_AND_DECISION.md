# AIOS Intelligence Stage 0.26 — Package Control, Baseline, and Decision

| Control | Frozen value |
|---|---|
| Baseline | `7ed2c40` on `main` |
| Stage 0.25 | formally closed by merged PR `#209` |
| Assessment | PostgreSQL schema design identified |
| Stage classification | design-governance approval and closure only |
| Migration or executable DDL | prohibited |
| PostgreSQL, role, or credential mutation | prohibited |
| Production data or stock mutation | prohibited |
| Repository, runtime, Telegram, or ingestion change | prohibited |
| OCR or inference | prohibited |

Stage 0.26 approves and freezes the PostgreSQL v1 schema contract for exactly:

1. `public.material_receipts`;
2. `public.material_receipt_items`;
3. `public.inventory_movements`.

`public.material_stock` remains the authoritative stored current-stock balance.
The existing `aios_material_stock_reader` remains unchanged and strictly
read-only. Current-stock retrieval does not replay movement history.

All three new primary keys are externally generated UUID values with no database
generation default. This package defines concepts, types, constraints, indexes,
transactions, and privilege boundaries, but contains no executable schema.

`INTELLIGENCE STAGE 0.26 POSTGRESQL SCHEMA GOVERNANCE APPROVED — READY FOR MIGRATION AND PRIVILEGE PLAN`
