# Stage 0.33C-P4S7-R20 Post-Merge Activation Record Creation Governance

Classification: `P4S7_ACTIVATION_GOVERNANCE_RECONCILED_READY_FOR_REVIEW`

The former serialization-definition blocker is **resolved** by merged PR #293's
canonical contract and merged PR #294's enforcement, now present in the runtime
executor. Activation creation remains **BLOCKED pending
independent review and human merge of this updated PR #292, fresh privileged
private-source verification, and all immediate pre-creation gates below**.
Review readiness does not mean activation-creation authorization.

## Scope and authoritative evidence

This is governance only. It creates no activation record, installation claim,
result evidence, final runtime target, staging object, candidate, or
`authorization.json`. It does not execute or import `one_shot_install.py`, modify
private sources, contact PostgreSQL, invoke the harness, restart services, or
authorize Step 5. No merge or runtime synchronization is performed by this stage.

The supplied P4S7-R19 PASS is the authoritative runtime baseline. It binds
runtime HEAD `abb11a25dd7810c4742ae2a724f0c1bd89de3efd`, actual and
policy-bound executor SHA-256
`f649b19c09c9d719b11577b14bfad0ce458f5c4dd6ccfd88c6727594787c81aa`,
canonical activation serialization enforcement present, and the activation
record absent. Earlier R17 independent-review acceptance and private-source
verification are historical evidence, not newly performed privileged checks.
GitHub reports PR #289 merged by human account
`bader5657`, at the exact reviewed head and merge below. Its reviews and comments
collections are empty; independent-review acceptance is inherited from the
supplied R17 baseline, not inferred from a GitHub approval event.

Read-only R20 inspection on 2026-09-26 (Asia/Jakarta) confirmed:

- `/opt/aios-src` HEAD is `abb11a25dd7810c4742ae2a724f0c1bd89de3efd`;
- `git status --porcelain=v1 --untracked-files=all` is empty;
- the actual executor SHA-256 equals the policy-bound SHA-256 below;
- the runtime activation reader requires canonical semantic-byte equality,
  exactly one terminal LF, exact integer `pr_number`, and ASCII six-digit-`Z`
  timestamp; and
- the activation record is absent.

The root-only private source directory was inaccessible to the earlier R18
inspecting account. This R20 inspection did not read private-source bytes or
weaken permissions. Historical R17 acceptance is not a substitute for fresh
privileged operator evidence at the future creation gate.

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
| `expected_runtime_head` | `abb11a25dd7810c4742ae2a724f0c1bd89de3efd` |
| `executor_sha256` | `f649b19c09c9d719b11577b14bfad0ce458f5c4dd6ccfd88c6727594787c81aa` |
| `policy_reference` | `docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/00_ONE_SHOT_RUNTIME_INSTALLATION_AUTHORITY.md` |
| `activated_at_utc` | Generate only during future creation from actual UTC, formatted `YYYY-MM-DDTHH:MM:SS.ffffffZ` with ASCII digits and uppercase `Z`; never prefill, backdate, or reuse. |

All values except `pr_number` are JSON strings. `pr_number` must have exact JSON
integer type and value `289`: booleans, `289.0`, exponent notation, and strings
are invalid. The timestamp must be a valid UTC calendar time with exactly six
fractional digits; offsets, missing fractions, and non-ASCII digits are invalid.
The identifier is the existing
executor `AUTHORITY_ID`, not a newly generated identifier. Schema, identity,
policy path, and metadata come from the current executor constants and
`read_activation_record` / `validate_activation_schema` contract.

## Mandatory pre-creation gates

Every gate must pass immediately before creation; uncertainty, inaccessible
evidence, mismatch, or residue means STOP without cleanup or creation.

1. Require fresh independent review and human merge of this updated PR #292.
   Require the merged PR #293 canonical contract and merged PR #294 enforcement
   to remain incorporated in the runtime executor. Require evidence of PR #289
   independent review at the frozen reviewed head and human merge.
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
   | PR #293 canonical serialization contract | `c8e2bdf9180ce71cc1dda5139ae786756e2dd22a` |
   | PR #294 enforcement | `abb11a25dd7810c4742ae2a724f0c1bd89de3efd` |

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
5. Require fresh approval-freshness proof from the exact unchanged private
   approval source, including its governed `not_after_utc`, immediately before
   activation creation. The previously governed bound expiry is
   `2026-09-26T21:24:52.273127Z`; require actual UTC
   `now < 2026-09-26T21:24:52.273127Z` and `now < not_after_utc` as read and
   validated from the private approval. Equality, expiry, unreadable time,
   inaccessible approval, mismatch, or invalid time is STOP. Creation neither
   reserves freshness nor grants renewal, replacement, or extension.
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
   This is a new privileged verification performed immediately before creation;
   R17 or R19 historical acceptance does not satisfy it. Inaccessible or stale
   evidence is STOP, not assumed validity. Never weaken
   permissions or regenerate/modify private sources.
