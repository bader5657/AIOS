# Migration 0003 — Production Deployment Closure and Baseline

| Control | Verified value |
|---|---|
| Deployment result | `MIGRATION 0003 PRODUCTION DEPLOYMENT PASS — THREE EMPTY SCHEMAS DEPLOYED` |
| Source baseline | `4b75847a7f64949bc2d37181f8fd551917550a66` on clean `main` |
| PostgreSQL | production `aios-postgres`, PostgreSQL 17.10, database `aios`, schema `public` |
| Restart count before/after | `0` / `0` |
| Service postflight | running, healthy, accepting connections |

Migration 0003 committed exactly the approved production schema for
`public.material_receipts`, `public.material_receipt_items`, and
`public.inventory_movements`. Postflight verified exact columns, constraints,
foreign-key actions, indexes, and zero non-internal triggers.

All new tables remained empty before commit and after commit:

- `material_receipts`: `0` rows;
- `material_receipt_items`: `0` rows;
- `inventory_movements`: `0` rows.

`public.material_stock` remained at `0` rows and retained its exact schema,
constraints, primary-key index, owner, ACL, and deterministic content fingerprint.
The unrelated relation, constraint, index, routine, trigger, role, membership,
default-ACL, database/schema-ACL, and extension fingerprints remained unchanged.

`aios_material_stock_reader` remained its dedicated restricted login with
effective SELECT-only table access, no writer membership, and no ownership. All
four planned writer identities remained absent. Deployment created no role,
login, grant, credential, default privilege, business row, runtime behavior,
Telegram integration, OCR, or inference effect.

This closure publication performs no database mutation. Migration 0003 production
deployment is formally closed only after this documentation-only package is
reviewed and merged normally to `main`.

`MIGRATION 0003 PRODUCTION DEPLOYMENT CLOSED`
