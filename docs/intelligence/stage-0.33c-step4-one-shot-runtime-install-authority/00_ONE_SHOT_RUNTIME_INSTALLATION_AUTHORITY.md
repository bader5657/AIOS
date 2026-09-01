# Stage 0.33C-P4S5 One-Shot Runtime Package Installation Authority

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
| approval semantic bytes | `3549` |
| approval transport bytes | `3550` |
| approval semantic-prefix SHA-256 | `266c39426fae0b04dacf009436334dd34d6791368dcad5066a9b2a37b9bd8a57` |
| harness SHA-256, binding context only | `b9fc9fb22724184696eabf02525bcc0a626bdff5ce3943ed31ba2e21130f5cad` |

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
1,328, and no later byte exists. For the approval, bytes `[0:3549]` are the
frozen semantic object, their SHA-256 is the frozen approval digest, byte
`[3549]` is exactly `0x0A`, total length is exactly 3,550, and no later byte
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

After every preflight gate passes and immediately before creating the first
staging object, the executor must atomically claim the authority by creating the
fixed record relative to a retained no-follow directory descriptor with
semantics equivalent to `O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW`, initial and
final mode `0600`, and no exists-then-create race. Successful exclusive creation
is the irreversible consume point. It occurs before any package construction or
publication.

Exactly one concurrent caller can win `O_EXCL`. Every losing caller must perform
only bounded non-following metadata validation, report `AUTHORITY_CONSUMED`, and
stop before staging or publication. It must not read raw evidence, wait, poll,
take over, unlink, repair, retry, invoke the harness, or contact PostgreSQL. An
unsafe existing object is `AUTHORITY_CONSUMPTION_STATE_INVALID` and also stops.

The winner writes only: schema version, authority identifier, PR #277 merge
commit, this authority's merge commit, consumption timestamp UTC, hostname,
installer identity, state `CONSUMED`, and safe preflight outcomes. It then
flushes, file-`fsync`s, closes the record, and `fsync`s the evidence parent
before staging. Creation itself remains consumption if writing, close, either
`fsync`, later installation, cleanup, evidence completion, or process execution
fails. A zero-byte, partial, or not-yet-durable safely typed record is still
operator-visible `CONSUMED / EVIDENCE_INCOMPLETE`, never reusable. A crash at or
after successful `O_EXCL` prohibits silent retry and requires separate
incident/recovery governance.

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
| `approved-input-approval.json` | `root:aiosadmin` | `0440` | `3549` | `3550` | byte `[3549] = 0x0A` | `266c39426fae0b04dacf009436334dd34d6791368dcad5066a9b2a37b9bd8a57` |

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

## Minimized execution evidence and excluded effects

The authority-bound final evidence path is exactly the consumption-record path
with `.result.json` appended. It must record the authority identifier, authority
merge binding, execution timestamp UTC, hostname, installer identity, parent
metadata, pre-target absence, approval-validity result, semantic hashes,
transport byte counts, staging checks, writable-descriptor closure/absence,
publication outcome per target, final metadata and semantic-prefix hashes,
cleanup status, consumption status, and final classification. This companion is
created exclusively/no-follow as mode `0600`, durably file- and parent-`fsync`ed,
never overwrites an existing object, and never contains raw package or business
content. Failure to create or complete final evidence after consumption remains
`CONSUMED / EVIDENCE_INCOMPLETE` and never permits retry.

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
`STEP4_ONE_SHOT_RUNTIME_INSTALL_AUTHORITY_READY_FOR_REVIEW`.
