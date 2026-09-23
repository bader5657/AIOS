# Stage 0.33C-P4S7-R18 Post-Merge Activation Record Creation Governance

Classification: `P4S7_POST_MERGE_ACTIVATION_CREATION_READY_FOR_REVIEW`

Creation readiness: **BLOCKED pending an authoritative activation serialization
contract**. Ready for review does not mean ready for activation creation.

## Scope and authoritative evidence

This is governance only. It creates no activation record, installation claim,
result evidence, final runtime target, staging object, candidate, or
`authorization.json`. It does not execute or import `one_shot_install.py`, modify
private sources, contact PostgreSQL, invoke the harness, restart services, or
authorize Step 5. No merge or runtime synchronization is performed by this stage.

The supplied P4S7-R17 PASS is the authoritative prior verification baseline,
including its independent-review acceptance and previously verified private
source state. R18 does not represent those historical observations as newly
performed verification. GitHub reports PR #289 merged by human account
`bader5657`, at the exact reviewed head and merge below. Its reviews and comments
collections are empty; independent-review acceptance is inherited from the
supplied R17 baseline, not inferred from a GitHub approval event.

Read-only R18 inspection on 2026-09-24 independently confirmed:

- `/opt/aios-src` HEAD is `a22ac1f13954040d6182ab2fa0614952f3e4f2b6`;
- `git status --porcelain=v1 --untracked-files=all` is empty;
- all three composite merge commits below are ancestors of that HEAD;
- the actual executor SHA-256 equals the current policy-bound SHA-256 below;
- activation, final target, claim, result companion, and governed staging names
  are absent from the inspected runtime and evidence directories.

The root-only private source directory was inaccessible to the inspecting
account. No private-source bytes were read or permissions weakened. Historical
R17 acceptance is not a substitute for fresh privileged operator evidence at
the future creation gate.

## Fixed path, purpose, and closed schema

The only activation path is:

`/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/p4s7-r13-post-merge-activation.json`

There is no alternate path, CLI override, or environment override. The record
provides final runtime proof of independently reviewed and human-merged PR #289,
the complete composite authority, and the exact runtime/executor/policy state.
Its existence alone never permits skipping verification or executing installation.

Exactly these nine keys are required; no missing, extra, or duplicate keys:

| Key | Frozen value or creation rule |
|---|---|
| `schema_version` | `aios-stage-0.33c-p4s7-r13-post-merge-activation-v1` |
| `authority_id` | `9d29c855-0f23-4539-a9b9-2e17dc89c49d` |
| `pr_number` | JSON integer `289` |
| `reviewed_head_sha` | `209618b845c844ad08915853fa1dfa07c1c9897a` |
| `authority_merge_sha` | `a22ac1f13954040d6182ab2fa0614952f3e4f2b6` |
| `expected_runtime_head` | `a22ac1f13954040d6182ab2fa0614952f3e4f2b6` |
| `executor_sha256` | `1042693ec4af0f95068426e67954ea9ba4477012b1e18a88bd125469d100df87` |
| `policy_reference` | `docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/00_ONE_SHOT_RUNTIME_INSTALLATION_AUTHORITY.md` |
| `activated_at_utc` | Generate only during future creation from actual UTC, formatted `YYYY-MM-DDTHH:MM:SS.ffffffZ`; never prefill, backdate, or reuse. |

All values except `pr_number` are JSON strings. The identifier is the existing
executor `AUTHORITY_ID`, not a newly generated identifier. Schema, identity,
policy path, and metadata come from the current executor constants and
`read_activation_record` / `validate_activation_schema` contract.

## Mandatory pre-creation gates

Every gate must pass immediately before creation; uncertainty, inaccessible
evidence, mismatch, or residue means STOP without cleanup or creation.

1. Require independent review and human merge of this governance, resolution of
   the serialization blocker below through reviewed governance, and evidence of
   PR #289 independent review at the frozen reviewed head and human merge.
2. Use local `/usr/bin/git -C /opt/aios-src` proof that the authority merge and
   expected HEAD are commits, and `merge-base --is-ancestor` succeeds for the
   authority merge against expected HEAD. Require actual HEAD exactly equal to
   expected HEAD and a completely clean tracked, staged, and untracked tree.
3. Separately require local ancestry success for every composite component:

   | Component | Merge SHA |
   |---|---|
   | PR #290 | `327732e611b6d6bb3b88c33775e320d2d5173862` |
   | PR #291 | `c58dcb92f49c529c00d6aeb09efe7fab7d00a47e` |
   | PR #289 | `a22ac1f13954040d6182ab2fa0614952f3e4f2b6` |

   No component may be omitted. Compare the bytes of
   `docs/intelligence/stage-0.33c-p4s7-runtime-install-execution-authority/00_FINAL_ONE_SHOT_RUNTIME_INSTALL_AUTHORITY.md`
   at the reviewed head and authority merge; require equality, preserving the
   executor's reviewed-authority binding.
4. Recompute SHA-256 of the actual runtime file
   `docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/one_shot_install.py`.
   Require actual digest = activation digest = policy-bound digest = the frozen
   digest above. Require runtime executor bytes equal the HEAD blob. Preserve
   the executor's policy authority-ID and classification checks. STOP on any
   mismatch; do not modify the executor or policy to make it pass.
5. Require actual UTC `now < 2026-09-26T21:24:52.273127Z`. Equality, expiry,
   unreadable time, or invalid time is STOP. No renewal or extension is granted.
6. Verify absence with no-follow directory-relative lookup, treating dangling
   symlinks and all other existing entry types as present. Under the fixed
   activation parent, require both `approved-input.json` and
   `approved-input-approval.json` absent. Require the activation basename absent.
