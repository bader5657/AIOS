# Post-Provision Verification and Sync Authority Activation

## Bounded verification

After human provisioning, the runtime identity must perform non-sudo, exact-path
verification. Confirm the root and every governed component with `lstat`/`stat`:
real directory, non-symlink, expected owner/group, and exact mode. Then create
one probe named `probe-<canonical-lowercase-UUIDv4>` under the evidence root,
exclusively as mode `0600`, with bounded secret-free content; flush and `fsync`
the probe and parent directory, verify it, and remove only that exact probe.
Verify the probe is absent afterward. Any collision, unsafe type, metadata drift,
write failure, or cleanup mismatch is STOP; never overwrite or repair.

The probe is not execution evidence, does not consume PR #267 sync authority,
and does not contact PostgreSQL. The actual session directory and files are
created only by the separately authorized synchronization execution.

## Evidence durability and manifest

Before runtime mutation, the future executor must durably write and fsync
prestate/authority evidence. After each critical stage it must durably record
mutation result, import result, service health, and rollback state. File flush,
file fsync, and session/parent-directory fsync are required where applicable.

`execution.jsonl` must contain bounded authority/session identity, PR #266
number/merge commit, PR #267 number/reviewed HEAD/merge commit, and PR #268
number/reviewed HEAD/merge commit, plus pre-sync and target SHAs, remote,
prestate, consumption timestamp, exact mutation/result, imports and callable
assertion, DB contact `NO`, service before/after identity, restart `NO`, worktree
state, rollback `YES/NO`, secret exposure `NONE`, and Step 2 `NOT AUTHORIZED`.
Before PR #268 merges, only its exact reviewed HEAD
`7100e4ee4d65cae0d71362032659a981578b7fa6` may be recorded; after merge, its
exact merge commit must be captured and verified. No placeholder or guessed
merge SHA is allowed. `manifest.json` must bind the complete three-PR identity
chain and those files by SHA-256, byte length, record counts, result/rollback
state, secret scan, Step 1 handoff, and Step 2 authorization state. Its own
final SHA is computed only after bytes are immutable and is not self-written into
the manifest.

No runtime.env contents, password, database URL, token, private key, arbitrary
stdout/stderr, source file, or raw Git object may enter evidence. Errors must be
sanitized.

## Authority activation and handoff

Provisioning plus verification PASS changes PR #267's state to
`ACTIVE / UNCONSUMED`; provisioning itself never consumes synchronization
authority. If provisioning is absent or verification fails, the authority
remains `MERGED / CONDITIONAL`, unconsumed, and unavailable for runtime mutation.

PR #267 runtime-sync execution evidence must include the merged PR #268 identity
because PR #268 governs the filesystem in which that evidence is stored. Missing
PR #268 number, reviewed HEAD, or verified merge commit is an activation block.

After activation, the separate sync execution authority still requires all
prestate gates, consumes once immediately before checkout mutation, and permits
only the frozen exact target/rollback behavior. A successful sync remains merely
eligible for independent Step 1 closure review. Step 2 remains NOT AUTHORIZED.

## Safety boundary

Production PostgreSQL contact: `NO`. Runtime checkout mutation: `NO`. Service
restart: `NO`. Authorization artifact: not created. Consumed directory: not
created. Harness, candidate, first-write authority, and candidate traffic: none.
