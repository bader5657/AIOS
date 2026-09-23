# Stage 0.33C-P4S7-R13 Final One-Shot Runtime-Install Execution Authority

Classification: `P4S7_RUNTIME_INSTALL_EXECUTION_AUTHORITY_READY_FOR_REVIEW`

## Decision and activation boundary

This artifact creates the final, narrow execution authority for exactly one
future Step-4 approved-input runtime installation attempt. It is inactive until
this exact artifact receives independent review and is human-merged. It does
not perform the attempt, create or consume the installation marker, create a
final target or staging object, restart a service, contact PostgreSQL, invoke
the harness, create a candidate, create `authorization.json`, close Step 4, or
authorize Step 5.

After merge, this authority is non-reusable, non-resettable, and non-retryable
after any ambiguous or durable consumption. It authorizes no generic installer
mode and no second attempt. It supplements and narrows the merged one-shot
installer policy; it does not weaken or replace any fail-closed control in that
policy.

## Authoritative R12 pre-execution baseline

P4S7-R12 is accepted as the authoritative pre-execution verification PASS and
is frozen as follows:

| Binding | Exact value |
|---|---|
| runtime checkout | `/opt/aios-src` |
| runtime `HEAD` | `b92991c4d88f899e6a4a861c439d898332c62508` |
| complete working tree | clean |
| runtime interpreter | `/opt/aios/runtime/venv/bin/python` |
| governed Python | `3.12.3` |
| execution identity | Unix `root` |

The future attempt must require this exact runtime `HEAD`, a clean complete
working tree, the exact interpreter and governed version, and effective/account
identity `root`. A different commit, dirty or untracked state, interpreter,
version, or identity is a pre-claim STOP.

## Frozen executor, policy binding, and command

The only executor is:

`/opt/aios-src/docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/one_shot_install.py`

Its SHA-256, independently derived from the exact executor currently present
in the R12 runtime checkout, is:

`c1aa32502dff875eaf889c0644655b8c5f4a2fa0361f5a0622b976580e9bc61b`

The merged policy at
`docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/00_ONE_SHOT_RUNTIME_INSTALLATION_AUTHORITY.md`
must bind that same digest. The executor's self-hash, the policy-bound digest,
and the digest above must all match immediately before claim. No manually
reconstructed or alternate digest is accepted.

The exact future command is one no-argument invocation:

```text
/opt/aios/runtime/venv/bin/python /opt/aios-src/docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/one_shot_install.py
```

No CLI arguments, environment-selected source or target, alternate path,
import-as-helper use, generic mode, force option, overwrite option, retry, or
reset is authorized.

## Frozen private sources and byte bindings

The only private sources are:

- `/run/aios/stage-0.33c-p4s5-source/approved-input.json`
- `/run/aios/stage-0.33c-p4s5-source/approved-input-approval.json`

At pre-claim revalidation the source parent must be a real, non-symlink
`root:root` directory with mode `0700`. Each source must be a real, regular,
non-symlink `root:root` file with mode `0400` and link count exactly `1`.
No alternate source, reconstruction, reserialization, normalization, or
environment-driven path is permitted.

| Domain | Semantic bytes | Transport bytes | Semantic SHA-256 | Transport SHA-256 |
|---|---:|---:|---|---|
| approved input | `1327` | `1328` | `e3c66fddf815c57f17baad49926c44588279d60cb4e78df867e0ae2189237a6d` | `2506e3ca741a2ee0429112af641c2febdae5675f522cd58a855f6b1d6896a837` |
| approval | `3579` | `3580` | `2ea9e735d7a5183a3e247abf57438d6e095fd7e9858d5ce688d221f7e9050f26` | `1d24f693154e0e8c2ac4504b9e81086662670c870e785c4f0d4d79c3ded16ac8` |

The semantic objects are followed by exactly one terminal LF byte in each
transport object, with no additional byte.

## TF-A, package, Model B, and approval identity

The exact `trusted_facts_sha256` is
`c006afcad84984baea6af164067fdd4cfc31cdcac5f86baf7b1ceefd6e4c5065`.
TF-A means only the canonical deterministic `TrustedReceiptFacts` DTO
projection digest. Raw-subobject hashing or fallback is prohibited.

The exact canonical `package_payload_sha256` is
`3b25029b1015bd67eddab2557cfef8202a48fff546ffc79fc3ab708c144de1f4`.

Model B is frozen as exact package-local state:

```text
approval.package_payload.evidence.registry_record_id == null
approved_input.ingestion_result.registry_record_id == null
registration_succeeded == false
```

No PostgreSQL lookup is required or authorized.

The only approval identity and time window are:

| Binding | Exact value |
|---|---|
| `approval_id` | `122625d8-d3fd-42a7-b9c6-c54fc1f367bf` |
| `approved_at_utc` | `2026-09-19T21:24:52.273127Z` |
| `not_after_utc` | `2026-09-26T21:24:52.273127Z` |

Every execution gate must require absolute UTC `now < not_after_utc`.
Equality, expiry, an invalid clock, or an unreadable clock is a STOP. This
authority provides no renewal, extension, or replacement approval.

