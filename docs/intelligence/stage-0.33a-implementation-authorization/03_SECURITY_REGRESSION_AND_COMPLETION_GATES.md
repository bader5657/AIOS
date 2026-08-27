# Security, Regression, and Completion Gates

## Mandatory unit and exact-taxonomy tests

Permanent tests must assert one exact result per input:

| Case | Required result |
|---|---|
| actor absent/omitted/`None` | `ACTOR_REQUIRED` |
| forged or corrupted exact `ActorContext` | `ACTOR_INVALID` |
| malformed generic actor | `ACTOR_INVALID` |
| blank/control/Unicode-lookalike/path/SQL/DSN/credential-shaped generic-invalid value | `ACTOR_INVALID` |
| generic-valid `reviewer:<id>` | `ACTOR_UNAUTHORIZED` |
| generic-valid legacy `operator:<non-UUID-id>` | `ACTOR_UNAUTHORIZED` |
| canonical lowercase operator UUIDv4 | successful authorization and candidate creation |
| same source after valid authorization | `SOURCE_ACTIVE_RECEIPT_EXISTS` |

No test may accept multiple codes. `ACTOR_PROVENANCE_CONFLICT` is not authorized. Raw internal exception text must not escape.

`ACTOR_REQUIRED`, `ACTOR_INVALID`, and `ACTOR_UNAUTHORIZED` must fail before mapper/candidate persistence activity. Required zero-side-effect evidence includes mapper calls `= 0`, candidate capability calls `= 0`, repository construction/calls `= 0` where the governed design permits, database connections `= 0`, and mutations `= 0`.

## Forged-object tests

Every public candidate boundary revalidates current state. Tests must cover:

- `object.__new__` forgery;
- `object.__setattr__` mutation where technically possible;
- subclass substitution where exact-type policy applies;
- manual reconstruction;
- malformed deserialization;
- post-construction mutation; and
- attribute injection where the object model permits.

Construction-time validation alone is insufficient.

## Trusted-boundary adversarial tests

Only a separately supplied authenticated `ActorContext` from the trusted AIOS identity boundary may provide creator authority. Tests must prove creator authority cannot come directly or indirectly from:

- Telegram text or caption;
- Telegram sender ID or arbitrary metadata;
- `IngestionResult` metadata;
- `TrustedReceiptFacts`;
- document or supplier values;
- OCR, Vision, LLM, or Brain output;
- arbitrary dictionaries/JSON; or
- database login username.

Stage 0.33A does not implement a Telegram identity resolver. Future Telegram sender-to-AIOS identity binding remains separately governed.

## Provenance non-exposure tests

Creator provenance must not automatically reach:

- Brain input or LLM prompt/context;
- Telegram acknowledgement/reply;
- Universal Ingestion result/metadata;
- generic log or error output;
- duplicate-source response;
- generic provenance-query API; or
- generic repository getter or unrelated public review DTO.

Tests must inspect outputs and reachable object graphs. No public provenance-read feature is authorized.

## Exception-graph gate

Recursive adversarial inspection of validation, capability, repository, and database failure paths must prove outward errors cannot reach:

- credentials or tokens;
- DSNs or SQL;
- repository/configuration objects;
- identity-resolver or Telegram-binding internals;
- database connections;
- traceback locals; or
- unsafe original actor input.

Only bounded actor codes, existing bounded candidate codes, and explicitly safe values may escape.

## Exported service-surface tests

`tests/unit/material_receipts/test_service.py` must permanently prove:

- `MaterialReceiptService` has no `create_receipt_candidate` method;
- no `create`, `save`, `insert`, `execute`, `execute_sql`, `dispatch`, `invoke`, `run`, `handle`, or equivalent unrestricted candidate-create alias exists;
- no exported service candidate method accepts raw `actor_reference`, `created_by_actor_reference`, dictionary/mapping/JSON actor, arbitrary actor kwargs, or `ActorContext`;
- no repository getter, database URL getter, generic SQL, generic mutation, or delete surface exists;
- existing revise, retrieve/review, confirmation, rejection, cancellation, and item-cancellation delegation remains unchanged where applicable; and
- `MaterialReceiptService` remains exported without importing application-layer actor authorization.

