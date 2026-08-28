# Exact Implementation File Allowlist and API Contract

## Allowlist rule

A future implementation may create or modify only the exact paths below. Directory-wide authority is not granted. Unrelated changes inside an allowed file are prohibited. If implementation evidence requires another path, stop and obtain an amended authorization before changing it.

The amended allowlist contains exactly **23 paths**: nine application/support paths, two migration paths, seven unit-test paths, and five integration-test paths. The 23rd path is authorized only under the narrow conditions recorded in `04_ALLOWLIST_AMENDMENT_CANDIDATE_INPUT_TEST.md`.

## Application allowlist

| Path | Authorized narrow purpose |
|---|---|
| `core/app/material_receipts/actor_provenance.py` | New candidate-only validator and canonical-reference production; no generic framework or capabilities. |
| `core/app/material_receipts/create_from_ingestion.py` | Add the distinct `actor_context` argument, validate before mapping/capability activity, propagate only the canonical reference, and preserve bounded exception containment. |
| `core/app/material_receipts/review_use_cases.py` | Revalidate current `ActorContext` at the candidate-create public boundary and pass the authorized canonical creator through create only; generic `ActorContext` grammar and unrelated consumers remain unchanged. |
| `core/app/material_receipts/ports.py` | Add the minimum typed create-operation parameter needed to carry the canonical creator reference; no generic actor or repository surface. |
| `core/app/material_receipts/composition.py` | Carry the creator through the stateless candidate operation into repository creation; no retained graph or runtime activation. |
| `core/app/material_receipts/results.py` | Add only `ACTOR_REQUIRED`, `ACTOR_INVALID`, and `ACTOR_UNAUTHORIZED` to the bounded public review failure taxonomy. |
| `core/material_receipts/repository.py` | Accept the canonical creator as a separate create argument and insert it in the existing receipt transaction; keep all reads and lifecycle updates free of provenance exposure/mutation. |
| `core/material_receipts/service.py` | Remove only the exported creator-less `MaterialReceiptService.create_receipt_candidate` method; retain the class and unrelated operations unchanged, add no replacement create alias/raw-actor API, and import no application-layer actor module. |
| `scripts/admin/bootstrap_material_writer_secrets.py` | Update only the hard-coded candidate receipt `INSERT` column matrix and matching ACL verification count/list for `created_by_actor_reference`; no credential, execution, role attribute, membership, ownership, posting, or runtime behavior change. |

No change is authorized to `core/material_receipts/models.py`, public review result DTOs, ingestion DTOs, `TrustedReceiptFacts`, Telegram code, Universal Ingestion, posting code, stock code, or movement code. Creator provenance must not be added to unrelated read DTOs.

`core/material_receipts/__init__.py` remains excluded: `MaterialReceiptService` stays exported, while removal of one method requires no package-export change. If implementation discovers an independently justified need to edit the initializer, it must stop and return to governance.

## Migration allowlist

Subject to the implementation-start inventory recheck confirming `0005` is free:

- `migrations/postgres/0005_add_material_receipt_creator_provenance.up.sql`
- `migrations/postgres/0005_add_material_receipt_creator_provenance.down.sql`

No other migration file may be created or modified. Migration 0004 and `material_receipts_source_asset_active_uidx` are immutable under this authority.

## Unit-test allowlist

| Path | Authorized proof |
|---|---|
| `tests/unit/app/material_receipts/test_actor_provenance.py` | New candidate-validator grammar, taxonomy, forgery, and exact-code tests. |
| `tests/unit/app/material_receipts/test_create_from_ingestion.py` | API ordering, presence, zero-call, propagation, bounded exception, and non-exposure tests. |
| `tests/unit/app/material_receipts/test_review_use_cases.py` | Candidate-boundary revalidation and generic `ActorContext` non-regression. |
| `tests/unit/app/material_receipts/test_composition_boundaries.py` | Narrow capability propagation and object/authority graph tests. |
| `tests/unit/app/material_receipts/test_candidate_input.py` | Repair only the stale public repository-create monkeypatch while preserving or strengthening the existing invalid-input zero-operational-capability security proof against the current private/internal persistence architecture; all unrelated tests in this file remain unchanged. |
| `tests/unit/admin/test_bootstrap_material_writer_secrets.py` | Exact candidate `INSERT` column/ACL expectation delta and proof of no broader bootstrap change. |
| `tests/unit/material_receipts/test_service.py` | Prove removal of the creator-less service method, absence of raw-actor/create aliases and generic mutation surfaces, and preservation of unrelated service delegation. |

## Integration-test allowlist

| Path | Authorized proof |
|---|---|
| `tests/integration/business_context/test_stage033a_actor_provenance_postgres.py` | New Migration 0005 lifecycle, schema, CHECK, privileges, atomicity, immutability, terminal replacement, preservation, and adversarial PostgreSQL tests. |
| `tests/integration/business_context/test_create_from_ingestion_composition.py` | Real disposable create-path API propagation, atomic success/failure, trust-boundary, and non-exposure coverage. |
| `tests/integration/business_context/test_material_receipt_repository.py` | Creator INSERT, atomic rollback, immutable lifecycle SQL, and no read-surface regression. |
| `tests/integration/business_context/test_material_writer_security_boundaries.py` | Production-equivalent disposable candidate/posting privilege denial and preservation proof. |
| `tests/integration/business_context/test_stage032_postgres.py` | Existing source-idempotency path updated only for the required actor argument and exact Stage 0.32 non-regression assertions. |

