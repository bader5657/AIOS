# P4S7 Recovery Review/Merge Evidence Contract — AIOS v1

Classification: `P4S7_RECOVERY_REVIEW_MERGE_CONTRACT_READY_FOR_REVIEW`

## Scope and authority

This supplementary governance defines the operator-verified protected-pin
model selected for AIOS v1. It supplements
[R34](../stage-0.33c-p4s7-recovery-activation/00_RECOVERY_ACTIVATION_GOVERNANCE.md)
without rewriting R32/R34, their historical evidence, or their current bindings.
This contract requires independent review and human merge before implementation
may rely on it. Review readiness is not operational authority. No automatic merge.

This change defines a mechanism only. It does not implement a reader, instantiate
an evidence record, publish a selector, supersede a binding, synchronize runtime,
create activation, or authorize installation. Unknown future identities remain
unknown. Signed evidence attestation is not adopted; it is a possible future
hardening option requiring separate key-management and authorization governance.

## Reused precedents and explicit extension

- [R13A](../stage-0.33c-p4s7-r13a-preclaim-enforcement/00_FINAL_PRECLAIM_EXECUTOR_ENFORCEMENT_AMENDMENT.md)
  supplies exact runtime identity, complete cleanliness, reviewed/merged blob
  equality, local Git checks, and failure before claim.
- [R15](../stage-0.33c-p4s7-final-authority-supersession/00_R13_FINAL_EXECUTOR_AND_ACTIVATION_BINDING_SUPERSESSION.md)
  uses separately reviewed addenda to preserve frozen historical authority.
- [R24](../stage-0.33c-p4s7-activation-binding-supersession/00_POST_PR295_ACTIVATION_BINDING_SUPERSESSION.md)
  separates the pinned runtime from later governance and combines retained PR
  identity evidence with local Git ancestry proof.
- [R18A](../stage-0.33c-p4s7-activation-serialization/00_ACTIVATION_CANONICAL_SERIALIZATION_CONTRACT.md)
  supplies canonical JSON, duplicate rejection, exact LF framing, and no repair.
- [R32](../stage-0.33c-p4s7-r32-recovery-bindings/00_RECOVERY_EXECUTOR_PACKAGE_BINDING_AMENDMENT.md)
  supplies recovery authority, approval, payload, and unchanged execution gates.
- R34 supplies the recovery activation schema and root-owned exclusive
  publication/custody controls.

The extension is explicit: a separately authorized, independently verified
protected selector authenticates one immutable repository evidence record.
Neither a Git hash, ancestry, merge message, PR number, file ownership, nor a
self-declared review result alone proves authorized human review and merge.

## Fixed locations and selection

Evidence records form an immutable series in repository `bader5657/AIOS`:

`docs/intelligence/stage-0.33c-p4s7-recovery-review-merge-evidence/records/<binding-id>.json`

`<binding-id>` is the record's canonical lowercase UUID `binding_id`. Each
reviewed/merged record remains byte-for-byte immutable. There is no `latest.json`,
directory scanning, highest-version discovery, alternate repository, path
override, implicit fallback, or selection by moving branch.

Exactly one protected selector selects the authoritative record:

`/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/p4s7-recovery-review-merge-trust.json`

The selector is a regular non-symlink file, UID/GID 0, exact mode `0400`,
`st_nlink == 1`. Traverse trusted ancestors with retained no-follow directory
descriptors and verify custody and device/inode stability. The runtime parent
retains its existing root:aiosadmin `0750` contract; no permissions are changed.
Read via a no-follow descriptor and verify file/path identity before and after
reading. A missing, replaced, changing, or unsafe selector is STOP.

## Closed selector schema

The object has exactly four required string fields:

| Field | Exact value or constraint |
|---|---|
| `schema_version` | `aios-p4s7-recovery-review-merge-trust-v1` |
| `evidence_commit` | Full lowercase Git commit ID matching `[0-9a-f]{40}` |
| `evidence_path` | Exact evidence-series path above, with the selected record's `binding_id` |
| `evidence_transport_sha256` | Full lowercase SHA-256 matching `[0-9a-f]{64}` |

