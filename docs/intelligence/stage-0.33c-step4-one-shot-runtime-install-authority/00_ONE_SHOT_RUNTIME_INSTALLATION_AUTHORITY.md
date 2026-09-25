# Stage 0.33C-P4S6 One-Shot Runtime Package Installation Authority

## Authority identity, activation, and scope

Authority identifier: `9d29c855-0f23-4539-a9b9-2e17dc89c49d`.

This documentation creates one fail-closed, single-attempt, non-reusable future
authority to install only the exact approved Step-4 package pair. It is inactive
until this authority is independently reviewed and merged. This publication
does not execute or consume the authority, create runtime files, contact
PostgreSQL, import or invoke the harness, call
`controlled_create_review_candidate`, create a candidate, create
`authorization.json`, restart or reload a service, or begin Step 5.

The authority is bound to merged PR #277, reviewed head
`0ed8cd8d93bf171d5ac714e9c83b97d225504f40`, and merge commit
`ca7940b8b94237611a37189e0bed10b002167e78`. The future executor must prove that
baseline and this authority's eventual merge commit before claiming the one
attempt. A branch head, unmerged commit, moving `main`, or equivalent prose is
not sufficient.

The only package targets are, in this fixed publication order:

1. `/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/approved-input.json`;
2. `/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/approved-input-approval.json`.

No other package target is authorized. In particular,
`/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/authorization.json`
must remain absent and must not be created, modified, or consumed.

## Frozen identities and exact private byte source

| Binding | Frozen value |
|---|---|
| retained evidence manifest | `9801b5e4-453d-429a-b51f-e8ffaa17a2c9` |
| input semantic bytes | `1327` |
| input transport bytes | `1328` |
| input semantic-prefix SHA-256 | `e3c66fddf815c57f17baad49926c44588279d60cb4e78df867e0ae2189237a6d` |
| approval semantic bytes | `3579` |
| approval transport bytes | `3580` |
| approval semantic-prefix SHA-256 | `2ea9e735d7a5183a3e247abf57438d6e095fd7e9858d5ce688d221f7e9050f26` |
| harness SHA-256, binding context only | `b9fc9fb22724184696eabf02525bcc0a626bdff5ce3943ed31ba2e21130f5cad` |

## Frozen executor and merged-authority binding

| Binding | Frozen value |
|---|---|
| executor repository path | `docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/one_shot_install.py` |
| executor SHA-256 | `f649b19c09c9d719b11577b14bfad0ce458f5c4dd6ccfd88c6727594787c81aa` |
| interpreter/runtime | `/opt/aios/runtime/venv/bin/python`, governed Python `3.12.3` |
| run-as identity | Unix `root` (`euid=0`, account name `root`) |
| arguments/input model | no arguments; closed constants and the two fixed private sources only |
| security-critical helpers | none; all claim, verification, fd, fsync, staging, ownership, publication, and final-verification logic is contained in the frozen executor |

This is the only installation mechanism authorized. Root is required solely for
the fixed `root:aiosadmin` ownership transition; service-account privileges are
unchanged. The executor has no generic mode and accepts no target, source, hash,
owner, mode, manifest, approval, force, overwrite, retry, reset, or network
argument. It contains no raw package content and must not be imported as a helper.

Before claim, the executor computes its own SHA-256, requires the policy table
above to contain that exact digest, requires both tracked artifacts to be clean
at repository `HEAD`, proves merged PR #277 commit
`ca7940b8b94237611a37189e0bed10b002167e78` is an ancestor, and finds a
first-parent merge commit containing both this authority identifier and this
exact executor digest. The containing merge commit is recorded in the marker;
no unknown future merge SHA is hard-coded. Human merge is permitted only after
the final PR #278 head is independently reviewed, and its merge commit must
contain that reviewed executor identity and policy. An unmerged head, dirty
replacement, hash mismatch, absent containing merge, or post-review executor
change stops before claim. A later clean deployment remains bound to the
original containing merge, not merely moving `main`.