Creator-less/raw-actor bypass absence must also be corroborated by the Stage 0.33A composition and security graph tests. The canonical creator string may cross only internal typed persistence seams after candidate authorization.

## Test-to-file mapping addition

- Exported service create-surface elimination → `tests/unit/material_receipts/test_service.py`
- Creator-less/raw-actor bypass absence → `tests/unit/material_receipts/test_service.py` plus Stage 0.33A composition/security tests
- Existing service non-regression → `tests/unit/material_receipts/test_service.py`

## Regression gates

The implementation PR must preserve and run the repository's relevant existing unit/integration suite plus mandatory new Stage 0.33A tests. Required regression evidence includes:

- generic `ActorContext` accepts its already-governed broader legitimate forms for unrelated consumers;
- candidate authorization is operation-specific;
- Stage 0.32 same-source concurrency/idempotency remains exact;
- Migration 0004 and its index are untouched;
- revision/review/confirmation/rejection/cancellation/posting never rewrite creator;
- terminal replacement uses a newly authenticated actor;
- posting, stock, movement, reader, and admin authority do not expand;
- no dependency, ORM, framework, service, runtime, Telegram, or Universal Ingestion change; and
- no creator read exposure.

## Dependency policy

Use Python standard library plus existing dependencies only. Standard-library `uuid` is preferred. No new package, ORM, framework, generic identity service, or audit platform is authorized. If a new dependency appears unavoidable, stop and obtain separate approval.

## Implementation PR completion evidence

The one authorized implementation PR, once authority is active, must report:

- exact base and head commits;
- changed files matching the allowlist only;
- migration inventory recheck showing `0005` was free before creation;
- all unit and disposable PostgreSQL commands/results;
- exact CHECK pass/fail evidence;
- atomic success and rollback evidence;
- privilege/ownership/ACL evidence;
- Stage 0.32 index and behavior preservation;
- lifecycle immutability and replacement evidence;
- trust-boundary, forgery, non-exposure, and exception-graph evidence;
- dependency diff;
- `MaterialReceiptService` create surface reported `REMOVED`;
- creator-less exported candidate paths reported `0`;
- raw-actor exported candidate paths reported `0`;
- governed ActorContext candidate-creation path reported `1`;
- repository internal persistence create path reported `1 governed internal path`; and
- confirmation that production PostgreSQL was not contacted.

It must receive a separate independent implementation review before merge. The implementation PR must not deploy Migration 0005 or activate runtime traffic.

## Stop conditions

Stop implementation and return to governance if:

- Migration `0005` is no longer free;
- exact PostgreSQL UUIDv4 enforcement cannot be implemented;
- the file allowlist is insufficient;
- the caller audit finds a live path requiring an out-of-allowlist change;
- any exported creator-less or raw-actor candidate-creation path would remain;
- a new dependency is required;
- production access would be needed;
- a generic `ActorContext` consumer would regress;
- Stage 0.32 behavior or index would change;
- creator immutability/atomicity cannot be proven;
- privilege expansion exceeds the one candidate `INSERT` column; or
- secrets, internal objects, or creator identity would be exposed.

## Authority and operational closure

This documentation PR does not activate implementation authority until independently reviewed, merged, synchronized, inventory-reverified, and allowlist-confirmed as specified in `00_AUTHORITY_BASIS_SCOPE_AND_OWNER_APPROVAL.md`.

Even after a successful implementation merge:

- actor-provenance operational gate: **OPEN** pending Stage 0.33B;
- runtime-secret rotation/activation safety gate: **OPEN**;
- explicit production safety review: **OPEN**;
- production PostgreSQL/deployment: **NOT AUTHORIZED**;
- production candidate activation: **NOT AUTHORIZED**; and
- Telegram identity binding/runtime activation: **NOT AUTHORIZED**.

## Next official action

Independent governance/architecture/security review of this implementation-authorization PR. If it passes, merge this package, synchronize clean `main`, reverify migration inventory and allowlist, and only then record Stage 0.33A implementation authority active for one implementation branch/PR.
