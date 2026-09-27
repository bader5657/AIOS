# AIOS P4S7-R34 Recovery Activation Governance

Classification: `P4S7_RECOVERY_ACTIVATION_GOVERNANCE_READY_FOR_REVIEW`

## Scope, evidence, and baseline

GOVERNANCE ONLY. Independent review and human merge are required. No automatic
merge. This document freezes a prospective recovery activation contract; it
does not authorize or perform activation creation, installation, or Step 5.

R33 is PASS on the supplied operator evidence, including the privileged
supplement `R33_PRIVILEGED_RECOVERY_VERIFICATION_PASS`. That supplement closes
only the privileged R33 verification gap, with prior nonprivileged checks
unchanged. R34 does not repeat privileged checks or treat historical evidence
as fresh pre-creation verification.

| Authoritative R33 binding | Exact value |
|---|---|
| Runtime HEAD | `ba717f6990d775748f46d62ef03a696f1618077b` |
| Executor SHA-256 | `da020dff0974acf0bb7fc22bc1b54f17d149ee8f11ace67420eb16cca73cd6be` |
| Policy-bound executor SHA-256 | `da020dff0974acf0bb7fc22bc1b54f17d149ee8f11ace67420eb16cca73cd6be` |
| Recovery authority | `7bc638e2-e1f4-4e87-a54a-4d0df031b130` |
| Fresh approval ID | `3a478d87-5c4f-4778-9f88-2228f4d7167f` |
| Approved at UTC | `2026-09-26T23:24:12.093093Z` |
| Not after UTC | `2026-10-03T23:24:12.093093Z` |
| Package payload SHA-256 | `be7a1750eb77ae77e8f020fc3f29c5f047cf88d1720a387f50f58f58c877962e` |