PR #283 (merge commit `7a07a48f4ad197d0a54f6d58e07e9b79f2dd7748`)
governs `trusted_facts_sha256` as the TF-A canonical deterministic
`TrustedReceiptFacts` DTO-projection digest. The installer maps the already
validated harness-native UTC timestamp to the same aware UTC datetime and uses
the existing `trusted_facts_sha256` helper; it does not hash the raw
`trusted_receipt_facts` subobject. This facts approval binding remains distinct
from the independently checked exact semantic-input and LF-inclusive transport
hashes. The approval schema and its single facts digest are unchanged.

The executor, Python standard library, and the repository-governed
`candidate_input`/`candidate_create_authorization` TF-A DTO/hash helpers are the
complete helper dependency surface. Network, PostgreSQL, service-control,
harness, candidate, and `authorization.json` behavior are prohibited.

## R13A final pre-claim activation and runtime truth

The installer remains unusable until the fixed activation record
`/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/p4s7-r13-post-merge-activation.json`
exists and validates. The record is not created by this amendment. A future
separately governed activation action must publish it exclusively without
replacement as a regular, non-symlink, single-link `root:root` file with mode
`0400`.

The activation record has exactly these members and no others:
`schema_version`, `authority_id`, `pr_number`, `reviewed_head_sha`,
`authority_merge_sha`, `expected_runtime_head`, `executor_sha256`,
`policy_reference`, and `activated_at_utc`. It requires schema
`aios-stage-0.33c-p4s7-r13-post-merge-activation-v1`, this authority identifier,
PR number `289`, reviewed head
`209618b845c844ad08915853fa1dfa07c1c9897a`, this policy path, the final
policy-bound executor SHA, three canonical lowercase commit/SHA identities, and
a canonical microsecond UTC activation timestamp.

Before claim, the executor itself uses `/usr/bin/git -C /opt/aios-src` with a
fixed minimal `PATH` and fails closed if Git or repository truth is unavailable.
It proves the supplied authority merge is a real commit and an ancestor of the
expected runtime HEAD; proves the R13 authority document at reviewed PR #289
head is byte-identical at that merge commit; requires `git rev-parse HEAD` to
equal `expected_runtime_head`; and requires
`git status --porcelain=v1 --untracked-files=all` to be empty. This is complete
repository cleanliness, including staged, tracked, and untracked dirt.

The executor also requires its actual `sys.executable` to be exactly
`/opt/aios/runtime/venv/bin/python`, safely resolves that identity, and requires
the actual running version tuple to be exactly `3.12.3`. Package metadata does
not satisfy either runtime gate. Both private source files are accepted only
after no-follow open/fstat establishes link count exactly one, without weakening
any existing type, owner, group, mode, byte, or digest check.

The fail-closed order is activation existence and closed schema; merge ancestry
and reviewed-authority binding; exact runtime HEAD; complete clean tree; actual
interpreter and version; both source link counts and metadata; all preserved
package, path, freshness, one-shot, staging, publication, cleanup, and evidence
gates; then claim. Every new failure is `PRECONDITION_FAILED` before claim and
therefore consumes no retry state and creates no staging or publication object.

The future executor may obtain bytes only from these two fixed private,
execution-side source paths:

- `/run/aios/stage-0.33c-p4s5-source/approved-input.json`;
- `/run/aios/stage-0.33c-p4s5-source/approved-input-approval.json`.

This authority does not create, provision, or populate that source area. The
separately controlled exact-byte custodian must materialize the existing exact
P4S2-validated byte objects there outside Git before execution. The source
directory must be a real non-symlink directory owned `root:root`, mode `0700`;
each source must be a real regular non-symlink file owned `root:root`, mode
`0400`, opened read-only with no-follow semantics. Alternate paths, standard
input, environment values, caller bytes, prose reconstruction, JSON
reserialization, normalization, changed ordering, regenerated approval, and
substitution from raw business facts are prohibited.

For the input, bytes `[0:1327]` are the frozen semantic object, their SHA-256 is
the frozen input digest, byte `[1327]` is exactly `0x0A`, total length is exactly
1,328, and no later byte exists. For the approval, bytes `[0:3579]` are the
frozen semantic object, their SHA-256 is the frozen approval digest, byte
`[3579]` is exactly `0x0A`, total length is exactly 3,580, and no later byte
exists. Neither semantic digest is a transport-file SHA, and no transport SHA
is invented or frozen.

