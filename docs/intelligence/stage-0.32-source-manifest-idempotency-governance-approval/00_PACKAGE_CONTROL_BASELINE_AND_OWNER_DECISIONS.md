# AIOS Intelligence Stage 0.32 Package Control, Baseline, and Owner Decisions

Date: 2026-08-27 (Asia/Jakarta)

## Package classification

This is a documentation-only governance approval package for Stage 0.32,
Source-Manifest Candidate Atomic Idempotency / Deduplication. It is based on
clean, synchronized `main` commit `98a8ff7f86c7e3d0cf988985df1d767aee97eafc`.

This package changes no runtime code, schema, migration, credentials, or
production system. It does not contact PostgreSQL, activate candidate creation,
wire Telegram or Universal Ingestion, or invoke OCR, Vision, LLM, or Brain.

## Established baseline

Stages 0.30, 0.31A, and 0.31B are merged and verified. Stage 0.31B exposes the
create-only operation:

```text
create_review_candidate_from_ingestion(
    ingestion_result,
    trusted_receipt_facts,
) -> ReceiptForReview
```

The current `material_receipts.source_asset_reference` is indexed by the
non-unique `material_receipts_source_asset_idx`. Repeated creates for one
retained manifest can therefore produce multiple candidates. The candidate
repository owns the complete receipt/item transaction; an application-only
pre-check cannot serialize concurrent creates.

Current production activation is NOT AUTHORIZED. Existing gates are:

1. atomic source-manifest candidate idempotency/deduplication;
2. durable candidate-creation actor provenance;
3. runtime-secret / activation safety; and
4. explicit production safety review.

Stage 0.32 addresses only gate 1.

## Project Owner decisions — APPROVED and frozen

1. Stage 0.32 is the next activation-gate stage.
2. At most one ACTIVE material receipt may exist for one canonical retained
   manifest.
3. ACTIVE is exactly `status NOT IN ('REJECTED', 'CANCELLED')`, including
   `EXTRACTED`, `NEEDS_REVIEW`, `CONFIRMED`, and `POSTED`.
4. REJECTED and CANCELLED rows remain permanently retained historical records.
5. A replacement candidate may be created only after all prior rows for that
   manifest are REJECTED or CANCELLED.
6. No physical deletion, automatic row reuse, receipt-ID reuse, or silent
   overwrite is authorized.
7. Correction of an active receipt uses governed review/revision flow.
8. PostgreSQL must enforce atomic concurrency correctness.
9. The v1 mechanism is a PostgreSQL partial unique index named
   `material_receipts_source_asset_active_uidx` with predicate
   `status NOT IN ('REJECTED', 'CANCELLED')`.
10. A create attempt with an active row returns bounded outcome
    `SOURCE_ACTIVE_RECEIPT_EXISTS`.
11. Same facts do not replay the existing row; different facts do not compare
    or overwrite it. Semantic fact comparison is not required for v1.
12. The sole deduplication identity is canonical retained
    `source_asset_reference`. Registry ID, Telegram ID, supplier, and document
    fields are not deduplication keys.
13. No additional candidate runtime privileges are authorized.
14. Confirmation and posting remain unchanged and unreachable from the create
    boundary.
15. Production activation remains blocked until all remaining gates close.

## Approval effect

This package approves the Stage 0.32 architecture and implementation boundary.
It authorizes neither migration creation/execution, repository changes,
deployment, production preflight, nor production activation.

