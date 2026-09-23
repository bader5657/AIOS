# Stage 0.33C-P4S7-R13A Final Pre-Claim Executor Enforcement Amendment

Classification: `P4S7_R13_PRECLAIM_ENFORCEMENT_AMENDMENT_READY_FOR_REVIEW`

## Scope and boundary

This narrow amendment implements only the four independent-review blockers for
PR #289: exact runtime Git truth, private-source link count, actual interpreter
truth, and post-merge activation. It does not modify or merge PR #289 and does
not activate or execute the installer. It creates no activation record,
consumption marker, approved-input target, package bytes, candidate, or
`authorization.json`; contacts no PostgreSQL service; invokes no harness;
restarts no service; and authorizes neither Step 5 nor an installation attempt.

## Frozen activation contract

The sole activation path is:

`/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/p4s7-r13-post-merge-activation.json`

No environment or command-line path is accepted. The future record is governed
as a regular, non-symlink, single-link `root:root` file with mode `0400`,
created by exclusive publication with no overwrite under a separate governed
action. This amendment implements validation only and does not create it.

Its closed metadata-only schema is exactly:

| Member | Required binding |
|---|---|
| `schema_version` | `aios-stage-0.33c-p4s7-r13-post-merge-activation-v1` |
| `authority_id` | `9d29c855-0f23-4539-a9b9-2e17dc89c49d` |
| `pr_number` | integer `289` |
| `reviewed_head_sha` | `209618b845c844ad08915853fa1dfa07c1c9897a` |
| `authority_merge_sha` | canonical real commit supplied only after human merge |
| `expected_runtime_head` | canonical exact runtime commit containing all reviewed code |
| `executor_sha256` | final R13A executor digest, identical to policy binding |
| `policy_reference` | `docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/00_ONE_SHOT_RUNTIME_INSTALLATION_AUTHORITY.md` |
| `activated_at_utc` | canonical UTC timestamp with six fractional digits and `Z` |

Unknown or missing members are rejected. No package or business fact is present.

The final executor SHA-256 bound by the merged policy and required in the
activation record is
`1042693ec4af0f95068426e67954ea9ba4477012b1e18a88bd125469d100df87`.

## Pre-claim repository and authority proof

Using only local repository truth at fixed `/opt/aios-src`, the executor requires
`authority_merge_sha` and `expected_runtime_head` to resolve as commits, the
former to be an ancestor of the latter, and the reviewed PR #289 authority
document at `209618b845c844ad08915853fa1dfa07c1c9897a` to be byte-identical in
the authority merge. It then requires `git rev-parse HEAD` to equal the
activation's expected runtime HEAD and requires complete empty output from
`git status --porcelain=v1 --untracked-files=all`. Git absence, repository
failure, unreadable HEAD/status, tracked changes, staged changes, and untracked
files all stop as `PRECONDITION_FAILED` before claim.

The current pre-PR #289 runtime HEAD is not hard-coded as execution authority.
The future human-merge commit and exact final runtime HEAD cannot be invented or
precomputed and must be supplied only by the post-merge activation action.

## Interpreter and private-source proof

The executor requires actual `sys.executable` identity
`/opt/aios/runtime/venv/bin/python`, safe deterministic resolution of that path,
and actual Python version tuple exactly `3.12.3`. Approval JSON or package
metadata cannot satisfy these checks.

After no-follow open and fstat, each exact private source must additionally have
`st_nlink == 1`. Existing regular-file, `root:root`, `0400`, fixed byte-count,
terminal-LF, semantic hash, transport, schema, TF-A, package payload, Model B,
freshness, and path controls remain unchanged.

## Ordering and failure contract

The enforced order is activation existence/schema, local merge/document
binding, exact runtime HEAD, complete tree cleanliness, actual interpreter and
version, private-source link count/metadata, all preserved package/path/freshness
and one-shot gates, then claim. Every newly introduced failure occurs with claim
count zero, staging count zero, publication count zero, and no consumed retry
state.

## Mandatory sequence

```text
R13A implementation PR
-> independent review
-> human merge
-> synchronize runtime source
-> amend PR #289 for the final executor and activation contract
-> fresh independent review
-> human merge PR #289
-> separately govern and create the post-merge activation record
-> final pre-attempt verification
-> exactly one runtime installation attempt
```

`P4S7-R13A PRE-CLAIM ENFORCEMENT PASS — READY FOR INDEPENDENT REVIEW`
