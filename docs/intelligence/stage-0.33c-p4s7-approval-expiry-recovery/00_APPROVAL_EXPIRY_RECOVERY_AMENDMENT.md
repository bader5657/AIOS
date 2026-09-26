# AIOS P4S7-R30 Approval Expiry Recovery Amendment

Classification: `P4S7_APPROVAL_EXPIRY_RECOVERY_GOVERNANCE_READY_FOR_REVIEW`

## Scope and effect

This governance-only amendment resolves R29's approval-renewal contradiction.
It requires independent review and human merge. It creates no fresh approval,
activation, execution permission, or Step-5 authority. No automatic merge.

The new recovery authority identity is
`7bc638e2-e1f4-4e87-a54a-4d0df031b130`. This is an inactive governance identity,
not a new approval ID or a claim. It supersedes only the expired-approval
execution path of historical authority
`9d29c855-0f23-4539-a9b9-2e17dc89c49d`, after the required reviews and merges.
The historical authority is not reused for future execution. All unchanged
safety controls remain mandatory; this does not broaden installation scope.

This is a prospective, narrowly scoped exception to the historical prohibition
on regenerated approval, not permission to repair or rewrite old artifacts.
Historical authorities and their recorded decisions remain immutable.

## Historical preservation and evidence provenance

Preserve byte-for-byte, without overwrite, delete, relocation, or in-place
mutation, both old private sources under
`/run/aios/stage-0.33c-p4s5-source/`:
`approved-input.json` and `approved-input-approval.json`.
Preserve the existing activation at
`/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/p4s7-r13-post-merge-activation.json`.
Preserve its metadata, historical authority state, and existing claim/result
absence evidence. Do not fabricate a retrospective installer result.

The operator-supplied history incorporated here states: the first invocation
exited 1 with `STOP: Stop`, with no claim, result, final targets, or staging;
the authority remained UNUSED. The supplied subsequent R28 root diagnosis
reported all preclaim gates PASS. These are supplied historical facts, not
new root checks performed by R30. Later passing gates do not establish the
original Stop cause. Approval expiry is a subsequent recovery constraint,
not an inferred cause of that first failure.

| Historical binding | Immutable historical value |
|---|---|
| Approval ID | `122625d8-d3fd-42a7-b9c6-c54fc1f367bf` |
| Approved at | `2026-09-19T21:24:52.273127Z` |
| Not after | `2026-09-26T21:24:52.273127Z` |
| Approval semantic count | `3579` bytes |
| Approval transport count | `3580` bytes |
| Approval semantic SHA-256 | `2ea9e735d7a5183a3e247abf57438d6e095fd7e9858d5ce688d221f7e9050f26` |
| Package payload SHA-256 | `3b25029b1015bd67eddab2557cfef8202a48fff546ffc79fc3ab708c144de1f4` |
| Pre-recovery executor SHA-256 | `3eec6a3b0cf0e1d9a768c15bf445876d3a463f38528a8fb4046ea27ba750ed97` |

Preserve all existing historical hashes, including the transport hash in its
original evidence. R30 does not read private bytes or invent an unavailable
transport digest. Future verification must establish any missing historical
digest read-only from those exact bytes. Never relabel historical values as
active recovery bindings. Historical UNUSED state does not authorize retry.

## Frozen input, business facts, TF-A, and Model B

The current closed input schema has no approval ID or approval-window fields.
Renewal therefore requires no input change: freeze `approved-input.json`
byte-identically, with semantic count `1327`, transport count `1328`, and
semantic SHA-256
`e3c66fddf815c57f17baad49926c44588279d60cb4e78df867e0ae2189237a6d`.
Future independent verification must compare exact input bytes, including LF,
and their transport hash. Any mismatch is STOP with its exact reason; do not
reconstruct input from business facts or normalize old bytes.

No drift is permitted in trusted_receipt_facts, supplier, document metadata,
item order, descriptions, quantities, units, material IDs, retained evidence,
manifest bindings, provenance, or other input/payload fields outside the
explicit renewal set below.

TF-A remains exactly
`c006afcad84984baea6af164067fdd4cfc31cdcac5f86baf7b1ceefd6e4c5065`:
the canonical deterministic TrustedReceiptFacts DTO-projection digest, with
no raw-subobject fallback. Model B remains exactly:

```text
approval.package_payload.evidence.registry_record_id == null
approved_input.ingestion_result.registry_record_id == null
approved_input.ingestion_result.registration_succeeded == false
```

No PostgreSQL lookup is required or authorized.

