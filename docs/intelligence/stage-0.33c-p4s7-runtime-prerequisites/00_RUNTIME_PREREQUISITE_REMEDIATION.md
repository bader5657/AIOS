# Stage 0.33C P4S7-R7 Runtime Prerequisite Remediation Governance

Classification: `P4S7_RUNTIME_PREREQUISITE_REMEDIATION_READY_FOR_REVIEW`

## Scope and non-authority

This artifact governs remediation of the runtime prerequisites found by P4S7.
It creates no execution authority. In this change no runtime checkout is
synchronized, no runtime owner or mode is changed, no private package byte is
materialized, and the installer is not modified or executed. There is no
service restart, PostgreSQL contact, harness invocation, candidate creation,
`authorization.json` creation, or Step 5 authorization.

The mandatory separation is:

1. merge this R7 governance only after independent review;
2. make, independently review, and human-merge a separate executable-binding
   reconciliation;
3. create separate runtime-checkout synchronization authority, then execute it;
4. create separate evidence-directory mode-remediation authority, then execute
   it;
5. create separate private-source materialization authority, then execute it;
6. repeat P4S7 verification.

No later step may be collapsed into, inferred from, or executed under this
artifact.

## Authoritative merged baseline

PR #285 is merged at
`50c2c7d210cf94cae99e43a75ea24dc5df2199db`. That merge has PR #284 merge
`4889a1e` and PR #285 amendment head `eaa261b` as ancestors. The merged TF-A
installer at
`docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/one_shot_install.py`
independently hashes to
`b82591be0d8f4f9876a8925e4428c3c0dc85589431733dfca178f86b3e415412`.
The retained manifest remains
`9801b5e4-453d-429a-b51f-e8ffaa17a2c9`.

## Runtime checkout synchronization contract