7. In that parent's `runtime-sync-evidence` directory require both
   `step4-install-authority-9d29c855-0f23-4539-a9b9-2e17dc89c49d.json` and
   `step4-install-authority-9d29c855-0f23-4539-a9b9-2e17dc89c49d.json.result.json`
   absent as the UNUSED companion state. Require no prior ambiguous or durable
   consumption history; absence alone cannot erase history.
8. Require no entries beginning `.approved-input.json.stage-` or
   `.approved-input-approval.json.stage-` in the runtime parent. No cleanup,
   adoption, deletion, reset, replacement, or residue repair is authorized.
9. Require fresh privileged operator evidence that the previously verified
   private source state remains valid. Verify the exact paths, metadata,
   semantic/transport sizes and hashes, package/approval identity, TF-A and
   Model B bindings governed by the merged R13 authority and current policy.
   The source parent `/run/aios/stage-0.33c-p4s5-source` must remain a real,
   non-symlink `root:root` directory mode `0700`; both source files must remain
   regular, non-symlink, single-link `root:root` files mode `0400`. Evidence must
   identify verification time and results without exposing private content.
   Inaccessible or stale evidence is STOP, not assumed validity. Never weaken
   permissions or regenerate/modify private sources.
10. Require path-component safety and the existing directory contracts: runtime
    parent `root:aiosadmin` mode `0750`, evidence directory
    `aiosadmin:aiosadmin` mode `0700`, real directories without symlink traversal.

Merging this document into repository main must not silently advance the runtime
checkout. The expected runtime HEAD remains frozen. Any runtime advance is a
STOP requiring separate governance; never rewrite the frozen value opportunistically.

## Serialization finding and creation blocker

The current activation reader calls `exact_json(data)`, which decodes UTF-8 and
uses `json.loads` with duplicate-member rejection. It checks the closed schema
and metadata but does **not** require canonical byte serialization, a particular
key order, byte count, transport hash, or a terminal LF. There is no activation
writer in this contract from which an exact serializer can be derived.

Elsewhere the executor canonicalizes package objects with
`json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()`.
Its claim/result writers append LF. Neither behavior establishes activation
transport semantics. This governance does not borrow either as an asserted
activation requirement.

Consequently the requested exact existing activation canonical serializer is
not derivable. Activation creation MUST STOP until independently reviewed and
human-merged governance explicitly resolves the canonical serializer and
whether transport LF is required, consistently with the frozen executor. Do not
invent transport semantics, silently pick a serializer, or append an LF merely
because other artifacts use one. If resolution changes executor bytes, separate
governance must reconcile all frozen SHA bindings before creation can proceed.

## Future exclusive publication and verification

This section governs a future, separately executed action only after all gates,
including serialization resolution, pass. It is not an executable creation script.

1. As root, open the validated parent directory with no-follow traversal and
   retain its descriptor. Check absence, then exclusively create the exact
   basename with `O_CREAT | O_EXCL | O_WRONLY | O_NOFOLLOW | O_CLOEXEC` and mode
   `0400`, under restrictive umask. No alternate path or temporary replacement.
   Existing entries cause STOP even if their contents appear correct.
2. Generate the timestamp only now and produce the complete nine-key object
   using the resolved exact canonical serializer. Append exactly one terminal
   LF only if that resolved contract requires transport LF. Derive expected
   byte length and SHA-256 from those exact bytes, including any required LF.
3. Completely write the bytes, handling short writes. Verify by descriptor that
   the inode is regular, UID `0`, GID `0`, mode `0400`, link count `1`. These exact
   values come from `read_activation_record`, not an inferred permission model.
4. File `fsync`, close every writable descriptor to this inode, then parent
   directory `fsync`, in that order. Read-only mode alone does not close an
   already-open writable descriptor.
5. Reopen the exact basename `O_RDONLY | O_NOFOLLOW | O_CLOEXEC` relative to the
   same parent. Verify inode/device identity against the created inode, regular
   type, UID/GID/mode/link count, exact length and EOF, complete-byte equality,
   SHA-256, UTF-8/duplicate-free closed schema, all frozen values, canonical
   serialization, and creation-time UTC timestamp. Require no writable fd remains.
6. Record bounded verification evidence separately through the later stage's
   governed evidence mechanism; never write installation claim/result companions
   as activation evidence. No evidence path is authorized by this document.

Any write, close, fsync, reopen, identity, metadata, schema, size, or hash failure
is STOP and an incomplete/ambiguous activation publication. Do not install,
delete, overwrite, update, reset, repair, reuse, replace, or automatically retry.
An existing record must never be adopted as the output of a new creation stage.

## Required sequence and retained boundaries

Activation governance → independent review → human merge → activation creation
execution → independent activation verification → final pre-attempt verification
→ exactly one runtime-install attempt.

No stage may be collapsed. The serializer blocker must be resolved before the
creation execution stage. Independent activation verification must repeat the
binding, byte, metadata, durability-evidence, and no-side-effect checks. Final
pre-attempt verification must freshly repeat all current installer gates,
including approval freshness, private sources, actual interpreter/version,
runtime truth, targets, staging and UNUSED claim/result state. Creation does not
reserve freshness or consume the installation authority.

The later one-shot installation retains its independent post-execution
verification and Step-4 closure requirements. PostgreSQL, harness invocation,
candidate creation, `authorization.json`, service restart, and Step 5 remain
unauthorized. This R18 stage stops after publishing the narrow governance PR;
the next official action is independent review, including disposition of the
explicit serialization blocker. No automatic merge.
