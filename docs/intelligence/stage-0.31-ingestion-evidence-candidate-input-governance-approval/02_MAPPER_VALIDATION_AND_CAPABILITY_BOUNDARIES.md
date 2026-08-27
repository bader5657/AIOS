# Mapper, Validation, and Capability Boundaries

## Approved Stage 0.31A operation

The preferred inert operation is:

```text
build_receipt_candidate_request(
    ingestion_evidence,
    trusted_receipt_facts,
    *,
    id_factory
) -> ReceiptCandidateRequest
```

The mapper creates the existing immutable `ReceiptCandidateRequest` and
`ReceiptItemCandidate` values. `source_asset_reference` is copied exclusively
from verified retained evidence. Required receipt facts are never invented.

The operation must not create or persist a candidate; construct
`MaterialReceiptRepository` or `InventoryPostingRepository`; load candidate or
posting credentials; call `ReviewFacade.create_candidate`; confirm; post;
update stock; create movements; invoke OCR, Vision, LLM, or Brain; alter
Universal Ingestion; or alter Telegram.

## ID policy

The receipt ID and every receipt-item ID are application-generated exact
`UUID` values of version 4. Caller-selected IDs are not part of the public
trusted-facts contract. Every generated ID must be unique within the request,
including uniqueness between the receipt ID and all item IDs. Malformed,
non-UUID, non-v4, or duplicate factory output fails closed.

The production/default factory is application-owned. Injection of a
deterministic UUID factory is permitted only for isolated tests and grants no
caller-selected-ID authority in production interfaces.

## Item and quantity limits

- A request contains at least 1 and at most 500 items.
- Item line numbers are positive and unique within the request.
- `full_colly_count` is an exact integer from 0 through 1,000,000.
- When `full_colly_count > 0`, `qty_per_full_colly` is required, greater than
  zero, and no greater than 1,000,000.
- When `full_colly_count == 0`, `qty_per_full_colly` is exactly `None`.
- `partial_qty` is from 0 through 1,000,000,000.
- `total_qty` is greater than 0 and no greater than 1,000,000,000.

Boolean values do not satisfy integer contracts.

## Decimal safety

All applicable quantity values are exact `Decimal` instances and finite. Float
coercion is prohibited. Maximum scale is 6 decimal places and maximum precision
is 20 digits. Values exceeding either limit fail closed.

Validation performs no quantization, rounding, truncation, normalization, or
lossy conversion. Accepted exact Decimal values are preserved unchanged. NaN,
positive or negative infinity, floats, and non-Decimal quantity inputs fail
closed.

## Packaging and unit contracts

The exact packaging equation is:

```text
total_qty =
    Decimal(full_colly_count)
    * qty_per_full_colly
    + partial_qty
```

For the zero-full-colly case, the absent per-colly term contributes exact zero.
Exact mathematical equality is required. No tolerance, rounding, or
recalculation of caller-supplied `total_qty` is permitted.

For unit `sheet`, every applicable quantity (`qty_per_full_colly` when present,
`partial_qty`, and `total_qty`) must be mathematically integral.

The unit vocabulary is exactly `sheet`, `pcs`, `kg`, `roll`, and `pack`. There
are no aliases, case folding, normalization, or fuzzy matches.

## Text and temporal limits

- `supplier_name` is required, nonblank, already in trimmed canonical form, and
  at most 128 characters.
- `document_number` is optional; when present it is nonblank, already in trimmed
  canonical form, and at most 128 characters.
- Each optional descriptive/material text field is, when present, nonblank,
  already in canonical form, and at most 512 characters.
- `received_at` must be timezone-aware.
- `document_date`, when present, must satisfy the existing exact date contract.
- `material_id`, when present, must satisfy the existing exact UUID contract.

Noncanonical whitespace, blank text, or over-limit text fails closed. No silent
trimming or truncation is permitted.

## Capability boundary

Stage 0.31A has:

- candidate persistence authority: NONE;
- confirmation authority: NONE and unreachable;
- posting authority: NONE and unreachable;
- `MaterialReceiptRepository` construction: ZERO;
- `InventoryPostingRepository` construction: ZERO;
- candidate credential loading: ZERO;
- posting credential loading: ZERO;
- production side effects: ZERO.

Importing or constructing the evidence handoff, validation DTOs, or mapper must
have zero side effects. No candidate/confirmation/posting API, repository,
credential loader, connection, SQL, DSN, or equivalent indirect capability may
be exposed.

## Stage 0.31B deferred boundary

Runtime composition, including any connection from existing Universal
Ingestion evidence into candidate persistence, is deferred to Stage 0.31B and
requires separate governance. Stage 0.31A neither authorizes nor anticipatorily
implements that composition. Existing Telegram and Universal Ingestion runtime
flows remain unchanged.