## Exact renewal allowlist and deterministic diff

The existing closed approval schema is retained. Its only mutable payload
values are these exact approval-root JSON pointers:

```text
/package_payload/approval_id
/package_payload/approved_at_utc
/package_payload/not_after_utc
```

These fields occur only at these locations in the current schema. No recursive
name-based wildcard, schema extension, extra member, or alternate occurrence
is allowed. At payload-relative scope the set is exactly `/approval_id`,
`/approved_at_utc`, `/not_after_utc`. All three must change.

Independent verification must parse historical and fresh JSON with duplicate
key rejection and enforce the same closed schema, types, and canonical bytes.
The expired historical approval is read solely as history; historical expiry
must not be bypassed in an active execution gate. Recursively compare objects
by sorted key union and arrays by index, preserving array order. Report added,
removed, type-changed, and unequal scalar values at escaped RFC 6901 pointers;
array length changes also fail. Use type-sensitive equality, so booleans do not
compare equal to integers. Require the sorted changed-pointer set for the two
payloads to equal exactly the three payload-relative pointers above.

At whole-approval scope, require exactly those three prefixed pointers plus
`/package_payload_sha256`. That fourth difference is solely the mandatory
derived checksum specified below, not a fourth discretionary metadata change.
The schema_version and every other field must remain identical. No missing
required change or extra difference is acceptable.

In particular, `project_owner_approval_reference`, `repository_commit`,
harness/interpreter/callable bindings, evidence, input hashes/counts, TF-A,
item count, provenance, and justification remain unchanged. Runtime deployment
identity is separately governed; it does not permit changing the payload's
repository_commit. If a fresh approval cannot truthfully retain the existing
reference, STOP for a separately reviewed amendment; do not silently expand
this allowlist.

## Fresh Project Owner approval and validity window

Explicit fresh Project Owner approval is mandatory after this amendment's
independent review and human merge, before fresh artifact creation. It must
confirm the same retained evidence, business facts, item order, TF-A, Model B,
and approval-metadata renewal only. Neither R30, UNUSED state, nor prior owner
approval implies that fresh approval.

Retain a separate auditable owner decision tied to this recovery authority and
the historical approval. Future creation/verification evidence must bind that
decision to the newly generated approval ID and exact artifact hashes. This
adds no field to the closed approval and does not rewrite the old reference.

Generate the fresh canonical lowercase UUIDv4 only during fresh approval
creation; it must differ from `122625d8-d3fd-42a7-b9c6-c54fc1f367bf`.
No fresh approval UUID or timestamps are generated by R30.

The established window is exactly seven days (604800 seconds), derived from
the historical approved_at/not_after pair. Set approved_at_utc to the actual
fresh approval/creation event in UTC, without backdating; perform creation
under that explicit contemporaneous approval. Set not_after_utc exactly to
approved_at_utc plus seven days. Both use valid ASCII
`YYYY-MM-DDTHH:MM:SS.ffffffZ`. If approval and creation cannot be coordinated,
STOP for a fresh owner decision; do not silently shift approval time.
Any different duration requires independent review and human-approved amended
governance before creation. Never extend the historical record.

Fresh gates require approved_at_utc <= actual UTC now < not_after_utc;
equality at expiry, invalid/unreadable clock, or expiry is STOP. Review or
activation does not reserve freshness or authorize automatic renewal.

## Future canonical bytes and derived bindings

The serializer is UTF-8, ensure_ascii=False, sort_keys=True,
separators=(",", ":"), allow_nan=False. No BOM, normalization, CRLF, or
surrounding whitespace. The following is a specification, not executable
authorization:

1. Canonicalize the fresh package_payload without LF and compute its SHA-256.
2. Set the outer package_payload_sha256 to that new digest; verify it differs
   from the historical value. The old digest is historical only.
3. Canonicalize the whole approval without LF: these are semantic bytes.
4. Transport bytes are semantic bytes plus exactly one ASCII LF.
5. Compute len(semantic bytes), len(transport bytes), SHA-256 of semantic
   bytes, and SHA-256 of transport bytes; require transport count = semantic
   count + 1. Do not assume counts changed or remained equal.

Fresh approval creation necessarily computes the derived payload checksum to
form a valid artifact. The later independent diff and binding-computation
stages must independently recompute and freeze all values; these distinct
gates are not collapsed by serialization dependencies.

Fresh private artifacts must use separately governed, distinct storage, with
exclusive creation and no overwrite of old sources. Exact paths and custody
must be frozen before creation. Keep raw business data outside Git. No fresh
hash/count is claimed here; those values do not exist yet.

