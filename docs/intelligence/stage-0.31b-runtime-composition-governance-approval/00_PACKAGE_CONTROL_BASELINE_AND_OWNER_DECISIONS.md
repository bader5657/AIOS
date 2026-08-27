# AIOS Intelligence Stage 0.31B Package Control, Baseline, and Owner Decisions

Date: 2026-08-27 (Asia/Jakarta)

## Package classification

This is a documentation-only governance approval package for AIOS Intelligence
Stage 0.31B, Universal Ingestion Evidence to Material Receipt Candidate
Runtime/Application Composition. It is based on clean, synchronized `main`
commit `c0bfdffd2b27366c1073da8bb1ef4089947487f4`.

This package changes no runtime code or production system. It does not implement
Stage 0.31B, activate candidate creation, contact PostgreSQL, create or load a
credential, invoke inference, or expose confirmation or posting authority.

## Established baseline

Stage 0.30 is merged and verified. It established the review-only Material
Receipt application boundary and its governed `create_candidate` operation.

Stage 0.31A is merged and verified. It established:

```text
build_receipt_candidate_request(
    ingestion_result: IngestionResult,
    trusted_receipt_facts: TrustedReceiptFacts,
) -> ReceiptCandidateRequest
```

The Stage 0.31A mapper provides retained-evidence and strong manifest
validation, bounded trusted facts, application-generated UUIDv4 receipt/item
IDs, numeric and text ceilings, Decimal precision and scale controls, exact
packaging validation, and exclusive evidence-derived source identity. It is
inert: candidate and posting repository construction, credential loading,
candidate persistence, confirmation, and posting are all zero or unreachable.

The numeric upper-bound technical debt is CLOSED.

## Project Owner decisions

The following decisions are APPROVED and frozen:

1. Stage 0.31B is the next implementation stage.
2. Its sole composition chain is Stage 0.31A mapper to Stage 0.30
   `create_candidate`, through a create-only candidate capability.
3. Stage 0.31B exposes exactly one public create operation.
4. The public operation has exactly two inputs: the current `IngestionResult`
   and an exact `TrustedReceiptFacts` instance. There is no third generic
   context or payload input.
5. The initial API does not accept `ActorContext`. The current
   `material_receipts` schema has no durable candidate-creation actor field;
   validating but not recording an actor would imply misleading audit
   semantics.
6. Durable candidate-creation actor provenance requires separate governance
   before production activation.
7. Current duplicate-candidate behavior is acceptable only during isolated,
   non-activated implementation and testing.
8. Production activation requires a separate atomic source-idempotency or
   deduplication decision. The recommended future v1 direction is one active
   material-receipt candidate per retained manifest, where active excludes
   `REJECTED` and `CANCELLED`. No such rule or migration is authorized here.
9. Confirmation remains absent and unreachable.
10. Posting remains absent and unreachable.
11. Existing Telegram integration remains unchanged.
12. Existing Universal Ingestion runtime remains unchanged.
13. OCR, Vision, LLM, and Brain have no receipt-fact authority.
14. Stage 0.31B implementation and tests must precede any activation proposal.
15. Production activation is a separate future governance stage.

## Approval effect

This package authorizes a later, separate implementation PR only within the
boundary stated here. It does not itself authorize implementation, deployment,
production activation, Telegram or Universal Ingestion wiring, schema changes,
credential changes, confirmation, posting, movement creation, or stock
mutation.
