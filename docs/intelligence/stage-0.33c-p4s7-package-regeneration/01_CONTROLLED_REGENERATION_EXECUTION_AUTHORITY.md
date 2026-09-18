# Stage 0.33C-P4S7-R3 Controlled Regeneration Execution Authority

Classification: `P4S7_CONTROLLED_REGENERATION_EXECUTION_AUTHORITY_READY_FOR_REVIEW`.
Authority ID: `1284ecc0-54d9-4df8-9d30-791710770f9b`.

## Activation and one-shot scope

This document proposes one non-reusable authority for a **future** controlled
regeneration of the Step-4 approved-input and approval pair. It is inactive
until independently reviewed and human-merged. Publication of this PR does not
claim, execute, or consume the authority and creates no private package bytes.
After activation, at most one controlled regeneration attempt may use it. No
generic regeneration CLI, source selector, output selector, overwrite, repair,
or second attempt is authorized.

The governance basis is PR #281, reviewed head
`ac11782702307e6e455f5e901cbeb27ace09e6ff`, merged at
`c102b81cbbb0fd2c02fa66b8b4ebbb7a04864601`. Execution must prove that
exact merge is an ancestor of its clean, reviewed repository checkout and that
this authority's independently reviewed merge is present. The schema revision
for this authority is exactly
`c102b81cbbb0fd2c02fa66b8b4ebbb7a04864601`; the approval's
`repository_commit` binds that revision. A later change to a relevant contract
file stops execution until separately reviewed governance rebinds it. The
following SHA-256 identities are part of the revision check:

| Contract file at the schema revision | SHA-256 |
|---|---|
| `core/app/material_receipts/stage033c_one_shot_harness.py` | `b9fc9fb22724184696eabf02525bcc0a626bdff5ce3943ed31ba2e21130f5cad` |
| `core/app/material_receipts/candidate_input.py` | `b91c47bf933fa9393991373b1c858ac97bb4f5ae8241239c7a725aa433f5bdc1` |
| `core/app/material_receipts/candidate_create_authorization.py` | `94ef0fcfac459f14b3316a5fb35f3d4832b9cad3146162a685e9208f8f2fe47d` |
| `core/storage/document_manifest.py` | `7887e074c162917ffed809354abfddcd1e5193bf0ecedfafbb47efebf4da42e3` |

The reviewed PR #278 installer remains
`docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/one_shot_install.py`,
SHA-256 `bc9ad237ed3a35d763ee2e609712bda26c7f8b05742847789cc2f4b3bb88af0d`.
This authority permits no change to that file or its semantics. The installer
still binds the unavailable old package values; a separate later frozen-binding
amendment must reconcile that fact before any runtime use.

## Bound source and facts

The only retained source is manifest
`9801b5e4-453d-429a-b51f-e8ffaa17a2c9`. Before claiming the attempt,
read-only revalidation must prove its canonical manifest path and ID, current
closed schema, exact byte size and SHA-256, status, media/metadata consistency,
and the stored original's real regular non-symlink file, byte size, and SHA-256.
The original must agree with the manifest and metadata. Missing, changed,
unsafe, or unsupported evidence stops before claim. No alternate source or
PostgreSQL lookup is authorized.