Both sources must also match the merged approval schema, manifest identity,
bound input identity, and harness identity without exposing their contents. If
either exact private byte object is absent, unsafe, unreadable, or fails any
binding, stop before consumption and classify `APPROVED_BYTES_UNAVAILABLE`.
Never reconstruct or replace it.

Project Owner-approved facts, item order, descriptions, quantities, units,
normalization, and provenance remain immutable. Evidence and logs may contain
only governed identifiers, hashes, byte counts, safe paths, metadata, UTC
timestamps, and classifications. Raw package bytes, approval JSON, supplier,
document number, item facts, OCR, retained images, addresses, phone numbers,
and signatures must not enter Git, terminal evidence, or logs.

## Fail-closed preflight and approval gate

All read-only preflight must complete before authority consumption. The future
executor must stop before publication unless it proves:

1. merged PR #277 and this authority's independently reviewed merge commit;
2. the governed parent
   `/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c` is a
   real non-symlink directory owned `root:aiosadmin`, mode `0750`;
3. every path component from `/opt` through that parent is safely resolved
   without following an unexpected symlink;
4. both final target basenames are absent under non-following lookup;
5. the two fixed private sources satisfy every frozen byte and identity binding;
6. the exact bounded approval schema and safe-string grammar remain valid;
7. immediately before the consume operation, an absolute UTC clock satisfies
   exclusively `now < not_after_utc`; equality, later time, invalid time, or an
   unreadable clock is expired and a STOP; and
8. the fixed consumption record is absent and no prior execution has consumed
   this authority.

There is no approval renewal, timestamp extension, regenerated or replacement
approval, target repair, overwrite, retry, or second attempt. Duplicate
freshness is not queried or revalidated. PostgreSQL contact remains prohibited.

## Durable one-shot consumption and concurrency

The sole consumption record is exactly:

`/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/runtime-sync-evidence/step4-install-authority-9d29c855-0f23-4539-a9b9-2e17dc89c49d.json`

This content-minimized evidence record is not a package target. Before use, the
existing `runtime-sync-evidence` directory must independently pass its governed
real-directory and no-symlink checks and be exactly `aiosadmin:aiosadmin`, mode
`0700`; this authority does not provision, repair, chmod, chown, or replace it.
An unsafe or unavailable evidence directory stops before consumption.

The exact transition is `UNUSED -> CLAIMED -> DURABLY_CONSUMED ->
EXECUTION_STARTED`. `UNUSED` means no marker exists and no execution history
indicates an unresolved claim attempt. `CLAIMED` means the exclusive marker
inode was created but durable persistence has not been proven.
`DURABLY_CONSUMED` means the exact marker was fully written, its file `fsync`
succeeded, its writable fd closed successfully, and the retained parent
directory `fsync` succeeded. `EXECUTION_STARTED` begins only with staging after
that complete barrier. Only `DURABLY_CONSUMED` authorizes staging.

After every preflight gate, including both-target absence and approval freshness,
passes, the executor claims with `O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW`, mode
`0600`, relative to the retained no-follow directory fd. There is no overwrite
or truncate-existing path. Successful `O_EXCL` creation establishes exclusive
`CLAIMED` ownership; successful complete write, file `fsync`, close, and
parent-directory `fsync` establishes the `DURABLY_CONSUMED` one-shot boundary.
Any barrier failure is a STOP with no staging.

The immutable write-once record contains only schema/state version, authority
identifier and containing merge commit, UTC claim timestamp, executor path and
SHA-256, and run-as identity. It contains no raw package or business data and
requires no later marker mutation. Its serialized `DURABLY_CONSUMED` state is
valid only after the external barrier completes; before then it is `CLAIMED`.

Exactly one concurrent process can claim. Every `EEXIST` loser reports
`AUTHORITY_CONSUMED` and stops immediately before staging. A loser must not read
partial claim contents to decide takeover. There is no lease, wait, poll,
timeout, stale-marker takeover, deletion, reset, repair, or retry.

A crash after `CLAIMED` but before the barrier is proven does **not** guarantee
that a persistent marker remains. It is `CONSUMPTION_DURABILITY_UNCERTAIN`;
automatic retry is prohibited even if the marker appears absent after restart.
Filesystem absence alone cannot re-prove `UNUSED`. If execution history,
operator evidence, or result evidence indicates a claim attempt without proven
durable completion, authority remains non-reusable until separate
incident/recovery review establishes disposition. External claim observability
never weakens the one-shot rule and creates no retry mechanism.

