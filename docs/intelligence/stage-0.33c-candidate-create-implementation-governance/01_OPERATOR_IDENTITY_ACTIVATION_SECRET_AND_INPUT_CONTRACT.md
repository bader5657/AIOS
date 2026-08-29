# Operator Identity, Activation, Secret, and Input Contract

## Trusted authorization artifact

The repository has no existing trusted production operator resolver suitable
for this capability. The implementation therefore creates a narrow resolver for
one fixed governance artifact; it does not create a general identity system.

The only authorization location is exactly:

`/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/authorization.json`

The path is a compile-time constant and is not accepted as caller input or read
from an environment variable. Every path component and the file must be real,
not a symlink. The final artifact must be a regular file owned
`root:aiosadmin`, mode `0440`. The implementation does not create or modify this
production path. A later, separately reviewed first-write authority must create
the artifact exclusively, freeze its raw-byte SHA-256, and remove or disable it
after the governed attempt.

The compact UTF-8 JSON object has an exact closed schema:

- `schema_version`: `"aios-stage-0.33c-candidate-create-authorization-v1"`;
- `enabled`: exact boolean `true`;
- `authorization_id`: canonical lowercase UUIDv4;
- `not_before_utc` and `expires_at_utc`: canonical UTC timestamps, with a short
  future authority-frozen window;
- `max_requests`: exact integer `1`;
- `operator_actor_reference`: `operator:<canonical-lowercase-UUIDv4>`;
- `source_manifest_reference`: exact canonical retained-manifest path;
- `source_manifest_sha256`: lowercase SHA-256;
- `trusted_facts_sha256`: lowercase SHA-256 of the future authority-frozen
  canonical facts representation; and
- `evidence_session_id`: future authority-frozen canonical session identifier.

Unknown, missing, duplicate, wrong-type, noncanonical, expired, premature, or
mismatched fields fail closed. The artifact is not itself an authority until a
later governance package independently hash-binds and activates it.

`authorization_id` is bound to the exact immutable authorization artifact bytes
by the future authority's frozen raw-byte SHA-256. It contains no path separator
and is never accepted separately from those validated bytes.

## Durable authorization consumption

The future operator must separately provision this exact real, non-symlink
directory before activation:

`/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/consumed`

Implementation does not provision, chmod, chown, repair, or remove it. For one
validated authorization, the only consumption path is deterministically:

```text
/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/consumed/<authorization_id>.json
```

The validated canonical lowercase UUIDv4 is the complete filename stem; path
separators, traversal, caller-selected paths, and alternate filenames are
prohibited. The record must be a real regular non-symlink file, owned by the
exact non-privileged Unix identity running the controlled process, with its same
governed runtime group where applicable, and mode `0600`. Group or world write
is prohibited. Unexpected directory or file owner, group, mode, type, or symlink
state fails closed before DB connection; implementation performs no repair.

The sole atomic claim is the safe Python equivalent of:

```python
os.open(
    consumption_path,
    os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
    0o600,
)
```

There is no `exists()`-then-create race, overwrite, truncation, rename over an
existing path, unlink/retry, or alternate filename. Successful exclusive
creation is the permanent consumption boundary; process memory or a local lock
is never authoritative.

The record contains exactly `schema_version`, `authorization_id`,
`authorization_artifact_sha256`, `consumed_at_utc`, `operator_reference` or its
approved safe representation, `source_evidence_sha256`, `correlation_id`, and
`state` exactly `"CONSUMED"`. It contains no database URL/password, token, API
or private key, `runtime.env`, raw business payload, or unrestricted source.

Before DB capability, the winning caller must fully write and flush the record,
`fsync` the file, close it safely, open and `fsync` the real consumed parent
directory, and close that descriptor. This winner durability rule does not delay
or weaken consumption at successful `O_EXCL` creation.

When `O_EXCL` reports the exact path already exists, a losing caller performs
only bounded non-following metadata validation. It must not open, read, or parse
the record body. A safe regular non-symlink file at the governed path with the
creation-time owner/group and mode `0600` returns `AUTHORIZATION_CONSUMED` even
when zero-byte, partially written, or not yet fsynced. No post-create chmod or
chown is allowed. A symlink, directory, socket, FIFO, device, unexpected type,
wrong owner/mode, or unsafe path returns
`AUTHORIZATION_CONSUMPTION_STATE_INVALID`. Neither result permits repository
creation, overwrite, deletion, repair, wait, polling, takeover, or retry.

Authorization state and evidence quality are distinct. Successful `O_EXCL` means
`CONSUMED` permanently. Full JSON review may classify consumption evidence as
`COMPLETE` or `INCOMPLETE`; incomplete evidence never means unconsumed and never
permits execution. Full JSON validation is for offline audit, not second-caller
authorization reuse decisions.

## Activation mechanism and ordering

Default activation is **DISABLED**. Missing authorization, `enabled != true`,
invalid ownership/mode/type/path, invalid schema, expired window, hash mismatch,
source/facts mismatch, or consumed request budget yields a bounded disabled or
ineligible result. Database privileges are infrastructure, never the activation
switch.

The exact future evaluation and claim order is:

1. read and validate the fixed activation artifact;
2. verify artifact file, type, owner, and mode;
3. verify canonical `authorization_id` and artifact SHA binding;
4. verify enabled state and `max_requests == 1`;
5. verify activation window and expiry;
6. verify candidate-specific canonical operator identity;
7. verify retained evidence identity and SHA binding;
8. verify approved real-business facts and digest binding;
9. revalidate exact DTO, item-count, quantity, and unit contracts;
10. derive the sole authorization-ID-bound consumption path;
11. atomically create it with `O_EXCL | O_NOFOLLOW`;
12. write the bounded consumption record;
13. flush it;
14. `fsync` the file;
15. `fsync` the consumed parent directory; and
16. only then construct/open DB capability and invoke the governed create once.

