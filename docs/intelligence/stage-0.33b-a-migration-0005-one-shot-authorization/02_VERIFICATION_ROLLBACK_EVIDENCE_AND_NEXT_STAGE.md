# Stage 0.33B-A Verification, Rollback, Evidence, and Next Stage

## Pre-COMMIT structural and privilege proof

After the exact UP artifact executes but before COMMIT, PostgreSQL catalog proof
must establish:

- creator column present, type `TEXT`, NOT NULL true, and default none;
- exact named creator CHECK present with the reviewed UUIDv4/operator grammar;
- no new provenance index and unchanged Stage 0.32 index;
- candidate writer `INSERT(created_by_actor_reference)` yes;
- candidate creator UPDATE, posting creator UPDATE, and reader write all no; and
- roles/attributes, memberships, ADMIN OPTION, and owners unchanged.

No synthetic INSERT, business write, or privilege write-test is permitted.

## Preservation and rollback contract

ALTER TABLE, CHECK, and GRANT must remain in the same explicit transaction. If
any pre-COMMIT gate fails, ROLLBACK must remove the creator column, creator CHECK,
and creator-column INSERT grant. No partial schema or ACL delta may persist.

Before COMMIT, while the same four locks remain continuously held, freshly
recompute the same four canonical fingerprints and require exact equality with
the locked pre-DDL values. No row-count-only fallback or unlocked comparison is
permitted. Migration 0005 must create zero business rows. Compare the complete
locked security/object state and permit only the creator column, creator CHECK,
and candidate-writer creator INSERT grant. Owners, roles, memberships, ADMIN
OPTION, triggers/functions, schemas/extensions, relations, unrelated ACLs/
indexes/constraints, and all other objects must remain unchanged. Any data,
security, or object difference requires ROLLBACK and STOP.

Before COMMIT also require the same `aios-postgres` identity, running/healthy
state, unchanged restart count, normal PostgreSQL response, unchanged
`aios.service`, unchanged `runtime.env`, and absent candidate activation. Any
failure requires ROLLBACK and STOP.

COMMIT is permitted only if every source/authorization/evidence/target/health/
lock/prestate/index/zero-row/fingerprint/security/hash/DDL/structural/privilege/
preservation gate passes. Transactional GRANT rollback is required. There is no
partial acceptance, warning-as-PASS, retry, or inferred evidence.

## Mandatory execution-evidence retention

Stage 0.33B-D must not launch its production control plane until the following
immutable, bounded, secret-safe contract is provisioned and its initial records
durably written. Evidence is captured during execution, never reconstructed
afterward.

### Narrow filesystem sub-authority and exact root

After this PR receives independent PASS and is merged unchanged, but before any
production PostgreSQL launch, the pre-execution filesystem sub-authority permits
only provisioning and writing Stage 0.33B-D evidence at:

`/opt/aios/runtime/intelligence/production-execution-evidence/stage-0.33b-d`

The path must be a real, non-symbolic-link directory owned by
`aiosadmin:aiosadmin` with mode `0750`. It may be created if absent and its exact
owner/mode set or verified. Missing directories strictly required in this exact
root chain may be created only where already-governed parent ownership permits;
no other parent may be modified. If permission, ownership, or path safety cannot
be established: STOP, DO NOT CONNECT, authority UNCONSUMED.

This sub-authority grants no production PostgreSQL or business-data authority,
application-code or `runtime.env` modification, service restart, Telegram,
Universal Ingestion, or candidate activation. It permits no recursive `chown` or
`chmod` outside the exact root, deletion/movement/overwrite of prior evidence,
unrelated or repository writes, secret writes, or arbitrary directory creation.
It is limited to the exact root and one new session directory. Evidence creation
does not consume Migration 0005 authority.

### Session identity and exclusive creation

Before launch generate exactly one new ID with format
`stage-0.33b-d-migration-0005-<UTC_TIMESTAMP>-<UUIDV4>`, where the timestamp is
UTC `YYYYMMDDTHHMMSSffffffZ` and the UUID is canonical lowercase UUIDv4. Example
shape only:

`stage-0.33b-d-migration-0005-20260828T123456123456Z-xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx`

Create `<evidence-root>/<session-id>` with exclusive new-directory semantics. It
must be a real non-symlink directory owned by `aiosadmin:aiosadmin`, mode `0750`.
Prefer one generated ID and fail closed on collision; only a deterministic
procedure fixed before execution may permit one fresh UUID generation before
production launch. Never reuse, overwrite, or silently select another ID.