Reject unknown, missing, duplicate, optional, null, or non-string fields. Reject
abbreviated IDs, symbolic refs, absolute evidence paths, traversal, alternate
basenames, and unresolved/non-commit objects. The selected evidence commit is
the independently verified actual merge of the evidence PR, not its branch head.

## Closed evidence schema

The top-level object has exactly the following fifteen required fields:

| Field | Type and exact value or constraint |
|---|---|
| `schema_version` | String `aios-p4s7-recovery-review-merge-evidence-v1` |
| `repository` | String `bader5657/AIOS` |
| `binding_id` | String, canonical lowercase UUID, full match `[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}`; filename equality |
| `authority_id` | String `7bc638e2-e1f4-4e87-a54a-4d0df031b130` |
| `policy_reference` | String `docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/00_ONE_SHOT_RUNTIME_INSTALLATION_AUTHORITY.md` |
| `activation_governance_reference` | String `docs/intelligence/stage-0.33c-p4s7-recovery-activation/00_RECOVERY_ACTIVATION_GOVERNANCE.md` |
| `approval_id` | String `3a478d87-5c4f-4778-9f88-2228f4d7167f` |
| `package_payload_sha256` | String `be7a1750eb77ae77e8f020fc3f29c5f047cf88d1720a387f50f58f58c877962e` |
| `expected_runtime_head` | String, full lowercase 40-character Git commit ID |
| `executor_sha256` | String, full lowercase 64-character SHA-256 |
| `policy_sha256` | String, full lowercase 64-character SHA-256 of exact policy file bytes |
| `reader` | Closed review/merge object below |
| `r32` | Closed review/merge object below |
| `r34` | Closed review/merge object below |
| `supersedes` | Closed predecessor object below |

Each review/merge object has exactly three required fields:

| Field | Type and constraint |
|---|---|
| `pr_number` | Positive JSON integer; exact integer type, never boolean/float/string |
| `reviewed_head_sha` | String, full lowercase 40-character Git commit ID |
| `merge_sha` | String, full lowercase 40-character Git commit ID |

`r32.pr_number` is exactly 299 and `r32.merge_sha` is exactly
`ba717f6990d775748f46d62ef03a696f1618077b`. `r34.pr_number` is exactly 300 and
`r34.merge_sha` is exactly `8e9a8023742773b055e17dba002b2ebf07528118`.
Reviewed heads must be established by retained independent review and actual
PR/merge evidence; a parent relationship alone is not proof of review. Reader
PR/head/merge identities are populated only after their real review and merge.

`supersedes` has exactly four required string fields:

| Field | Constraint |
|---|---|
| `kind` | Exactly `r34-baseline` or `recovery-evidence-v1` |
| `commit` | Full lowercase 40-character commit ID containing the predecessor |
| `path` | Exact predecessor artifact path |
| `transport_sha256` | Full lowercase 64-character SHA-256 of its exact bytes |

For `r34-baseline`, commit is exactly the PR #300 merge above and path is exactly
the R34 governance reference. Hash the actual committed Markdown bytes, without
JSON parsing or normalization. No baseline digest is invented by this contract.
For `recovery-evidence-v1`, the path identifies the immediately preceding record
in the fixed series and commit is its independently verified evidence merge.
The commit/path/hash tuple identifies the predecessor; no synthetic baseline
UUID is needed. Every JSON object is closed at every depth. No security-critical
field is optional. Arrays and all other types are forbidden in these schemas.

## Canonical bytes and integrity

Both selector and evidence use exactly:

```python
semantic_bytes = json.dumps(
    value, ensure_ascii=False, sort_keys=True,
    separators=(",", ":"), allow_nan=False,
).encode("utf-8")
transport_bytes = semantic_bytes + b"\n"
```