10. Require path-component safety and the existing directory contracts: runtime
    parent `root:aiosadmin` mode `0750`, evidence directory
    `aiosadmin:aiosadmin` mode `0700`, real directories without symlink traversal.

Merging this document into repository main must not silently advance the runtime
checkout. The expected runtime HEAD remains frozen. Any runtime advance is a
STOP requiring separate governance; never rewrite the frozen value opportunistically.

## Canonical serialization and enforced reader contract

The [merged PR #293 canonical serialization contract](../stage-0.33c-p4s7-activation-serialization/00_ACTIVATION_CANONICAL_SERIALIZATION_CONTRACT.md)
resolves the former definition gap. The merged runtime executor now enforces it
in `read_activation_record` before any claim. Its semantic bytes are exactly:

```python
semantic_bytes = json.dumps(
    activation, ensure_ascii=False, sort_keys=True,
    separators=(",", ":"), allow_nan=False,
).encode("utf-8")
transport_bytes = semantic_bytes + b"\n"
```

The semantic JSON has no BOM or surrounding whitespace. Disk transport has
**exactly one terminal ASCII LF** (`0x0A`), with no CRLF, second LF, or space
before LF. The LF is transport framing and is excluded from the semantic-byte
comparison. Do not strip or normalize invalid bytes. The reader rejects
duplicate members, non-UTF-8, missing or extra keys, wrong value types, invalid
timestamp, and noncanonical semantic bytes with `PRECONDITION_FAILED` before
claim. The reader also preserves no-follow regular-file checks and requires
single-link `root:root` mode `0400`. No additional activation key or separate
activation hash field is introduced. These rules are now final governed
creation requirements, not a pending serialization decision.

## Future exclusive publication and verification

This section governs a future, separately executed action only after every
pre-creation gate passes. It is not an executable creation script.

1. As root, open the validated parent directory with no-follow traversal and
   retain its descriptor. Check absence, then exclusively create the exact
   basename with `O_CREAT | O_EXCL | O_WRONLY | O_NOFOLLOW | O_CLOEXEC` and mode
   `0400`, under restrictive umask. No alternate path or temporary replacement.
   Existing entries cause STOP even if their contents appear correct.
2. Generate the timestamp only now and produce the complete nine-key object
   using the exact canonical serializer above. Append exactly one terminal
   LF. Derive expected byte length and SHA-256 from those exact transport
   bytes, including the LF; these verification values are not schema fields.
3. Completely write the bytes, handling short writes. Verify by descriptor that
   the inode is regular, UID `0`, GID `0`, mode `0400`, link count `1`. These exact
   values come from `read_activation_record`, not an inferred permission model.
4. File `fsync`, close every writable descriptor to this inode, then parent
   directory `fsync`, in that order. Read-only mode alone does not close an
   already-open writable descriptor.
5. Reopen the exact basename `O_RDONLY | O_NOFOLLOW | O_CLOEXEC` relative to the
   same parent. Verify inode/device identity against the created inode, regular
   type, UID/GID/mode/link count, exact length and EOF, complete-byte equality,
   SHA-256, UTF-8/duplicate-free closed schema, all frozen values, exact integer
   `pr_number`, canonical semantic-byte equality, exactly-one-LF transport,
   and creation-time ASCII six-digit-`Z` UTC timestamp. Require no writable fd
   remains.
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

No stage may be collapsed. Independent activation verification must repeat the
binding, byte, metadata, durability-evidence, and no-side-effect checks. Final
pre-attempt verification must freshly repeat all current installer gates,
including approval freshness at that later gate, private sources, actual
interpreter/version, runtime truth, targets, staging and UNUSED claim/result
state. Creation does not
reserve freshness or consume the installation authority.

The later one-shot installation retains its independent post-execution
verification and Step-4 closure requirements. PostgreSQL, harness invocation,
candidate creation, `authorization.json`, service restart, and Step 5 remain
unauthorized. This R20 stage stops after updating the narrow governance PR.
The next official action is fresh independent review of updated PR #292,
followed only by human merge if accepted. No automatic merge or activation.