The exact target is `/opt/aios-src`. Read-only R7 inspection found a real
non-symlink `aiosadmin:aiosadmin` directory, mode `0755`, detached at
`964193f2e567b5109de50c427bbbf632b2198958` (PR #265), with an empty porcelain
status. It is stale and was not synchronized by R7.

A later, separate authority must require all of the following before and after
the synchronization:

- record the pre-sync SHA and prove the complete working tree is clean;
- discard no local change and stop on any dirty, unmerged, unexpected, or
  untracked state requiring disposition;
- use only a clean fast-forward synchronization to current `main`; no reset,
  forced update, replacement checkout, or history rewrite;
- prove the post-sync `HEAD` is on the expected `main` lineage containing PR
  #284 and merge commit
  `50c2c7d210cf94cae99e43a75ea24dc5df2199db` for PR #285;
- independently hash the post-sync executor bytes and require exactly
  `b82591be0d8f4f9876a8925e4428c3c0dc85589431733dfca178f86b3e415412`;
- stop on every mismatch and preserve evidence; and
- do not restart `aios.service` or any other service.

This artifact governs those requirements but does not authorize or perform the
sync.

## Executable package-binding inspection

The merged installer uses a mixed model. Its `FILES` tuple hard-codes filename,
semantic byte count, transport byte count, and semantic SHA-256. It then loads
the approval and validates the closed schema, expiry, internally bound input
counts and hashes, DTO-projection trusted-facts hash, canonical
`package_payload_sha256`, manifest identity, and other evidence bindings from
the package.

The exact stale executable constants are confined to the
`approved-input-approval.json` member of `FILES`:

| Executable binding | Historical value | Active value |
|---|---:|---:|
| approval semantic bytes | `3549` | `3579` |
| approval transport bytes | `3550` | `3580` |
| approval semantic SHA-256 | `266c39426fae0b04dacf009436334dd34d6791368dcad5066a9b2a37b9bd8a57` | `2ea9e735d7a5183a3e247abf57438d6e095fd7e9858d5ce688d221f7e9050f26` |

The input member's hard-coded `1327`, `1328`, and
`e3c66fddf815c57f17baad49926c44588279d60cb4e78df867e0ae2189237a6d`
are unchanged verified values and are not stale. The manifest ID also remains
unchanged. The installer contains no executable hard-coded comparison for the
historical approval transport SHA, `trusted_facts_sha256`,
`package_payload_sha256`, approval ID, `approved_at_utc`, or `not_after_utc`;
those are package-loaded and structurally or cryptographically validated.

Because the three stale constants remain executable, a narrow, separately
reviewed and human-merged installer binding amendment is mandatory before any
runtime installation. That amendment must update the executable bindings,
regenerate and freeze the executor SHA, reconcile its paired authority policy,
and preserve all fail-closed behavior. Neither this finding nor the merged R6
binding amendment silently authorizes the stale executor.

## Active regenerated package bindings

Only this complete binding set may be used after executable reconciliation:

| Binding | Value |
|---|---|
| input semantic bytes | `1327` |
| input transport bytes | `1328` |
| input semantic SHA-256 | `e3c66fddf815c57f17baad49926c44588279d60cb4e78df867e0ae2189237a6d` |
| input transport SHA-256 | `2506e3ca741a2ee0429112af641c2febdae5675f522cd58a855f6b1d6896a837` |
| TF-A `trusted_facts_sha256` | `c006afcad84984baea6af164067fdd4cfc31cdcac5f86baf7b1ceefd6e4c5065` |
| `package_payload_sha256` | `3b25029b1015bd67eddab2557cfef8202a48fff546ffc79fc3ab708c144de1f4` |
| approval semantic bytes | `3579` |
| approval transport bytes | `3580` |
| approval semantic SHA-256 | `2ea9e735d7a5183a3e247abf57438d6e095fd7e9858d5ce688d221f7e9050f26` |
| approval transport SHA-256 | `1d24f693154e0e8c2ac4504b9e81086662670c870e785c4f0d4d79c3ded16ac8` |
| approval ID | `122625d8-d3fd-42a7-b9c6-c54fc1f367bf` |
| `approved_at_utc` | `2026-09-19T21:24:52.273127Z` |
| `not_after_utc` | `2026-09-26T21:24:52.273127Z` |

Model B remains package-local validation. PostgreSQL reads and writes are
prohibited.

## Private source materialization contract

The future target is exactly `/run/aios/stage-0.33c-p4s5-source`. It was absent
at R7 inspection and remains absent. Materialization is prohibited until after
the executable-binding reconciliation is independently reviewed and merged and
a later materialization authority is independently reviewed and merged.

The sole byte sources are the existing exact R5 artifacts:

- `/opt/aios/data/documents/.stage-0.33c-p4s7-regeneration-1284ecc0-54d9-4df8-9d30-791710770f9b/regenerated-approved-input.json`;
- `/opt/aios/data/documents/.stage-0.33c-p4s7-regeneration-1284ecc0-54d9-4df8-9d30-791710770f9b/regenerated-approved-input-approval.json`.

No reconstruction, reserialization, normalization, regeneration, alternate
source, or private-byte disclosure is permitted. A later authority must require
the source workspace and both artifacts to pass expected identity, real
directory/regular-file, non-symlink, owner, mode, exact byte-count, and all six
hash-domain checks before copying.

The target directory must be a real non-symlink `root:root` directory, mode
`0700`. The two target source files must be real regular non-symlink
`root:root` files, mode `0400`. Publication must use retained directory
descriptors, no-follow resolution, exclusive creation, bounded exact-byte
writes, file `fsync`, closure of every writable descriptor, parent-directory
`fsync`, and read-only no-follow reopening for independent byte, hash,
ownership, type, and mode verification. Existing, partial, uncertain, or
mismatched state is a STOP; there is no overwrite or unrelated path change.
No service restart is authorized.

## Runtime evidence directory remediation contract

The exact directory is
`/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/runtime-sync-evidence`.
R7 read-only inspection found a real non-symlink directory owned
`aiosadmin:aiosadmin`, mode `0750`. Its only observed child was the retained
Step-1 session directory with the expected two regular evidence files; no
suspicious residue was identified by the bounded name/type/metadata inspection.
Repository authority requires `aiosadmin:aiosadmin`, mode `0700` for later
installer consumption. The owner and group must not be changed to
`root:aiosadmin`.

Before a later, separately authorized mode remediation, re-resolve the exact
path without following symlinks and require a real directory, exact
`aiosadmin:aiosadmin` ownership, current state consistent with the recorded
prestate, and no suspicious residue requiring incident review. Any deviation
is a STOP. The sole authorized future mutation is changing that exact
directory's mode to `0700`; afterward independently verify exact path, inode,
real-directory type, non-symlink status, `aiosadmin:aiosadmin`, and `0700`.
Change no child or unrelated path and restart no service. R7 does not authorize
or perform the mode change.

## Approval freshness and terminal gates

At every later authority, preflight, claim, materialization, installation, and
execution gate, an absolute trustworthy UTC clock must prove exclusively
`now < 2026-09-26T21:24:52.273127Z`. Equality, a later time, an invalid clock,
or an unreadable clock is expired and requires STOP before mutation or
consumption. There is no automatic renewal, timestamp extension, or substitute
approval. Expiry before installation requires a new, separately governed
approval.

This governance authorizes no `aios.service` restart, PostgreSQL access,
harness execution, candidate creation, `authorization.json`, or Step 5. It is
ready only for independent review.
