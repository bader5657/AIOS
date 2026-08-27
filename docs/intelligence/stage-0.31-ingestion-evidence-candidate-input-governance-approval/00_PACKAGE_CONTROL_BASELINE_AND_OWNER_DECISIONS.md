# AIOS Intelligence Stage 0.31 Package Control, Baseline, and Owner Decisions

Date: 2026-08-27 (Asia/Jakarta)

## Baseline and decision

This documentation-only governance package is based on clean, synchronized
`main` commit `b7354e501ca66200dc0dcef4e626c00d0033e85d`, the merge of Stage
0.30 implementation PR #229. Stage 0.30 is merged, verified, and closed.

The Stage 0.31 boundary evaluation concluded:

> INTELLIGENCE STAGE 0.31 INGESTION EVIDENCE -> CANDIDATE INPUT BOUNDARY IDENTIFIED
> — READY FOR GOVERNANCE APPROVAL

No architecture blocker remains. The Project Owner APPROVES Stage 0.31,
Universal Ingestion Evidence -> Material Receipt Candidate Input Boundary, as
the next AIOS Intelligence stage.

This package records governance only. It implements no Stage 0.31 code and
changes no production system, runtime, Telegram integration, Universal
Ingestion runtime, inference path, credential, database, or data.

## Project Owner decisions

The following decisions are approved and frozen:

1. Stage 0.31 is the next AIOS Intelligence stage.
2. Stage 0.31 uses a two-step rollout:
   - Stage 0.31A: mapper, validation, evidence handoff, and offline tests only;
   - Stage 0.31B: separately governed runtime composition later.
3. Existing Telegram integration is retained. Telegram setup must not be
   repeated, replaced, reconfigured, or changed in Stage 0.31A.
4. The existing Universal Ingestion retained manifest is the authoritative
   source evidence. Universal Ingestion runtime remains unchanged in 0.31A.
5. `registry_record_id` is optional corroborating identity only and never
   replaces retained manifest evidence.
6. Successful ingestion evidence requires a successfully created and retained
   canonical manifest. Registry registration may be absent or unsuccessful
   when the manifest was retained successfully.
7. Strong retained-manifest verification is required. Regular-file existence
   alone is insufficient; the existing manifest validator and filename/content
   identity consistency checks are mandatory.
8. Raw Telegram text, caption, and document metadata are not trusted receipt
   business data.
9. Arbitrary Universal Ingestion metadata is not trusted receipt business data.
10. OCR, Vision, LLM, and Brain output have no receipt-fact authority.
11. Stage 0.31A accepts only explicitly trusted structured/operator-supplied
    facts and deterministic offline test fixtures.
12. Receipt and receipt-item IDs are application-generated UUIDv4 values.
    Caller-selected IDs are not trusted public facts. Deterministic injected ID
    factories are permitted only in isolated tests.
13. Source identity comes authoritatively from retained ingestion evidence.
    Trusted business facts cannot contain or override the source asset,
    manifest identity, or Registry identity.
14. The application numeric, precision, scale, text, packaging, item-count, and
    unit safety ceilings in this package are approved.
15. Confirmation and posting remain deferred, uncomposed, and unreachable.

## Approval effect

This package approves only a later, separately authorized Stage 0.31A
implementation of inert mapper, validation, evidence handoff, and offline test
functionality. It grants no candidate persistence, confirmation, posting,
database, credential, runtime-composition, Telegram, Universal Ingestion
mutation, OCR, Vision, LLM, or Brain authority.