Require strict UTF-8, duplicate-key rejection at every depth, exact closed schema
and types, and `canonical_bytes == semantic_bytes`. Transport has exactly one
ASCII LF. Reject BOM, CRLF, additional LF, whitespace differences, alternate
escapes, invalid numbers/constants, and all noncanonical bytes. Never strip,
normalize, coerce, or repair. Record and independently verify semantic/transport
counts and SHA-256 during later publication; these are not extra schema fields.
The selector digest and predecessor digests cover full transport bytes.

Read evidence from the exact commit tree entry, which must be a regular Git
blob (mode `100644`, not a symlink/gitlink), using local Git object bytes. Never
substitute a working-tree copy. Require full transport hash equality before
accepting the parsed record. Git availability/object/integrity failure is STOP.
No artifact contains its own commit hash or its own digest.

## Trust root and separately authorized selector publication

The trust root is explicit operator authorization plus independent verification
of retained PR/review/merge evidence, followed by protected selector publication
and fresh verification of its continuing authority. It is not self-authentication
by the JSON or proof supplied by root ownership alone.

Before publication, an independent verifier must establish for the evidence PR:
repository identity, PR number, exact final reviewed head, independent acceptance
of that head, actual human merge, and exact evidence-blob equality from reviewed
head to merge. Retain that verification and publication authorization under the
existing operator evidence process, bound to the selector's exact four fields
and exact bytes. It must also authenticate every declared component's PR,
reviewed head and actual merge, and the predecessor/unique-successor decision.
Unavailable or contradictory review evidence is STOP. A merge message, API
`merged` flag alone, Git parent, or stale historical PASS is insufficient.

Initial publication requires separate authorization and exclusive creation,
no-follow descriptor custody, complete writes, root:root `0400`, file fsync,
closure of all writable descriptors, parent fsync, then independent read-only
reopen and exact identity/metadata/byte/hash verification. Any existing entry,
partial publication, uncertainty, or race is STOP. No repair or automatic retry.

A later selector transition requires separate explicit authorization and fresh
independent verification of the old selector, new evidence, and exact immediate
predecessor. Preserve the previous selector bytes and publication evidence.
This contract does not authorize overwrite, deletion, replacement, or select a
transition execution procedure; that later action requires its own reviewed
publication/transition procedure before mutation. There is never automatic
advancement to a discovered successor.

## Future reader verification algorithm

Before private-source reads, claim, staging, publication, or any activation or
installation side effect, the future reader must perform all of the following:

1. Validate selector custody, closed schema and canonical bytes at the sole
   fixed path. Bind the read to stable descriptor/path identity.
2. Resolve exactly its pinned commit/path and read the exact regular Git blob.
   Verify transport SHA, then evidence schema and canonical bytes.
3. Require exact repository, authority, approval, payload, policy and R34
   references. No caller-supplied constants or compatibility fallback.
4. Verify R32/R34 identities and ancestry at the exact runtime HEAD. For each
   declared review/merge object, require a real two-parent merge whose second
   parent equals the declared reviewed head. Squash/rebase/octopus merges are
   unsupported in v1 and STOP. Never infer PR identity from commit messages.
5. Verify reviewed/merged equality for R32's amendment, executor and policy;
   R34's governance document; and the reader's executor and policy. Historical
   comparisons use their own reviewed/merged blobs, not today's runtime files.
   Require preserved R34 bytes at runtime to equal its historical merged blob.
6. Verify the reader review/merge identities against the operator-authenticated
   record and retained review evidence. The offline reader enforces the pinned
   identities/topology/blob equalities; independent operator verification
   establishes human review, PR mapping and authority. It must not fabricate
   those facts from Git. No executor network/API lookup is introduced.
7. Require actual runtime HEAD == evidence.expected_runtime_head == activation's
   expected_runtime_head, with clean staged, tracked and untracked state.
   Require R32, R34 and reader merges as ancestors. The reviewed reader must
   incorporate this independently reviewed/merged contract; its implementation
   must pin that contract's then-known merge and exact governance blob, and
   verify that merge's ancestry and blob equality. Do not invent that SHA now.