The existing `tests/integration/business_context/disposable_postgres.py` mechanism must be reused unchanged. If it cannot safely support the tests, stop and return to governance; modification is not authorized by this package.

## Frozen actor evaluation contract

The required order at every governed candidate-creation public boundary is:

1. actor presence;
2. exact generic `ActorContext` structural/trust revalidation of current state;
3. candidate-specific authorization; and
4. mapper and candidate-creation activity.

Exact outcomes:

| Input/state | Public outcome |
|---|---|
| no actor, omitted actor, or `None` where mandatory | `ACTOR_REQUIRED` |
| forged/corrupted object, invalid exact DTO type, or generic-invalid representation | `ACTOR_INVALID` |
| generic-valid `reviewer:<id>` | `ACTOR_UNAUTHORIZED` |
| generic-valid legacy `operator:<non-UUID-id>` | `ACTOR_UNAUTHORIZED` |
| `operator:<canonical-lowercase-uuidv4>` | authorized; continue |
| same source after valid authorization | `SOURCE_ACTIVE_RECEIPT_EXISTS` |

No input may have multiple accepted public codes. `ACTOR_PROVENANCE_CONFLICT` is not authorized.

## Candidate-specific validator

The new narrow validator is conceptually:

```python
authorize_candidate_creation_actor(actor_context: ActorContext) -> str
```

It must revalidate the exact trusted DTO type and current state according to the existing policy, preserve generic `ActorContext` behavior, accept only operator/canonical-lowercase-hyphenated UUIDv4, and return one canonical non-secret reference. It exposes no database, repository, credential, resolver, transport, or general authorization capability.

The validator must not become a global identity/authorization framework. Standard-library `uuid` should be used where sufficient; no new dependency is authorized absent separate justification and approval.

## API evolution

The authorized public application API is:

```python
create_review_candidate_from_ingestion(
    ingestion_result,
    trusted_receipt_facts,
    actor_context: ActorContext,
)
```

`ActorContext` remains distinct from `IngestionResult` and `TrustedReceiptFacts`. No raw actor string, generic dictionary, or arbitrary JSON actor API is authorized. Validation precedes mapper, candidate capability, repository construction/calls where the design permits, database connection, and database mutation.

## Propagation and persistence seam

Only the canonical creator string returned by the candidate validator may cross the typed create-operation port and repository boundary. It remains separate from ingestion/trusted-fact DTOs and public read results.

The repository must insert `created_by_actor_reference` directly with the receipt header inside the existing transaction. Receipt header, all items, and creator provenance commit together or roll back together. A post-insert provenance `UPDATE` is prohibited.

All revision, review, confirmation, rejection, cancellation, and posting SQL must omit `created_by_actor_reference`. No generic update or getter is authorized.

## Exported service create-surface decision

`MaterialReceiptService` remains exported for its already-governed non-creation operations. Stage 0.33A requires removal of `MaterialReceiptService.create_receipt_candidate`; after implementation:

```python
hasattr(MaterialReceiptService, "create_receipt_candidate") is False
```

No replacement `create`, `save`, `insert`, `execute`, `execute_sql`, `dispatch`, `invoke`, `run`, `handle`, arbitrary-kwargs, or other alias may provide candidate creation. The service must accept neither `actor_reference: str`, `created_by_actor_reference: str`, dictionaries/mappings/JSON, nor `ActorContext` for candidate creation. It must not import `core.app.material_receipts.actor_provenance` or another higher application-layer identity/authorization module.

The repository may require the already-authorized canonical creator as a separate internal create argument. That persistence seam is not authentication or authorization authority and is callable by the governed composition only with the validator-produced value. `MaterialReceiptRepository.create_receipt_candidate` must remain absent from the public repository surface. A private/internal seam such as `_create_receipt_candidate`, or the exact current implementation equivalent, may be used and narrowly sentineled by the amended candidate-input test when materially useful. No test-only public alias, generic/public repository construction, or raw-actor API is authorized.

## Required caller audit

Before removing the service method, implementation must perform a repository-wide static/call-site audit for `MaterialReceiptService.create_receipt_candidate` and equivalent imports/aliases.

- If no live caller exists, remove the method and proceed.
- If a caller is found, classify it as obsolete/dead, test-only, a legitimate governed application path, or an unauthorized bypass.
- Do not automatically adapt any caller.
- If adaptation requires a path outside this 23-path allowlist, stop and return to governance.

No out-of-allowlist caller is automatically modifiable.

## Single-path completion invariant

Implementation completion requires:

```text
MaterialReceiptService create surface = REMOVED
externally reachable creator-less candidate paths = 0
externally reachable raw-actor candidate paths = 0
governed ActorContext candidate-creation path = 1
repository internal persistence create path = 1 governed internal path
```

More than one externally reachable candidate-creation path blocks implementation merge.
