# Create-Only Capability, Authority, and Result Contract

## Public application capability

Stage 0.31B has exactly one public application operation:

```text
create_review_candidate_from_ingestion(
    ingestion_result,
    trusted_receipt_facts,
) -> ReceiptForReview
```

The operation is create-only. Its public surface must not expose retrieval,
revision, rejection, cancellation, confirmation, posting, generic execution or
dispatch, repository access, connections, or configuration.

The two public inputs are exactly:

- the current `IngestionResult`, revalidated by Stage 0.31A; and
- an exact `TrustedReceiptFacts`, revalidated by Stage 0.31A.

The caller cannot provide receipt or item IDs, source/manifest/Registry
identity, credentials, DSN, repository, connection, transaction, confirmation
authority, posting authority, or a generic context/payload.

## Frozen capability chain

The only permitted chain is:

```text
Stage 0.31B create use case
  -> Stage 0.31A build_receipt_candidate_request
  -> stateless create-only candidate capability
  -> Stage 0.30 create_candidate
```

For each valid invocation, the mapper executes exactly once. Only after mapping
succeeds may the create capability execute, exactly once. Evidence, trusted-fact,
or mapper failure must produce zero create-capability, repository-persistence,
and database calls.

Stage 0.31B must not call `MaterialReceiptRepository` directly and must not
contain SQL, a generic persistence interface, a generic `save` method, a raw
connection, or a generic transaction facility.

## Create-only adapter

The use case receives or retains only a stateless create-only capability. If an
outer composition root temporarily constructs the reviewed Stage 0.30 candidate
composition, it must extract or bind only the narrow create behavior through an
adapter that does not retain the broader object graph.

A bound `ReviewFacade.create_candidate` method is not sufficient containment if
its receiver remains recoverable. The returned Stage 0.31B use-case object must
not retain or permit traversal to:

- `ReviewFacade`;
- `MaterialReceiptRepository`;
- `CandidateDatabaseConfig`;
- candidate DSN, URL, username, or password;
- database connection or repository factory; or
- any confirmation, posting, revision, rejection, or cancellation capability.

Containment must be structural and behavioral, not dependent only on underscore
or name-mangling conventions.

## Candidate persistence authority and identity

Candidate persistence is authorized only through the existing Stage 0.30
`create_candidate` operation. The only permitted runtime database identity is:

```text
aios_material_receipt_candidate_runtime
```

The security-reviewed typed `CandidateDatabaseConfig` boundary remains confined
to the outer candidate composition root. Callers cannot select a username or
DSN. The `aios` administrator, material-stock reader, and posting identities are
not permitted.

The candidate secret may be loaded only during explicit outermost candidate
runtime composition. Importing Stage 0.31B or constructing inert mapper/use-case
components loads no environment, credential, or database connection. Secrets,
configuration, repositories, and connections must not be returned or retained
by the higher-level use case.

## Posting and confirmation exclusion

Stage 0.31B requires all of the following:

- `InventoryPostingRepository` construction: ZERO;
- `PostingDatabaseConfig` construction: ZERO;
- posting credential loading: ZERO;
- posting runtime identity use: ZERO;
- confirmation authority: NONE and unreachable; and
- posting authority: NONE and unreachable.

`confirm_receipt`, `post_confirmed_receipt`, `revise_candidate`,
`reject_receipt`, `cancel_receipt`, `cancel_receipt_item`, and generic repository
methods must not be reachable through the public API or returned object graph.

## Source and fact authority

`source_asset_reference` is determined exclusively by the Stage 0.31A mapper
from verified retained `IngestionResult` evidence. Stage 0.31B accepts no
separate source reference, manifest, Registry ID, or arbitrary source metadata.

`TrustedReceiptFacts` is the only business-fact input. Stage 0.31B must not
construct it or derive receipt facts from `IngestionResult.metadata`,
`IngestionResult.text`, Telegram caption/document metadata, OCR, Vision, LLM,
Brain output, generic mappings, or heuristic parsing. Raw untrusted objects are
not accepted in place of the exact trusted DTO.

## Transaction and result contract

Stage 0.31B owns no database transaction. The Stage 0.31A mapper remains inert;
the existing candidate repository operation owns its persistence transaction.
No outer, nested, or split transaction is introduced.

The operation returns the existing bounded `ReceiptForReview`. Successful
creation yields the existing review-safe `NEEDS_REVIEW` state. Confirmation
fields gain no authority, and no inventory movement or stock mutation occurs.