No PostgreSQL connection or credential read occurs before step 16. Failure before
claim leaves authority unconsumed, the consumption path absent, connection count
zero, and writes zero. Successful exclusive creation permanently consumes it.
Later write, flush, either fsync, repository, connection, transaction, insert,
crash, or evidence-finalization failure never restores authority or permits retry.
Durability failure after claim prohibits DB connection while remaining consumed.
A started DB transaction failure rolls back that same transaction.

The operator actor is produced solely from the verified, later hash-bound,
root-owned authorization artifact. It is never supplied by the request,
business facts, environment, Telegram identity, username, arbitrary JSON, or
database login. The controlled module constructs the exact `ActorContext`; the
existing Stage 0.33A boundary revalidates and captures Actor A once. No Actor B,
mutable downstream context, override, global registry, or raw actor escape is
permitted.

## Candidate input contract

The controlled request reuses the authoritative exact DTOs; it invents no
parallel business model:

- `IngestionResult` must satisfy `source_context_from_ingestion_result`, refer to
  a retained canonical regular manifest with matching UUID identity, and match
  the authorization source path and digest;
- `TrustedReceiptFacts` requires canonical supplier name, optional canonical
  document number/date, timezone-aware `received_at`, and a nonempty tuple of
  items; and
- `TrustedReceiptItemFacts` requires unique positive line numbers, governed
  optional descriptive/material fields, bounded exact Decimal packaging values,
  and unit exactly `sheet`, `pcs`, `kg`, `roll`, or `pack`.

The 1–500 item contract is already authoritative in
`core/app/material_receipts/candidate_input.py` through nonempty validation and
`MAX_RECEIPT_ITEMS = 500`. Other existing limits and exact packaging formula
remain unchanged. Receipt and item UUIDv4 values continue to be generated by the
existing mapper. Status is not input.

Real production input requires an exact later Project Owner eligibility decision
and hash binding. Synthetic production input, hardcoded business values, seeds,
fallback facts, arbitrary ingestion payloads, and arbitrary file paths are
prohibited.

## Credential boundary

The entrypoint accepts no credential, DSN, environment mapping, or secret path.
It must not load `runtime.env`. Only the existing
`MaterialReceiptRepository.from_environment()` may obtain
`AIOS_MATERIAL_RECEIPT_CANDIDATE_DB_PASSWORD`, after all deterministic
eligibility gates have passed. How a later governed executor receives the
already-provisioned process environment is part of later execution governance;
this implementation neither provisions nor rotates it.

Permitted metadata is limited to fixed role names, authorization/evidence
identities, safe source/facts digests, bounded failure code, timestamps, result
IDs/status, and counts. Passwords, tokens, API keys, private keys, DSNs,
`runtime.env` content, environment dumps, and unrestricted business facts must
never enter logs, errors, evidence, or return metadata.

## Database, transaction, and exact effects

The exact runtime role remains
`aios_material_receipt_candidate_runtime`, with governed membership in
`aios_material_receipt_candidate_writer`. No owner/admin connection, role
change, membership change, or GRANT is authorized.

One eligible call uses the existing one-connection, one-`READ COMMITTED`
repository transaction. It may create exactly:

- one `material_receipts` row for the request, ending `NEEDS_REVIEW`; and
- exactly `len(TrustedReceiptFacts.items)` `material_receipt_items` rows linked
  to that receipt, each ending `NEEDS_REVIEW`.

It creates or updates zero `inventory_movements` and zero `material_stock` rows,
and produces zero confirmation or posting effects. Confirmation fields remain
unset. No caller-selected status or automatic transition is accepted.

## Duplicate, concurrency, failure, and deactivation

Source identity is the exact retained `source_asset_reference`. The existing
`material_receipts_source_asset_active_uidx` serializes active-source creation.
A duplicate returns bounded `SOURCE_ACTIVE_RECEIPT_EXISTS`; it does not return an
existing candidate or create extra rows.

Same-authorization concurrency is a control-plane test: for arbitrary bounded N
simultaneous callers using one authorization, exactly one wins `O_EXCL`; all
N-1 losers validate safe metadata only and return `AUTHORIZATION_CONSUMED`. They
do not read the payload, wait, poll, lock, take over, construct the repository,
connect, persist, or retry. The winner may proceed only after durability.
Filesystem existence remains authoritative after crash, service restart, or a
new process even if the payload is empty, partial, complete-but-unfsynced, or
classified `INCOMPLETE` for evidence review.

Database duplicate/source concurrency is a separate persistence test. It uses
the lower governed application/repository harness, or two independently valid
test-only authorization identities when the controlled boundary must be used. It
proves one source success and one `SOURCE_ACTIVE_RECEIPT_EXISTS` without reusing
one consumed production-style authorization. Thus `max_requests = 1` means one
successful atomic claim, not a commit plus another DB-reaching call.

Any repository error rolls back the same transaction, leaves no partial receipt
or item rows, returns a bounded failure, and triggers no retry, confirmation,
posting, inventory, or stock action.

Operational deactivation is the absence, expiry, disablement, consumption, or
later governed removal of the fixed authorization artifact/caller boundary. An
existing consumed record remains immutable historical state. Reauthorization
requires a new canonical authorization ID and separately governed artifact. It
does not use Migration DOWN, schema/provenance removal, ownership changes,
privilege broadening, evidence rewriting, or data deletion.