The session contains exactly `execution.jsonl` and, only at finalization,
`manifest.json`; no other v1 file is required. Before launch create
`execution.jsonl` with semantics equivalent to `O_CREAT | O_EXCL`, no symlink
following, owner/group `aiosadmin:aiosadmin`, mode `0640`. An existing file is a
HARD STOP: no overwrite or truncate. `manifest.json` must not exist before
finalization and must then be created exclusively; an existing manifest is a
HARD STOP and is never updated in place.

### JSONL schema, events, and bounded output

`execution.jsonl` is UTF-8 JSON Lines with exactly one JSON object per line.
Every record includes `seq`, `timestamp_utc`, `stage`, `session_id`, `event`, and
`status`. Where relevant it may include only bounded fields such as
`authority_pr`, `authorization_reviewed_head`, `authorization_merge_commit`,
`current_main`, `target_identity`, `control_plane_identity`,
`migration_up_sha256`, `gate_name`, `gate_result`, `transaction_state`, and
`final_classification`.

Reached phases must retain at least these events; fail-fast paths may omit events
never reached:

```text
evidence_session_initialized
source_gate_pass
authorization_gate_pass
evidence_hash_gate_pass
migration_hash_gate_pass
target_precheck_pass
production_control_plane_launch_attempt
production_connection_result
transaction_begin_result
lock_L01_result
lock_L02_result
lock_L03_result
lock_L04_result
locked_identity_result
migration_prestate_result
stage_032_index_result
zero_row_result
pre_ddl_fingerprint_result
security_object_baseline_result
immediate_migration_hash_result
migration_up_result
structural_verifier_result
privilege_verifier_result
post_ddl_fingerprint_result
security_object_preservation_result
precommit_health_result
transaction_commit_or_rollback
postcommit_completion_result
final_classification
```

`postcommit_completion_result` is required only if COMMIT occurred. Records may
contain counts, digests, booleans, governed role/object names, commit/artifact
hashes, bounded status/error codes, and safe governed PostgreSQL catalog metadata.
They must not contain raw business rows, Telegram message or document contents,
passwords or password verifiers, tokens/bot tokens/API keys/private keys,
`DATABASE_URL`, credential-bearing DSNs, `runtime.env` contents, or arbitrary
exception locals. Failures may retain only sanitized fields such as
`error_class`, `bounded_error_code`, `safe_stage`, and `safe_operation`; never
environment dumps, connection URIs, or traceback locals containing credentials
or configuration.

### Durability and launch transition

After every critical phase, flush `execution.jsonl` and request filesystem
durability with `fsync` or equivalent durable file-sync semantics. Critical
phases include at minimum initialization before database launch, control-plane
launch result, all four locks acquired, locked pre-DDL baseline complete,
Migration UP result, pre-COMMIT verification complete, COMMIT/ROLLBACK result,
and final classification.

Before the first production launch, the root and session must be validated,
`execution.jsonl` exclusively created, and initial records flushed and fsynced.
Immediately before invoking the exact governed Docker/`psql` argv, append and
durably sync event `production_control_plane_launch_attempt` with status
`ATTEMPTING`. The launch attempt itself permanently consumes Migration 0005
authority regardless of launch outcome. If evidence write/flush/fsync fails
before launch: STOP and leave authority UNCONSUMED. If it fails after launch:
authority remains CONSUMED, fail closed according to transaction state, ROLLBACK
if still pre-COMMIT, and no retry.

### Finalization, secret scan, and manifest

On every terminal path after session creation—including PASS, BLOCKED, FAILED,
INCONCLUSIVE, ROLLBACK, and COMMITTED—the executor must attempt finalization.
First flush and fsync `execution.jsonl`, close it, secret-scan its bounded bytes,
then compute its SHA-256, byte size, and record count.

The scan must at minimum reject obvious `DATABASE_URL`, password-bearing URI,
PRIVATE KEY header, known token/key label, and `runtime.env` content leakage
without printing a discovered secret. A failed scan sets final classification
`EVIDENCE_SECRET_SAFETY_FAILURE`; if the transaction is still open pre-COMMIT,
ROLLBACK. There is no retry or leaked-content publication.

Create `manifest.json` exclusively with only these bounded fields:

```text
stage
session_id
authority_pr
authorization_reviewed_head
authorization_merge_commit
current_main
evidence_pr
evidence_merge_commit
migration_up_sha256
started_at_utc
finished_at_utc
final_classification
authority_consumed
transaction_outcome
execution_jsonl_sha256
execution_jsonl_bytes
execution_jsonl_record_count
secret_scan
container_identity_safe_reference
no_raw_business_rows
production_candidate_activation
```