## Frozen targets, namespace, and directories

The only final targets, in governed publication order, are:

1. `/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/approved-input.json`
2. `/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/approved-input-approval.json`

Both must be absent immediately before claim. There is no overwrite, repair,
adoption, or replacement authority.

The governed staging prefixes are exactly:

- `.approved-input.json.stage-`
- `.approved-input-approval.json.stage-`

No existing entry with either prefix may be present immediately before claim.
Any debris is a STOP; cleanup or takeover of pre-existing debris is not
authorized.

The exact final parent is
`/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c`. It
must be a real, non-symlink `root:aiosadmin` directory with mode `0750`, and
every intermediate path-safety check must pass immediately before execution.

The exact evidence directory is
`/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/runtime-sync-evidence`.
It must be a real, non-symlink `aiosadmin:aiosadmin` directory with mode
`0700`. This authority does not otherwise modify it; only the installer's
already governed bounded consumption and result-evidence behavior is allowed.

## One-shot claim and durable-consumption barrier

The preserved state machine is exactly:

```text
UNUSED -> CLAIMED -> DURABLY_CONSUMED -> EXECUTION_STARTED
```

No staging or publication may begin before durable consumption. The mandatory
claim durability sequence is exactly:

```text
exclusive marker creation
-> complete marker write
-> file fsync
-> writable-fd close
-> parent-directory fsync
```

Only completion of the entire sequence establishes `DURABLY_CONSUMED` and
permits `EXECUTION_STARTED`. An ambiguous claim or durability failure is not
reusable even if the marker later appears absent. A durable claim is
irreversible. There is no lease, stale-marker takeover, delete, reset, repair,
automatic retry, or second attempt.

## Immediate pre-claim revalidation

Immediately before claim, the executor must revalidate all of the following as
one fail-closed gate set:

1. approval identity and `now < not_after_utc` freshness;
2. exact executor SHA-256 and the identical merged-policy SHA binding;
3. exact R12 runtime `HEAD`, clean complete working tree, interpreter, governed
   Python version, and root run-as identity;
4. private-source parent/file ownership, modes, types, non-symlink status, link
   counts, byte counts, and semantic/transport hashes;
5. both final targets absent and both staging-prefix namespaces debris-free;
6. final-parent, evidence-directory, and intermediate path safety;
7. exact Model B package-local state without PostgreSQL contact;
8. TF-A DTO-projection semantics and exact trusted-facts digest;
9. exact package-payload digest and all input, approval, and approval-identity
   bindings; and
10. unused one-shot authority with no ambiguous or prior consumption history.

Any failure is a STOP before claim. Passing governance review or an earlier
R12 observation never substitutes for this immediate revalidation.

## Publication success, failure, and evidence semantics

The only success classification is
`STEP4_APPROVED_INPUT_INSTALLATION_VERIFIED`, and it may be emitted only after:

1. durable consumption;
2. input publication, verification, and governed cleanup complete;
3. approval publication, verification, and governed cleanup complete; and
4. final pair reverification PASS.

All merged installer semantics remain binding, including
`APPROVED_BYTES_INVALID`, `CONSUMPTION_DURABILITY_UNCERTAIN`,
`STEP4_APPROVED_INPUT_PARTIAL_INSTALLATION`,
`APPROVED_INPUT_STAGING_PREPUBLICATION_CLEANUP_INCOMPLETE`,
`APPROVED_INPUT_STAGING_CLEANUP_INCOMPLETE`, and
`RESULT_EVIDENCE_WRITE_FAILED`. No failure, ambiguous state, partial install,
cleanup failure, or evidence-write failure permits silent retry.

After an attempt, the installer must produce only the already governed bounded
metadata evidence sufficient to independently verify one-time authority
consumption, executor identity, source and target hashes, publication state,
final verification state, cleanup state, and final classification. Raw package
content and business facts must not enter evidence, logs, or Git.

## Explicit exclusions and mandatory sequence

This authority permits only the Step-4 approved-input runtime installation
described above. PostgreSQL reads or writes, harness invocation, candidate
creation, `authorization.json`, service restart/reload, and Step 5 are not
authorized.

The mandatory sequence is:

```text
R13 authority creation
-> independent review
-> human merge
-> exactly one runtime installation attempt
-> post-execution independent verification
-> Step-4 closure
-> only then Step-5 consideration
```

No step may be collapsed. Human merge activates only the one attempt; it does
not itself execute or consume it. The next official action after publication
of this artifact is independent review of this narrow governance PR.

## Review classification

`P4S7-R13 EXECUTION AUTHORITY GOVERNANCE PASS`

- R12 PRE-EXECUTION BASELINE BOUND
- FINAL EXECUTOR / PACKAGE / APPROVAL BINDINGS FROZEN
- ONE-SHOT CONSUMPTION FROZEN
- PRE-CLAIM GATES FROZEN
- SUCCESS / FAILURE SEMANTICS FROZEN
- RUNTIME INSTALLER NOT EXECUTED
- POSTGRESQL CONTACT ZERO
- STEP 5 NOT AUTHORIZED
- READY FOR INDEPENDENT REVIEW
