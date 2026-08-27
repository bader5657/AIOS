# Test Governance, Production Safety, Approval, and Next Action

## Unit and behavioral test governance

A later Stage 0.31B implementation must prove behaviorally:

1. The public API has exactly two inputs and exactly one public operation.
2. The Stage 0.31A mapper executes exactly once for each valid call.
3. The create-only capability executes exactly once and only after valid
   mapping.
4. Invalid evidence prevents the create capability, repository construction,
   database activity, and persistence.
5. Invalid or forged trusted facts prevent those same activities.
6. Every bounded mapper failure prevents persistence.
7. Source identity remains exclusively mapper-authoritative.
8. The result is `ReceiptForReview` in `NEEDS_REVIEW` state.
9. Confirmation, posting, revision, rejection, and cancellation are
   inaccessible.
10. Generic dispatch and generic mutation surfaces are absent.
11. Posting repository/configuration construction and posting credential use
    remain zero.
12. Module import loads no candidate/posting credentials and performs no
    database, environment, filesystem, runtime, Telegram, or ingestion action.
13. Inert construction performs no credential loading or database activity.
14. Mapper and candidate failure call counts establish correct ordering and
    fail-closed behavior.
15. Current duplicate invocation behavior is explicitly tested and described as
    non-idempotent, isolated-test behavior—not production-safe semantics.

Tests must use independent counters, sentinels, and adversarial objects where
behavior can be exercised; source-string inspection alone is insufficient.

## Disposable PostgreSQL integration governance

Integration testing must use a fresh, governed, admitted disposable PostgreSQL
instance only. It must reproduce the exact restricted production-equivalent
candidate identity and grants without using a production database or secret.

The integration suite must prove:

- valid trusted input persists exactly one receipt and all mapped items;
- receipt and items persist atomically;
- `source_asset_reference` exactly equals the verified retained manifest;
- the persisted result is `NEEDS_REVIEW`;
- no `inventory_movements` row is created;
- `material_stock` is unchanged;
- candidate identity cannot update stock or insert movements;
- posting identity is neither created nor used by Stage 0.31B composition;
- candidate transaction failure rolls back both receipt and items; and
- mapper failure occurs before every database call.

Governed non-production admission and existing PostgreSQL test skip protections
must not be weakened.

## Security and object-graph governance

Security tests must recursively traverse the returned composed use-case object
and attempt to recover all of the following:

- `ReviewFacade`;
- `MaterialReceiptRepository`;
- `CandidateDatabaseConfig`;
- candidate password, username, database URL, or DSN;
- database connection;
- repository factory;
- confirmation, posting, revision, rejection, or cancellation methods;
- `InventoryPostingRepository` and `PostingDatabaseConfig`;
- posting credentials; and
- any generic callable mutation surface.

Every item must be unreachable. Tests must inspect callable receivers, closures,
partials, slots, containers, and ordinary attributes as applicable; naming
privacy is not proof. The create-only adapter must remain stateless and must not
provide a traversal route to the broad Stage 0.30 composition.

On invalid mapper input, repository construction is zero where composition is
deferred until after mapping, database activity is zero, candidate persistence
is zero, and every confirmation/posting activity remains zero.

## Production safety and non-activation

During this governance package:

- Production PostgreSQL contact: NO.
- Production mutation: NONE.
- Production stock mutation: NONE.
- Production role/grant changes: NONE.
- `runtime.env` mutation: NONE.
- Runtime service restart or activation: NONE.
- Telegram mutation: NONE.
- Universal Ingestion runtime mutation: NONE.
- OCR, Vision, LLM, and Brain invocation: NONE.
- Production credential creation or loading: NONE.
- Candidate persistence, confirmation, posting, and movement creation: NONE.

Rollback is documentation-only: close the governance PR or revert its
documentation commit. There is no runtime rollback because this package changes
no runtime or production state.

## Project Owner approval

The Project Owner APPROVES the Stage 0.31B runtime/application composition
boundary, public API, authority chain, exclusions, test obligations,
implementation boundary, and activation gates recorded in this package.

This approval makes Stage 0.31B ready for a separate implementation
authorization. It does not authorize implementation in this PR and never
authorizes production activation.

## Next official action

1. Independently review and merge this documentation-only governance PR.
2. Verify the governance merge on clean, synchronized `main`.
3. Issue a separate, narrow Stage 0.31B implementation authorization.
4. Implement and test only the approved create-only composition on a separate
   branch and PR, including disposable PostgreSQL and object-graph security
   tests.
5. Conduct a fresh independent implementation review before merge.
6. Govern source idempotency, durable actor provenance, runtime-secret safety,
   and production activation separately before any runtime wiring.

`STAGE 0.31B RUNTIME COMPOSITION GOVERNANCE APPROVED — READY FOR IMPLEMENTATION AUTHORIZATION`