Repository inspection at this baseline confirms the executor digest equals
the policy-bound digest. GitHub records [PR #299](https://github.com/bader5657/AIOS/pull/299)
as merged at that exact baseline. These are repository checks, not a new live
runtime attestation. The governing recovery and private-source contracts remain
[R30](../stage-0.33c-p4s7-approval-expiry-recovery/00_APPROVAL_EXPIRY_RECOVERY_AMENDMENT.md),
[R31A](../stage-0.33c-p4s7-recovery-private-source/00_RECOVERY_PRIVATE_SOURCE_FILESYSTEM_GOVERNANCE.md),
and [R32](../stage-0.33c-p4s7-r32-recovery-bindings/00_RECOVERY_EXECUTOR_PACKAGE_BINDING_AMENDMENT.md).

## Immutable historical activation and one recovery path

Preserve byte-for-byte and with unchanged metadata the historical activation:

`/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/p4s7-r13-post-merge-activation.json`

Do not overwrite, reuse, delete, relocate, or reinterpret it. Historical
authority, sources, activation, and evidence remain immutable history.

Freeze exactly one distinct recovery activation path:

`/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/p4s7-recovery-activation.json`

No alternate path, CLI override, environment override, discovery, or historical
fallback is permitted. Any existing directory entry at the recovery activation
path, including a symlink or an apparently correct file, is STOP. This document
does not create that path.

## Closed recovery activation schema

The top-level value must be a JSON object with exactly the following eight
keys. Every value must be a string; missing keys, extra keys, duplicate keys,
nulls, booleans, numbers, arrays, and nested objects are rejected. All fixed
strings require exact equality, without trimming, normalization, or coercion.

| Required key | Exact value or rule |
|---|---|
| `schema_version` | `aios-stage-0.33c-p4s7-recovery-activation-v1` |
| `authority_id` | `7bc638e2-e1f4-4e87-a54a-4d0df031b130` |
| `expected_runtime_head` | `ba717f6990d775748f46d62ef03a696f1618077b` |
| `executor_sha256` | `da020dff0974acf0bb7fc22bc1b54f17d149ee8f11ace67420eb16cca73cd6be` |
| `policy_reference` | `docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/00_ONE_SHOT_RUNTIME_INSTALLATION_AUTHORITY.md` |
| `approval_id` | `3a478d87-5c4f-4778-9f88-2228f4d7167f` |
| `package_payload_sha256` | `be7a1750eb77ae77e8f020fc3f29c5f047cf88d1720a387f50f58f58c877962e` |
| `activated_at_utc` | Actual activation creation time under the timestamp contract below |

The policy reference is the fixed repository-relative policy path in the
verified runtime checkout, not a caller-selected file. Its active recovery
authority and executor digest must match the record and actual executor bytes.
The approval ID and payload digest must independently equal the freshly
validated recovery approval and recomputed canonical payload digest.

This replaces obsolete R13 activation semantics prospectively. The old
`pr_number`, `reviewed_head_sha`, and `authority_merge_sha` fields are excluded,
not renamed or copied. PR #289 and its reviewed head cannot prove recovery
review or merge. PR #299 lineage and subsequent recovery governance/amendment
review and merge evidence are mandatory external verification gates. The
future reader amendment must define and enforce their exact recovery trust
bindings; it must not drop reviewed-authority/merge verification merely
because these three historical fields are absent from the new record.

TF-A and Model B remain required pre-creation and executor gates; they are not
duplicated into this minimal activation schema. No historical schema version
or authority ID is accepted for recovery.

## Canonical byte and timestamp contract

Use UTF-8 JSON serialization with `ensure_ascii=False`, `sort_keys=True`,
`separators=(",", ":")`, and `allow_nan=False`.

- Semantic bytes are canonical JSON without LF.
- Transport bytes are semantic bytes plus exactly one ASCII LF (`0x0a`).
- Reject BOM, CRLF, leading/trailing whitespace in semantic bytes, additional
  LF, duplicate keys, noncanonical key ordering, or any byte difference from
  canonical reserialization. Parse with duplicate-key rejection before testing
  the exact closed schema. Do not silently normalize malformed input.
- Record and independently verify semantic and transport counts and SHA-256
  digests after creation; those derived values are not extra schema fields.

`activated_at_utc` must be actual creation-time UTC, never copied from approval,
review, merge, or historical activation. Its full-string format is
`YYYY-MM-DDTHH:MM:SS.ffffffZ`, with ASCII digits only and exactly six fractional
digits. Require a full match of
`[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z`
and a valid UTC calendar/time parse. Reject offsets, lowercase z, invalid dates,
leap-second encodings, and backdating. No timestamp is generated by R34.

## Fresh pre-creation gates

Immediately before separately authorized creation, reverify every gate below.
Any failure, unavailable evidence, uncertain clock, or identity drift means
STOP BEFORE CREATION; no automatic repair or renewal is authorized.

1. Actual runtime HEAD equals the exact frozen binding; the complete runtime
   tree is clean, including staged, tracked, and untracked files. Actual
   executor bytes match the HEAD blob and their SHA equals the activation and
   policy-bound SHA. Review/merge/runtime-sync prerequisites below are complete.
2. Prove merged PR #299 lineage at
   `ba717f6990d775748f46d62ef03a696f1618077b`, plus exact reviewed and merged
   recovery governance/reader evidence. A moving branch or an unmerged head
   cannot substitute for this evidence.
3. Recovery authority is UNUSED. Both recovery claim/marker and result are
   absent under the existing `runtime-sync-evidence` directory:
   `step4-install-authority-7bc638e2-e1f4-4e87-a54a-4d0df031b130.json` and
   `step4-install-authority-7bc638e2-e1f4-4e87-a54a-4d0df031b130.json.result.json`.
   Historical state does not authorize or consume recovery.
4. Verify the unchanged historical input at
   `/run/aios/stage-0.33c-p4s5-source/approved-input.json` and fresh approval at
   `/run/aios/stage-0.33c-p4s5-recovery-source/approved-input-approval.json`,
   using all R31A/R32 source, metadata, schema, hash, count, and LF gates.
   Input semantic/transport counts remain 1327/1328 and semantic SHA is
   `e3c66fddf815c57f17baad49926c44588279d60cb4e78df867e0ae2189237a6d`.
   Fresh approval semantic/transport counts are 3579/3580, semantic SHA is
   `6ea5fc118e375ac035f321110198eb43811fb5b991a095554c15d0a6cbeb16c9`,
   and transport SHA is
   `1579e7fffd93bd0dc35d31539c9703b21482c486eee14aaed5535ab3a87dc367`.
   Require the exact approval ID and both timestamps in the baseline table.
5. Require computed payload SHA == approval outer payload SHA == activation
   payload SHA == the frozen fresh package payload SHA above.
6. Require TF-A == unchanged DTO projection digest ==
   `c006afcad84984baea6af164067fdd4cfc31cdcac5f86baf7b1ceefd6e4c5065`.
   Model B remains unchanged: both registry IDs are JSON null and
   `registration_succeeded` is boolean false. No PostgreSQL check is permitted.
7. Require `2026-09-26T23:24:12.093093Z <= now < 2026-10-03T23:24:12.093093Z`.
   Equality at expiry or expiry is STOP. No renewal under this authority.
   Recheck freshness at publication and later execution gates; activation
   does not reserve or extend the approval window.
8. Verify recovery directory identity and custody under R31A: real no-follow
   directory, root:root, mode 0700, retained ancestor/child descriptor identities
   stable against current evidence. Earlier device/inode observations are not
   permanent constants or a substitute for fresh verification.
9. Recovery activation is absent; historical activation bytes, hash, metadata,
   and identity match retained historical evidence without modification. Verify
   trusted activation-parent traversal and identity before exclusive creation.
10. Both final package targets `approved-input.json` and
    `approved-input-approval.json` under the fixed runtime parent are absent;
    staging debris and recovery claim/result are absent. Preserve the existing
    prohibition on candidate and `authorization.json` creation.

## File custody and exclusive publication contract

The future recovery activation must be a regular non-symlink file, root:root
(UID/GID 0), exact mode `0400`, with `st_nlink == 1`.

After all gates pass and separate creation authorization is obtained:

1. Traverse from a trusted root using retained no-follow directory descriptors;
   verify ancestors and activation-parent custody and device/inode stability.
   Do not follow symlinks or repair conflicting directories.
2. Exclusively open the fixed recovery basename relative to the retained
   parent with `O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW`, restrictive initial mode
   `0600`. Any existing entry or race collision is STOP, never overwrite.
3. Verify regular type and single link; record device/inode. Write the complete
   canonical transport bytes, handling short writes. Set root:root and exact
   mode `0400` through the descriptor, and verify metadata.
4. Fsync the file, close every writable file descriptor, then fsync the retained
   parent directory. Any error is STOP; do not claim durability on failure.
5. Reopen read-only/no-follow relative to that parent. Verify the same inode
   and device, exact schema, bytes, counts, digests, bindings, timestamp,
   metadata, and parent/ancestor identities. No writable alias is permitted.

A failed or partial publication is STOP. Preserve evidence for separately
governed disposition; no automatic overwrite, delete, retry, or permission
repair. Successful publication verification does not replace the later
independent activation verification or authorize installation.

## Executor impact and activation blockers

**Executor activation-reader amendment required: YES.** At the R33 baseline,
`one_shot_install.py` sets `ACTIVATION_RECORD = None`; the default reader stops
with `PRECONDITION_FAILED / RECOVERY_ACTIVATION_NOT_GOVERNED` before opening
activation or private sources. The retained parser uses the historical R13
schema, nine-key set, PR #289, and historical reviewed-head/merge semantics.
Setting a path alone would not implement this recovery contract.

Activation creation remains blocked until a separate reader amendment is
implemented, independently reviewed, human-merged, and runtime synchronized.
It must enforce the fixed recovery path, closed recovery schema, approval and
payload bindings, recovery review/merge trust, and all unchanged safety gates.
The executor must remain fail-closed on the historical activation, including
the historical path, schema, authority, and any fallback. Only the governed
recovery activation may satisfy its activation gate; even that record never
substitutes for separate execution authority.

**Binding transition blocker:** a reader code amendment necessarily changes
the executor digest; merging and synchronizing also changes runtime HEAD.
R34 freezes the exact supplied R33 HEAD and SHA, not future unknown values.
Do not call those old values the amended runtime/executor identity, weaken
exact equality to ancestry, or silently accept a new digest. Before creation,
explicit independently reviewed, human-merged binding-supersession governance
must freeze the actual amended executor/policy SHA and exact post-merge runtime
HEAD and establish the recovery review/merge evidence. This is a prerequisite
within the amendment/review/merge/runtime-sync stages below; if additional
governance review is needed, preserve its separate review and human merge.
Until that prerequisite is satisfied, exact R34 checks continue to STOP on
changed identities. No superseding values are invented or authorized here.

These are disclosed future activation blockers, not permission to implement
the amendment in R34. The document is ready for governance review, not ready
for activation creation or an install attempt.

## Required sequence; no collapse

R34 activation governance
→ independent review
→ human merge
→ executor activation-reader amendment if required (required here)
→ independent review
→ human merge
→ runtime sync
→ fresh pre-creation verification
→ recovery activation creation
→ independent activation verification
→ final pre-attempt verification
→ separate execution authority
→ exactly one install attempt
→ post-execution verification
→ Step-4 closure
→ only then Step-5 consideration.

Creation requires its own explicit authorization. Every later phase remains
pending; neither a governance merge nor UNUSED state grants execution rights.
No step may be collapsed, skipped, inferred from a previous PASS, or performed
under this governance-only task. Approval expiry at any applicable gate is STOP.

## R34 execution boundary and disposition

| Action/state | R34 result |
|---|---|
| Recovery authority state | UNUSED; governance does not consume it |
| Recovery activation created | NO |
| Historical activation modified or reused | NO |
| Executor or policy modified | NO |
| Runtime modified or services restarted | NO |
| Private sources modified | NO |
| Installer authorized or executed | NO |
| Claim, result, staging, or runtime targets created | NO |
| PostgreSQL contacted | NO |
| Harness invoked | NO |
| Candidate or authorization.json created | NO |
| Step 5 authorized | NO |

Only this governance document is added. No live private-source or privileged
runtime verification is asserted by R34. Supplied R33 authority/absence evidence
remains the baseline; future gates must establish fresh truth.

Governance classification: `P4S7_RECOVERY_ACTIVATION_GOVERNANCE_READY_FOR_REVIEW`.
Next official action: independent review of the R34 governance-only PR, then
human merge if accepted. Activation remains blocked as stated above. STOP.