8. Require actual executor bytes == runtime HEAD executor blob == reader merge
   executor blob. Require their SHA == evidence.executor_sha256 == activation
   executor_sha256 == policy-bound executor SHA. Require runtime policy bytes ==
   runtime HEAD policy blob == reader merge policy blob, SHA == policy_sha256,
   and the policy's active recovery authority to match. No policy repair.
9. Follow exact predecessor commit/path/hash links, validating every predecessor
   record under this same contract, until the exact R34 baseline. For historical
   records compare their own committed runtime/executor/policy identities, not
   the current live HEAD. Require unique binding IDs, no cycles, and predecessor
   evidence merges to precede successor evidence merges by Git ancestry.
10. Reject altered history, forks, skipped predecessors, conflicting authorized
    successors or stale selector authority. Structural chain verification is
    local; completeness/currentness of authorized succession requires fresh
    independent operator verification described below. No directory scan can
    substitute for that verification.
11. Preserve all existing interpreter, private-source custody, approval freshness,
    canonical package/TF-A/Model B, unused-authority, target absence and preclaim
    gates. Independently compare activation approval/payload bindings with the
    freshly validated approval and recomputed payload, after trust gates pass.

Use the existing literal `/usr/bin/git -c safe.directory=/opt/aios-src -C
/opt/aios-src ...` contract with environment exactly `{"PATH":"/usr/bin:/bin"}`.
No persistent Git configuration change, alternate repository, network fetch by
the executor, import/invocation of the installer as a verification shortcut,
or weakening exact equality to ancestry is permitted.

Any unavailable, ambiguous, malformed, stale or inconsistent evidence, exception,
schema/byte/type/hash mismatch or identity drift is `PRECONDITION_FAILED` before
private-source reads, claim, staging and publication. No activation is performed
by this evidence reader. Missing trust never falls back to the historical R13
activation or its reviewed-head/merge semantics.

## Bootstrap, anti-circularity and supersession

The ordered lifecycle is mandatory:

1. Independently review and human-merge this mechanism-only contract.
2. Implement the reader, binding this now-known contract identity.
3. Independently review and human-merge that reader implementation.
4. Establish actual reviewed head, reader merge, separately authorized synced
   runtime HEAD, executor SHA and policy SHA. No guessed future values.
5. Under separate binding-supersession authority, populate the evidence record
   from those known values and the exact predecessor. This later record is the
   machine-readable binding-supersession artifact; no record is created here.
6. Independently review and human-merge that evidence record, then independently
   verify the actual merge and retained review evidence.
7. Separately authorize and publish the protected selector containing that
   evidence commit, path and transport SHA. Independently verify publication.
8. Only then may the reader trust the selected external evidence, subject to
   fresh operator verification and all preserved gates. Activation creation
   and execution still require their separate authorizations.
9. Later reader amendments repeat implementation/review/merge and establish new
   identities. Later bindings repeat evidence review/merge/publication with
   explicit immediate-predecessor supersession. No authority or approval renewal
   is implicit; changing the fixed authority/approval requires new governance.

The evidence never embeds its own merge SHA. Its selector is produced only
after evidence merge; the selector embeds no own commit or self-hash. The reader
need not embed its own future merge or digest. Runtime may remain pinned while
the later evidence merge exists locally as Git objects, following R24. Evidence
and predecessor objects must be made available through separately authorized
preparation without advancing runtime HEAD; missing objects remain STOP.
The later evidence merge is not required to be an ancestor of the earlier
runtime. Instead it must descend from the reader/runtime lineage it attests.
Fetching objects does not establish human review or supersession authority.

## Freshness and limits of offline verification

An offline reader cannot discover an unpublished or unavailable later
revocation, hidden successor, or a replay of a formerly valid protected pin.
Neither a clean checkout nor a valid hash chain proves continuing authorization.