## Required executor and activation amendments

A new executor/package-binding amendment is required after fresh values exist.
The current FILES constant hard-binds approval semantic size/hash and transport
count. The current payload checksum check recomputes the declared digest;
it is not a separate literal historical payload-SHA constant in the executor.
Exact approval-byte binding transitively binds that payload digest, and the
authority also freezes it. Update all active bindings consistently without
weakening validation. R30 modifies no executable code.

The later reviewed executor must use the new recovery authority identity and
claim/result namespace, the governed fresh sources, and a distinct recovery
activation path/version. Old approval/activation fallback is prohibited.
Preserve all one-shot, no-follow, metadata, durability, source, package, TF-A,
Model B, target-absence, staging-absence, freshness, and fail-closed controls.
Stop on old claim/result presence or ambiguous historical consumption as well
as any new claim/result presence; a new identity is not a consumption reset.

New activation governance must separately freeze the exact path/version,
closed schema, policy reference, reviewed/merged authority identities, runtime
HEAD, executor SHA, and safe exclusive publication/verification controls
before creation. The old activation path must never be overwritten or reused.
The executor amendment must prebind the proposed new activation contract;
later activation governance must match that reviewed contract exactly. Any
necessary code change requires another reviewed amendment and runtime sync
before activation, not an unreviewed repair. No circular self-containing commit
or unknown future merge value may be fabricated.

Fresh root verification retains the exact process-local Git trust setting
`/usr/bin/git -c safe.directory=/opt/aios-src -C /opt/aios-src ...`
and subprocess environment `{"PATH": "/usr/bin:/bin"}`. No Git config changes.

## Mandatory recovery order: no collapse

1. R30 recovery governance.
2. Independent review.
3. Human merge.
4. Explicit fresh Project Owner approval.
5. Create fresh approval private artifact.
6. Independent allowlisted-diff verification.
7. Compute and independently freeze new package/approval hashes and counts.
8. Executor/package-binding amendment.
9. Independent review.
10. Human merge.
11. Runtime synchronization under separately established authority.
12. New recovery activation governance.
13. Independent review.
14. Human merge.
15. New activation creation.
16. Independent activation verification.
17. Fresh final pre-attempt verification of every preclaim gate and history.
18. Separate explicit exactly-one-install execution authority.
19. One install attempt, retaining the executor's immediate preclaim checks.
20. Post-execution verification.
21. Step-4 closure only on verified completion.
22. Only then Step-5 consideration, under separate governance.

Each gate must pass before its successor. A STOP preserves all history and
requires further governance; it never grants cleanup, automatic retry, another
renewal, or authority reuse. Expiry during this sequence is STOP. No claim is
created to reserve an attempt. Step-4 failure does not permit closure or Step 5.

## R30 boundaries and disposition

| Action | R30 result |
|---|---|
| Fresh approval created | NO |
| Old approval/input/private sources modified or overwritten | NO |
| Old activation modified | NO |
| New activation created | NO |
| Executor modified | NO |
| Runtime modified | NO |
| Installer executed or authorized | NO |
| Claim/result created | NO |
| Targets/staging created | NO |
| PostgreSQL contacted | NO |
| Harness invoked | NO |
| Candidate created | NO |
| authorization.json created | NO |
| Services restarted | NO |
| Step 5 authorized | NO |

No remaining schema contradiction blocks review: the exact three-field payload
diff and mandatory outer derived-checksum difference are explicitly separated.
Future execution remains blocked on all later stages, exact fresh bindings,
and new activation authority. Private equality and fresh root gates are future
verification requirements, not claims of measurements performed in R30.

Basis: [historical final authority](../stage-0.33c-p4s7-runtime-install-execution-authority/00_FINAL_ONE_SHOT_RUNTIME_INSTALL_AUTHORITY.md),
[installer policy](../stage-0.33c-step4-one-shot-runtime-install-authority/00_ONE_SHOT_RUNTIME_INSTALLATION_AUTHORITY.md),
[closed-schema executor](../stage-0.33c-step4-one-shot-runtime-install-authority/one_shot_install.py),
and [R24 activation binding history](../stage-0.33c-p4s7-activation-binding-supersession/00_POST_PR295_ACTIVATION_BINDING_SUPERSESSION.md).

Next official action: independent review of this single governance amendment,
then human merge if accepted. This PR does not merge itself or authorize any
later operational step. STOP.
