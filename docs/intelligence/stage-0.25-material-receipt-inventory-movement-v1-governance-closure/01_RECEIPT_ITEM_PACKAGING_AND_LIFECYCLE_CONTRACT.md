# Receipt, Item, Packaging, and Lifecycle Contract

## Receipt header

The approved minimum conceptual receipt header contains:

- `receipt_id`;
- `supplier_name`;
- nullable `document_number`;
- nullable `document_date`;
- `received_at`;
- `source_asset_reference`;
- `status`;
- nullable `confirmed_at`;
- nullable `confirmation_actor_reference`;
- `created_at` and `updated_at`.

No accounting field belongs to Stage 0.25. `document_number` is trimmed,
case-preserving, nullable, and recommended to be at most 128 characters. It is
not globally unique. Supplier plus document number is a duplicate-review signal,
not canonical identity; `receipt_id` is canonical. `document_date` is copied only
when present and verified and must not be inferred from another timestamp.

Supplier name is receipt metadata. Receipt processing must not create or update
Supplier Registry records.

## Receipt item and material identity

The approved minimum conceptual item contains `receipt_item_id`, `receipt_id`, a
line/order identifier, `candidate_material_description`,
`canonical_display_name`, `size_description`, `specification`, nullable
pre-resolution `material_id`, `full_colly_count`, `qty_per_full_colly`,
`partial_qty`, `total_qty`, `unit`, posting/lifecycle state, and timestamps.

Extraction may produce an unresolved material description. Exact active
`material_id` resolution is mandatory before authoritative confirmation or
posting. Free-text matching alone must never mutate `material_stock`.

Compound v1 names may include `SH EF 630x560 K150/M125/M125` and
`SH EF 1200x1020 K125/M125/M125`. Normalized material type, width, length, and
paper specification remain future material-master architecture debt.

## Packaging and quantity

V1 uses only:

- `full_colly_count >= 0`;
- `qty_per_full_colly > 0` when `full_colly_count > 0`;
- `partial_qty >= 0`;
- `total_qty > 0` for confirmation and posting.

`partial_qty` is the total loose base-unit quantity outside all complete colly.
V1 does not introduce `partial_colly_count`. When `full_colly_count = 0`, the
complete-colly contribution is exactly zero.

The frozen invariant is:

```text
total_qty = (full_colly_count * qty_per_full_colly) + partial_qty
```

Quantities use exact Decimal/NUMERIC semantics, never binary floating point. For
`sheet`, all operands and the total are integral and equality has zero tolerance.
The current EF-material base unit is `sheet`; colly is packaging metadata only.
The receipt item unit must exactly equal the target `material_stock.unit`. No
implicit unit conversion is allowed.

## Extraction, confirmation, and lifecycle

An extracted candidate is not an authoritative business record. Vision, OCR, or
LLM output may only suggest fields. Candidate uncertainty is bounded to `exact`,
`uncertain`, or `missing`; required fields not marked exact require operator
resolution. Raw OCR text is not required in business receipt tables.

An operator must explicitly review supplier, document number/date when present,
material, size/specification, packaging operands, total quantity, and unit.
Editing a reviewed candidate invalidates stale confirmation.

The frozen state machine is:

```text
EXTRACTED -> NEEDS_REVIEW -> CONFIRMED -> POSTED
                         \-> REJECTED
                         \-> CANCELLED
```

`POSTED`, `REJECTED`, and `CANCELLED` are terminal in v1.

The two design-only validation examples are valid:

- `125 * 50 + 0 = 6250 sheet` for `SH EF 630x560 K150/M125/M125`;
- `62 * 50 + 38 = 3138 sheet` for `SH EF 1200x1020 K125/M125/M125`.

They must not be inserted into production.