After the complete barrier, authority is irreversibly `DURABLY_CONSUMED`. A
crash or failure afterward never permits retry, even if staging never began,
staging failed, publication failed, or final verification failed. Separate
incident/recovery governance is required.

## Exact staging, verification, and publication contract

For each artifact in the frozen order, the winner must follow merged PR #277:

1. generate exactly one canonical lowercase UUIDv4 staging basename in the
   governed parent and create it exclusively on the same filesystem using
   `O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW`, initial mode `0600`;
2. reject collision, symlink, non-regular type, alternate path, or device drift;
3. write only the applicable fixed private source transport bytes completely,
   reject short writes or extra bytes, flush, and file-`fsync`;
4. set exactly `root:aiosadmin` and `0440`, and `fsync` metadata as required;
5. close every installer-controlled writable descriptor and prove no
   `O_WRONLY` or `O_RDWR` descriptor references the staged inode;
6. reopen only read-only with no-follow semantics if descriptor verification is
   needed; and
7. verify before publication that the object is regular, not a symlink, on the
   governed filesystem, exactly `root:aiosadmin` and `0440`, and satisfies its
   exact semantic-prefix SHA, terminal `0x0A`, transport length, and no-extra-byte
   contract.

Setting mode `0440` does not revoke write capability held by an already-open
`O_WRONLY` or `O_RDWR` descriptor. Publication is prohibited until writable
installer descriptors and uncontrolled writable aliases are proven absent.
Neither staging nor final paths may be reopened writable.

Only after read-only pre-publication verification may the executor use the
same-filesystem atomic hard-link no-replace model from the complete staged inode
to the fixed final basename. The destination must still be absent. `EEXIST` is a
STOP. Direct final writes, overwrite, truncate, rename-over, unlink-and-retry,
retry-overwrite, chmod/chown repair, or replacement are prohibited.

The exact per-object checks are:

| Final target | Owner/group | Mode | Semantic prefix | Transport | Terminal byte | Frozen semantic-prefix SHA-256 |
|---|---|---:|---:|---:|---|---|
| `approved-input.json` | `root:aiosadmin` | `0440` | `1327` | `1328` | byte `[1327] = 0x0A` | `e3c66fddf815c57f17baad49926c44588279d60cb4e78df867e0ae2189237a6d` |
| `approved-input-approval.json` | `root:aiosadmin` | `0440` | `3579` | `3580` | byte `[3579] = 0x0A` | `2ea9e735d7a5183a3e247abf57438d6e095fd7e9858d5ce688d221f7e9050f26` |

After each publication, `fsync` the parent, independently open the final target
read-only/no-follow, and reverify regular non-symlink type, device, owner/group,
mode, exact transport length, terminal byte, semantic-prefix length and SHA,
zero trailing bytes, equality to the fixed private source, and absence of every
installer-controlled writable descriptor or alias.

Only after successful final verification may the executor unlink that exact
staging pathname, `fsync` the parent, verify staging absence, and reverify the
final target. Staging unlink cannot mutate the hard-linked final inode. Cleanup
must never use wildcards or directory sweeps. If exact cleanup fails, preserve
the verified final and residual staging link, classify
`APPROVED_INPUT_STAGING_CLEANUP_INCOMPLETE`, block package use, and require the
separate incident/recovery governance required by merged PR #277; final content
must not be altered or mislabeled corrupt solely because unlink failed.

If exactly the first target publishes but the second publication or verification
fails, classify `STEP4_APPROVED_INPUT_PARTIAL_INSTALLATION`, preserve the first
final target, and STOP. Do not delete, overwrite, retry, continue as success,
invoke the harness, or begin Step 5. Separate incident/recovery governance is
required. After both targets pass, independently verify the exact pair again.

## Explicit crash-window disposition

