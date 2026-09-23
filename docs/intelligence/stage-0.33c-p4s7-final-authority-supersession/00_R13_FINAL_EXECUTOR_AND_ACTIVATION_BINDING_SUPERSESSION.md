# Stage 0.33C-P4S7-R15 Final Authority Binding Supersession

Classification: `P4S7_FINAL_AUTHORITY_BINDING_SUPERSESSION_READY_FOR_REVIEW`

## Governance-only decision and frozen authority

This separate addendum is the authoritative supersession mechanism, effective
only after independent review and human merge. It creates governance only and
does not itself authorize activation creation or an installation attempt.

[PR #289](https://github.com/bader5657/AIOS/pull/289) must remain frozen at
reviewed head `209618b845c844ad08915853fa1dfa07c1c9897a`, including its authority
document at
`docs/intelligence/stage-0.33c-p4s7-runtime-install-execution-authority/00_FINAL_ONE_SHOT_RUNTIME_INSTALL_AUTHORITY.md`.
No commit, amendment, rebase, branch sync, or wording edit may be added to that
PR. Its authority document must remain byte-identical through human merge.

PR #289 must NOT be modified to carry these updated bindings because doing so
would change the `reviewed_head_sha` that the activation contract is designed
to bind. This separate addendum resolves that circular head dependency.

## Narrow supersession and precedence

Only PR #289's stale executor SHA, policy-bound executor SHA, enforcement
responsibility, and post-merge activation requirements are superseded. All
other PR #289 semantics remain intact. In particular:

- The historical pre-R13A digest
  `c1aa32502dff875eaf889c0644655b8c5f4a2fa0361f5a0622b976580e9bc61b`
  remains preserved only as history. It is not active execution authority.
- The active executor and policy-bound SHA-256 are both
  `1042693ec4af0f95068426e67954ea9ba4477012b1e18a88bd125469d100df87`.
  Executor self-hash, merged policy binding, and activation binding must agree
  immediately before claim.
- Enforcement responsibility rests with merged
  [PR #290](https://github.com/bader5657/AIOS/pull/290), merge commit
  `327732e611b6d6bb3b88c33775e320d2d5173862`. Its executor enforces activation,
  merge/document proof, exact runtime HEAD and complete cleanliness, actual
  interpreter/version, private-source single-link checks, and preserved gates.
- PR #289's R12 runtime HEAD
  `b92991c4d88f899e6a4a861c439d898332c62508` remains a historical baseline.
  Its use as a future exact-HEAD gate, including immediate pre-claim item 3,
  is superseded solely by the post-merge activation-bound HEAD rule below.
  Cleanliness, interpreter, version, and root identity requirements remain.
- PR #289's statement that human merge activates the attempt and its sequence
  proceeding directly from merge to installation are superseded by the
  composed authority and post-merge activation sequence below.

The R13A amendment's narrative instruction to "amend PR #289 for the final
executor and activation contract" is replaced by this separate addendum and
the sequence below. This reconciles that procedural instruction without
changing PR #290's code, policy, activation schema, or enforcement behavior.
No other authority is broadened or fail-closed control weakened.

## Final executor and policy

The unchanged sole executor is:

`/opt/aios-src/docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/one_shot_install.py`

The unchanged policy reference is:

`docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/00_ONE_SHOT_RUNTIME_INSTALLATION_AUTHORITY.md`

Both bind SHA-256
`1042693ec4af0f95068426e67954ea9ba4477012b1e18a88bd125469d100df87`.
The observed runtime HEAD for this governance verification is
`327732e611b6d6bb3b88c33775e320d2d5173862`; it is not the future execution HEAD.

## Incorporated post-merge activation contract

The sole activation path is:

`/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/p4s7-r13-post-merge-activation.json`

The later record must use PR #290's exact closed metadata-only schema:

| Member | Required binding |
|---|---|
| `schema_version` | `aios-stage-0.33c-p4s7-r13-post-merge-activation-v1` |
| `authority_id` | `9d29c855-0f23-4539-a9b9-2e17dc89c49d` |
| `pr_number` | integer `289` |
| `reviewed_head_sha` | `209618b845c844ad08915853fa1dfa07c1c9897a` |
| `authority_merge_sha` | Unknown until PR #289 human merge; then the canonical real authority merge commit |
| `expected_runtime_head` | Exact post-merge runtime commit containing merged PR #290, this merged addendum, and merged PR #289 |
| `executor_sha256` | `1042693ec4af0f95068426e67954ea9ba4477012b1e18a88bd125469d100df87` |
| `policy_reference` | `docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/00_ONE_SHOT_RUNTIME_INSTALLATION_AUTHORITY.md` |
| `activated_at_utc` | Canonical UTC timestamp with six fractional digits and `Z` |

Unknown or missing members are rejected. Future commit values must not be
invented, precomputed, or populated with the current pre-merge runtime HEAD.
The record contains no package bytes or business facts. It must be a regular,
non-symlink, single-link `root:root` file with mode `0400`, created by exclusive
publication without overwrite under a separately governed future action.
This addendum does not create that record or authorize its creation now.

PR #290 requires both commit fields to resolve locally, the authority merge to
be an ancestor of the expected runtime HEAD, and the frozen reviewed PR #289
document to be byte-identical in that merge. Actual `/opt/aios-src` HEAD must
equal the activation's expected HEAD, with completely clean tracked, staged,
and untracked state. Executor bytes must match the HEAD blob and policy digest.
Missing activation or any failed activation/enforcement gate stops before claim.

The later governed activation action and final independent verification must
also establish that the exact expected runtime HEAD contains all three merged
components, including this addendum. This is a governance obligation; this
document does not claim that PR #290 independently detects this new addendum.

## Composed authority and fresh review condition

Final Step-4 runtime-install authority is the composition of all four:

A. The frozen PR #289 reviewed authority document, subsequently human-merged.
B. Merged PR #290 executor enforcement and policy.
C. This independently reviewed, human-merged binding supersession addendum.
D. The later separately governed, valid post-merge activation record.

No single component alone authorizes execution. All preserved immediate
pre-claim gates must still pass; composition does not waive them.

PR #289 may receive fresh independent review only after this addendum is
merged. The fresh reviewer must evaluate frozen PR #289 together with merged
PR #290 and this merged addendum, and explicitly confirm that the stale
executor binding is superseded. PR #289 must then be human-merged WITHOUT
modifying its reviewed head. No automatic merge is authorized.

## Preserved package and runtime-install constraints

All already verified PR #289 bindings are incorporated unchanged: exact private
source paths, input and approval semantic/transport hashes and byte counts,
terminal LF rules, TF-A DTO projection and digest, `package_payload_sha256`,
Model B package-local state, approval identity and freshness, final-target
absence, staging-debris STOP rules, path safety, one-shot durability, and
success/failure semantics. No package changes or approval renewal are made.

In particular, the approval remains bounded by
`not_after_utc == 2026-09-26T21:24:52.273127Z`, with absolute UTC
`now < not_after_utc` required at every execution gate. Review or merge does
not extend that window. No retry, reset, cleanup takeover, overwrite, or
reuse after ambiguous or durable consumption is authorized.

The exact interpreter `/opt/aios/runtime/venv/bin/python`, Python `3.12.3`,
root identity, sole no-argument executor invocation, and all other preserved
controls remain binding. Historical verification is not current pre-attempt
verification; this governance task does not reread private package content.

## Mandatory future sequence and execution boundary

```text
supersession governance
-> independent review
-> human merge supersession
-> fresh independent review PR #289 as composite authority
-> human merge PR #289 WITHOUT modifying its head
-> synchronize /opt/aios-src to new main
-> create governed activation record under a separate governed action
-> final pre-attempt verification
-> exactly one runtime-install attempt
```

No step may be collapsed. The unchanged post-attempt independent verification
and Step-4 closure requirements still apply; Step 5 requires later separate
consideration and is not authorized here.

This PR does NOT authorize or perform activation creation, installer execution,
installation claim creation, runtime target creation, PostgreSQL contact,
harness invocation, candidate creation, `authorization.json` creation, service
restart/reload, or Step 5. It does not modify PR #289, executor code, package
bytes, or runtime state. The next official action is independent review of
this separate governance PR. Do not merge automatically.