The manifest contains no secrets. Flush and fsync it, fsync the session directory
where supported/practical, then set `execution.jsonl` and `manifest.json` to
read-only governance mode `0440` and never modify them again. The session remains
mode `0750`, every entry remains owned by `aiosadmin:aiosadmin`, no symlink exists,
and no additional file is required. Permission-finalization failure after launch
does not restore authority and must not cause a Migration 0005 rerun; return to
governance.

Compute SHA-256 over the complete final exact bytes of `manifest.json` and record
that SHA in the final operator/Codex report, not inside the manifest where it
would self-reference. The final report must also carry the required
`execution.jsonl` SHA recorded by the manifest.

If provisioning fails before launch, classify `STAGE 0.33B-D ACTIVATION BLOCKED
— EXECUTION EVIDENCE RETENTION NOT PROVISIONED`, DO NOT CONNECT, and leave
Migration 0005 authority UNCONSUMED. If a session was created but a later
pre-launch gate blocks launch, do not delete or rewrite it; finalize an
activation-blocked record where practical. A later separately authorized launch
uses a new session ID.

## Frozen Stage 0.33B-D execution order

No reordering is authorized:

A. all pre-launch repository, source, authorization, evidence-package/hash,
   migration-hash, non-PostgreSQL container metadata, and control-plane argv gates;
B. provision and validate the exact evidence root and session;
C. durably record the launch-attempt event;
D. first exact production control-plane launch attempt—authority CONSUMED;
E. `BEGIN`;
F. transaction-local controls;
G. L01 `material_receipts` ACCESS EXCLUSIVE, L02 `material_receipt_items` SHARE,
   L03 `inventory_movements` SHARE, L04 `material_stock` SHARE;
H. locked target identity;
I. creator objects absence;
J. Stage 0.32 index;
K. zero-row requirement;
L. four-table fingerprints;
M. security/object recheck;
N. immediate UP artifact hash;
O. exact Migration 0005 UP;
P. structural verifier;
Q. privilege verifier;
R. post-DDL four-table fingerprints;
S. security/object preservation;
T. pre-COMMIT health;
U. COMMIT only if all PASS, otherwise ROLLBACK;
V. bounded completion check only if COMMIT occurred; and
W. evidence finalization.

## Post-COMMIT completion and Stage 0.33B-V separation

After successful COMMIT, perform only the bounded execution-completion checks
already governed: same container identity, running/healthy state, unchanged
restart count, PostgreSQL responsive, `aios.service` unchanged, `runtime.env`
unchanged, Telegram unchanged, Universal Ingestion unchanged, and candidate
activation NO. This is not Stage 0.33B-V, and evidence finalization does not turn
it into Stage 0.33B-V.

If COMMIT succeeded but completion health is FAIL or INCONCLUSIVE, authority
remains consumed: do not rerun Migration 0005, do not execute DOWN, and return
to governance.

After Stage 0.33B-D PASS, a separate newly published, independently reviewed
authorization must permit exactly one fresh Stage 0.33B-V `BEGIN READ ONLY`
production post-deployment verification session. The actor-provenance
operational gate remains OPEN through authorization and deployment and closes
only after Stage 0.33B-D PASS and Stage 0.33B-V PASS. Stage 0.33B-V must carry its
own then-governed evidence contract.

Migration deployment does not activate candidate creation traffic, Telegram
actor binding, Universal Ingestion provenance flow, confirmation, posting, or
any runtime feature. Production candidate activation remains independently
governed and unauthorized.

## Publication safety record

| Control | Publication result |
|---|---|
| Production PostgreSQL contacted / SELECT | NO / NO |
| Production mutation | NONE |
| Production evidence root created | NO |
| Migration 0005 / Migration 0004 / DOWN | NOT EXECUTED |
| Ownership / roles / grants / memberships | UNCHANGED |
| Runtime / `runtime.env` | UNCHANGED |
| Telegram / Universal Ingestion | UNCHANGED |
| Candidate activation | NO |

```text
STAGE 0.33B-A MIGRATION 0005 ONE-SHOT EXECUTION AUTHORIZATION PUBLISHED
— REVIEWED STAGE 0.33B-PE EVIDENCE BOUND
— FOUR-TABLE PRESERVATION LOCKING FROZEN
— AUTHORITY CONSUMPTION AT FIRST PRODUCTION LAUNCH ATTEMPT
— EXECUTION-EVIDENCE FILESYSTEM RETENTION CONTRACT FROZEN
— READY FOR INDEPENDENT AUTHORIZATION REVIEW
— MIGRATION 0005 NOT YET AUTHORIZED TO EXECUTE
— PRODUCTION CANDIDATE ACTIVATION NOT AUTHORIZED
```