- Before `CLAIM`: unused and safe to stop, absent earlier unresolved claim history.
- After `CLAIMED` before the barrier: `CONSUMPTION_DURABILITY_UNCERTAIN`; no automatic retry.
- After `DURABLY_CONSUMED` before staging: permanently consumed; no retry.
- During staging: permanently consumed; no retry.
- After first publication: merged partial-install rules apply; preserve the published object.
- After pair publication before final verification: permanently consumed; investigate, do not retry.
- After final verification before cleanup: pair remains verified; merged cleanup classification applies.

Approval expiry and both target-absence checks precede `CLAIM`. Staging is
structurally after successful marker `fsync`, writable-fd close, and retained
parent-directory `fsync`; merely `CLAIMED` execution cannot stage or publish.

## Minimized execution evidence and excluded effects

The authority-bound final evidence path is exactly the consumption-record path
with `.result.json` appended. It must record the authority identifier and merge binding, executor path and SHA-256, run-as identity,
claim outcome, durability outcome, final consumed status, execution timestamp UTC, parent
metadata, pre-target absence, approval-validity result, semantic hashes,
transport byte counts, staging checks, writable-descriptor closure/absence,
publication outcome per target, final metadata and semantic-prefix hashes,
cleanup status, consumption status, and final classification. This companion is
created exclusively/no-follow as mode `0600`, durably file- and parent-`fsync`ed,
never overwrites an existing object, and never contains raw package or business
content. Failure to create or complete final evidence after durable consumption remains
`DURABLY_CONSUMED / EVIDENCE_INCOMPLETE` and never permits retry.

The result object has this exact closed top-level key set (one key per line):

```text
approval_cleanup_complete
approval_final_inode_verified
approval_final_metadata
approval_freshness_valid
approval_published
approval_semantic_prefix_hash_verified
approval_semantic_sha256
approval_stage_device_verified
approval_staging_verified
approval_transport_bytes
approval_transport_bytes_verified
approval_verified
approval_writable_fd_absent
approval_writable_fd_closed
artifact_role
authority_commit
authority_id
claim_exclusive
classification
consumption_state
durability_barrier_complete
errno_code
executor_path
executor_sha256
input_cleanup_complete
input_final_inode_verified
input_final_metadata
input_published
input_semantic_prefix_hash_verified
input_semantic_sha256
input_stage_device_verified
input_staging_verified
input_transport_bytes
input_transport_bytes_verified
input_verified
input_writable_fd_absent
input_writable_fd_closed
pair_reverified
parent_metadata
pre_targets_absent
run_as
schema_version
stage
timestamp_utc
```

`parent_metadata` is either `null` before capture or an exact object with
`device`, `inode`, `uid`, `gid`, and `mode` integer keys. Each
`*_final_metadata` is either `null` before final verification or an exact
object with those five integer keys plus `size`. `errno_code` is an integer or
`null`; source hashes and transport byte counts are `null` until both private
sources have passed preflight. `pre_targets_absent` and
`approval_freshness_valid` are `null` until checked. All other status checks
are booleans: `false` means the gate was not reached or did not pass; `true`
means it passed. `artifact_role` is one fixed final basename or `NONE`.
`run_as` is `root`; `executor_path` is the frozen relative repository path.
No hostname is recorded because this authority does not govern a hostname.
The result records actual source hashes and byte counts and observed filesystem
metadata; it does not include source bytes, package values, or raw exceptions.
Both success and governed failure use this same schema.

This filesystem-only authority permits no service restart, Telegram reload,
service-environment change, `runtime.env` change, harness import-for-execution,
harness invocation, controlled callable invocation, database connection,
candidate creation, authorization creation, inventory effect, or stock effect.
The bounded outcome remains:

- production PostgreSQL contacted: `NO`;
- production PostgreSQL writes: `0`;
- harness invoked: `NO`;
- controlled callable invoked: `NO`;
- candidate created: `NO`;
- `material_receipts` inserts: `0`;
- `material_receipt_items` inserts: `0`;
- `inventory_movements`: `0`;
- `material_stock` mutations: `0`;
- `authorization.json` created: `NO`;
- Step 5: `NOT AUTHORIZED`.

The required lifecycle is this authority PR, independent review, human merge,
exactly one governed attempt, post-install verification, and independent Step-4
closure review. This authority does not execute installation and does not close
Step 4. Its pre-execution classification is
`P4S6_BLOCKERS_REMEDIATED_READY_FOR_REREVIEW`.