Every recovery activation attempt and subsequent execution attempt therefore
requires fresh authorized operator verification, immediately before the attempt,
that the exact protected selector remains current and authoritative, its
predecessor chain is complete, and no revocation or conflicting authorized
successor exists. Retain that verification bound to the exact selector bytes
and attempted action. It cannot be inferred from an earlier PASS or file mtime.
If unavailable, uncertain, changed, or contradicted before the attempt, STOP.
The reader's offline PASS never substitutes for this mandatory external gate.
This contract does not add a self-declared freshness field to either schema.

## Compatibility with R34 and preserved boundaries

The activation record remains exactly eight required string fields:
`schema_version`, `authority_id`, `expected_runtime_head`, `executor_sha256`,
`policy_reference`, `approval_id`, `package_payload_sha256`, `activated_at_utc`.
Review/merge fields never return to that record. All R34 canonicalization,
timestamp, custody, publication, independent-verification and execution
boundaries remain binding. This addendum supplies R34's missing external trust
mechanism; no historical R32/R34 edit is needed.

R34's existing HEAD/SHA bindings remain authoritative until separately reviewed,
human-merged supersession and authorized selector publication establish a new
binding. Merely merging this mechanism-only document changes none of them.
Reader support does not authorize activation, consume recovery authority, reserve
the approval window or grant one-shot installation rights.

## Required future specification and implementation tests

Tests must use isolated temporary Git graphs/files and synthetic custody/review
fixtures, never production selectors, activation, private sources or databases.

| Area | Mandatory cases |
|---|---|
| Selector custody | Missing selector; wrong owner/group/mode/link count; symlink including dangling; unsafe ancestor; changed descriptor/path identity |
| Selector parsing | Malformed JSON/UTF-8; missing/extra/duplicate keys; wrong types; noncanonical bytes; BOM/CRLF/missing or repeated LF; no normalization |
| Git resolution | Missing commit/blob; non-commit ID; wrong/traversing evidence path; symlink/gitlink entry; working-tree substitution; wrong transport hash |
| Evidence parsing | Malformed JSON; missing/extra/duplicate keys at every depth; wrong types including boolean/float PR number; noncanonical bytes |
| Fixed identities | Wrong repository, authority, approval, payload, policy or R34 reference; filename/UUID mismatch |
| Runtime and policy | Wrong executor SHA; wrong policy SHA; wrong runtime HEAD; executor/blob inequality; dirty staged/tracked/untracked state; absent required governance lineage |
| Review and merge | Wrong reviewed head; wrong merged head; altered reviewed blob; altered merged blob; invalid/unsupported merge topology; missing or contradictory retained independent review/PR evidence |
| Succession | Stale authority; predecessor fork; cycle; skipped predecessor; duplicate identity; altered historical evidence; conflicting authorized successor; wrong baseline; stale/replayed selector |
| Failure boundary | Every failure yields PRECONDITION_FAILED with zero private-source reads, claim, staging, publication and activation effects; no fallback/repair/retry |
| Positive fixture | One end-to-end authenticated evidence chain, synthetic independent operator verification, canonical selector/evidence, real isolated Git blobs/topology, exact runtime/policy/executor bindings and preserved package gates |
| Freshness limitation | Locally valid but externally revoked/unverified selector remains blocked by operator gate; offline PASS cannot claim unseen-revocation detection |
| Anti-circularity | Reader/runtime commit precedes evidence merge; exact evidence read from later Git objects without runtime advancement; no self-commit or self-hash fields |

These tests are specified, not implemented or executed by this governance task.
The positive fixture must explicitly model the external operator gate; mocks
must not be described as proof of live human review or live runtime readiness.

## Disposition

Only this supplementary governance document is added. No executor/policy,
historical evidence, binding, runtime, service, database, production selector,
production evidence record or activation is changed. No migration, restart,
rebuild, source publication, claim, installer or harness invocation occurs.

Next action: independent review of this governance contract and human merge if
accepted. Reader implementation is a separate subsequent task. STOP.