The exact approved Project Owner facts and item order are those frozen in the
merged [P4S7-R2 governance](00_CONTROLLED_PACKAGE_REGENERATION.md#frozen-project-owner-facts).
This authority adds or changes none. Supplier, document number/date, two item
descriptions, both `material_id: null` values, `sheet` units, colly counts,
and quantities must match that table exactly. Independently recompute
`125 * 50 + 0 = 6250` and `62 * 50 + 38 = 3138`; use the current DTO decimal
string rules. Neither `lembar` nor `sheet EF` may appear in a technical unit
field. Resolve every other required field and explicit null from retained
evidence or an existing Project Owner-approved fact; absence or ambiguity is a
STOP. OCR, LLM output, historical receipts, filenames, or defaults cannot
invent business facts.

Preserve merged PR #280 **Model B — hash-bound package cross-validation**:

```text
approval.package_payload.evidence.registry_record_id
==
approved_input.ingestion_result.registry_record_id
```

Equality is exact JSON equality without coercion. Failed registration requires
`null` in both locations; successful registration requires the same positive
integer in both. This proves internal package consistency only; it does not
prove an external Registry row and entails no PostgreSQL contact.

## Regeneration and approval contract

Build only the current harness-native closed input envelope from the bound
schema revision, retained manifest/source metadata, the unchanged approved
facts, merged governance, and the reviewed harness/input contract. Reject
missing, extra, or duplicate keys and invalid type, state, timestamp, quantity,
unit, evidence, or item-order relationships. Canonical JSON is UTF-8 with
`ensure_ascii=False`, `sort_keys=True`, `separators=(",", ":")`, and
`allow_nan=False`. Input semantic bytes are canonical JSON without LF. Input
transport bytes are semantic bytes followed by exactly one `0x0A` LF and no
other byte.

The fresh approval uses the current closed Step-4 wrapper and the same
canonicalization and one-LF transport rule. It requires a new UUIDv4
`approval_id`, absolute UTC microsecond-Z `approved_at_utc`, and
`not_after_utc` exactly 604,800 seconds later, exclusively valid while
`now < not_after_utc`. The Project Owner approval reference must be a fresh,
governed, bounded, non-secret reference to explicit approval of these new
bindings. No old approval bytes, ID, time, reference, or digest may be passed
off as the new approval. If explicit fresh approval cannot be obtained, the
attempt stops without an approved pair.

Regenerate `trusted_fact_provenance` with exactly 26 current closed JSON
Pointers: four receipt fields and eleven fields for each of the two indexed
items, including explicit nulls. The exact field list and pointer semantics
are those in P4S7-R2 and the schema revision. Values are only
`EVIDENCE_DERIVED` or `PROJECT_OWNER_APPROVED`, supported field by field;
missing or extra pointers stop the attempt.

Compute independently from actual canonical objects and freeze the input
semantic SHA-256, input transport SHA-256, canonical trusted-facts SHA-256,
canonical `package_payload` SHA-256, complete approval semantic SHA-256, and
complete approval transport SHA-256. The payload hash covers only the payload
without LF, avoiding self-hashing. Record actual input and approval semantic
and transport byte counts. Check the approval's embedded input hashes/counts,
trusted-facts hash, payload hash, evidence binding, and item count against
independent calculations. The approval transport hash, which is not a member
of the closed approval wrapper, is frozen in the regeneration summary. The
historical hashes and 1,327/1,328 or 3,549/3,550 byte counts are not targets;
matching lengths by coincidence does not establish old-byte identity.

## Exact private review workspace and one-shot claim

The sole future output workspace is
`/opt/aios/data/documents/.stage-0.33c-p4s7-regeneration-1284ecc0-54d9-4df8-9d30-791710770f9b`.
It is a persistent, private **review-material** workspace, separate from
`/run/aios/stage-0.33c-p4s5-source` and the final runtime package targets.
The sole future run-as identity is `aiosadmin:aiosadmin`; root execution is
outside this authority. The existing `/opt/aios/data/documents` parent must
first pass real-directory, `aiosadmin:aiosadmin` ownership, and no-symlink
path-component checks. Use retained directory descriptors and no-follow
relative operations so path replacement cannot redirect publication. An
unsafe or unavailable parent stops. The actor may create no alternate output
directory under this authority.

Before claim, construct and validate the prospective pair in private memory,
allocate the new approval reference, compute its exact hashes and counts, and
obtain explicit Project Owner approval of those final bindings. Check approval
freshness immediately before claim. If that cannot be completed without
writing output files, stop without claiming; this authority permits no
unapproved on-disk package. After these read-only and in-memory gates, the
sole attempt is claimed by exclusive,
no-follow creation of that exact workspace as a real directory, owned by the
future reviewed actor, mode `0700`. Workspace existence means this authority
has been claimed and prohibits every retry, including after a crash or failed
validation. The parent directory must be `fsync`ed before writing outputs.
An uncertain mkdir or parent-fsync outcome also prohibits automatic retry,
even if later directory absence is observed. The workspace and failed partial
files are retained for independent disposition; no deletion or reset is
authorized here. The persistent workspace directory is the durable claim
evidence. Any separate incident record may contain only the authority ID,
containing authority merge, claim timestamp, actor, schema revision, and
outcome, without raw package data. Absence of such a record cannot restore the
authority after a known claim attempt.

Inside the workspace the only package/review filenames are:

1. `regenerated-approved-input.json`;
2. `regenerated-approved-input-approval.json`;
3. `regeneration-summary.json`.

Each must be a real regular non-symlink file, owner equal to the reviewed actor,
mode `0400` after publication. Staging may start at `0600`. Use exact-name
exclusive creation with `O_CREAT | O_EXCL | O_NOFOLLOW`, no overwrite or
truncate-existing behavior, bounded complete writes, file `fsync`, close all
writable descriptors, parent `fsync`, then read-only no-follow reopen and
independent size/hash and mode/ownership verification. A failed or partial
write never becomes an approved package. Publish the summary last, only after
both package files and all checks pass. The summary's `validation_status` is
`REVIEW_MATERIAL_VALIDATED`, not a runtime-installation approval; independent
package verification and a separate binding amendment remain mandatory.
The input transport ceiling is 86,836 bytes, the approval transport ceiling is
13,620 bytes, and the minimized summary transport ceiling is 4,096 bytes.

## Closed minimized summary

`regeneration-summary.json` is canonical UTF-8 JSON with one LF and exactly
these keys, no others:

```text
schema_version: "aios-stage-0.33c-p4s7-regeneration-summary-v1"
authority_id: "1284ecc0-54d9-4df8-9d30-791710770f9b"
governance_merge_commit: "c102b81cbbb0fd2c02fa66b8b4ebbb7a04864601"
schema_revision: "c102b81cbbb0fd2c02fa66b8b4ebbb7a04864601"
manifest_id: "9801b5e4-453d-429a-b51f-e8ffaa17a2c9"
input_semantic_bytes: nonnegative integer
input_transport_bytes: input_semantic_bytes + 1
input_semantic_sha256: lowercase SHA-256
input_transport_sha256: lowercase SHA-256
trusted_facts_sha256: lowercase SHA-256
approval_semantic_bytes: nonnegative integer
approval_transport_bytes: approval_semantic_bytes + 1
approval_semantic_sha256: lowercase SHA-256
approval_transport_sha256: lowercase SHA-256
package_payload_sha256: lowercase SHA-256
approval_id: new canonical lowercase UUIDv4
approved_at_utc: UTC microsecond-Z timestamp
not_after_utc: UTC microsecond-Z timestamp
validation_status: "REVIEW_MATERIAL_VALIDATED"
model_b_binding_status: "PASS"
```

The summary contains no raw package JSON, supplier, document, item, OCR,
retained image, credential, or secret. Raw regenerated input and approval stay
outside Git. A Git report may contain only governed identifiers, hashes,
counts, timestamps, validation results, and package binding metadata. The
workspace is review material first; no file is copied to runtime sources by
this authority.

## Fail-closed boundary and remaining sequence

Any schema, canonicalization, quantity, unit, provenance, retained-evidence,
Model B, hash, count, owner-approval, freshness, privacy, or filesystem check
failure stops. Do not label a partial pair approved, publish a success summary,
materialize runtime sources, or amend PR #278 package bindings from an
unverified pair. There is no retry under this authority. A separate incident
review is required for a failed or uncertain claimed attempt.

This authority does not synchronize `/opt/aios-src`, change evidence-directory
mode, materialize `/run/aios/stage-0.33c-p4s5-source`, execute the installer,
contact PostgreSQL, invoke the harness, create a candidate or
`authorization.json`, or authorize Step 5. It does not close Step 4 or perform
any separately governed duplicate preflight.

The required order remains: PR #281 merge; this authority PR; independent
review; human merge; exactly one controlled regeneration attempt; independent
package verification; separate package-specific frozen-binding amendment;
independent review and human merge; separate runtime checkout and evidence-mode
remediation; separately authorized private-source materialization; repeat
P4S7 verification; separate runtime-install execution authority, review, and
human merge; then at most one runtime installation attempt. No stages may be
collapsed.
