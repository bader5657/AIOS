# Stage 0.33C-P4S7-R2 Controlled Approved-Package Regeneration

Classification: `P4S7_CONTROLLED_PACKAGE_REGENERATION_READY_FOR_REVIEW`.

## Decision and boundary

The exact private Step-4 approved-input and approval byte objects previously
bound by PR #278 are unavailable after the P4S7 post-merge recovery search.
The old input was bound as 1,327 semantic bytes, 1,328 transport bytes, and
semantic SHA-256 `e3c66fddf815c57f17baad49926c44588279d60cb4e78df867e0ae2189237a6d`.
The old approval was bound as 3,549 semantic bytes, 3,550 transport bytes, and
semantic SHA-256 `266c39426fae0b04dacf009436334dd34d6791368dcad5066a9b2a37b9bd8a57`.
These are historical identifiers, not targets for regeneration. Manual
reconstruction or a claim to recover those exact bytes is prohibited.

This governance authorizes a later **controlled regeneration** of a new Step-4
approved package using the unchanged Project Owner facts and selected retained
evidence. It does not create the package, approval record, hashes, runtime
private sources, an installation authority, or an execution attempt. PR #278
is merged at `4782aef7b6ab63aeccf3c2c813ce588b615173be`. PR #280's merged
Model B cross-validation remains governing. Step 4 remains open; Step 5 is not
authorized.

## Frozen Project Owner facts

Regeneration must preserve exactly the following Project Owner-approved
business facts and item order. The approval process must bind them again to
the new canonical bytes. No change is permitted without separate Project Owner
approval.

| Fact | Approved value |
|---|---|
| Supplier | `PT Universal Jasa Kemas` |
| Document number | `SJ-2607/0256` |
| Document date | `2026-07-02` |
| Item count | `2` |

| Item | Description | `material_id` | Technical `unit` | `full_colly_count` | `qty_per_full_colly` | `partial_qty` | `total_qty` |
|---:|---|---|---|---:|---:|---:|---:|
| 1 | `SH EF 630 x 560 mm - K150/M125/M125` | `null` | `sheet` | 125 | 50 | 0 | 6250 |
| 2 | `SH EF 1200 x 1020 mm - K125/M125/M125` | `null` | `sheet` | 62 | 50 | 38 | 3138 |

Quantity revalidation is mandatory: `125 * 50 + 0 = 6250` and
`62 * 50 + 38 = 3138`. Serialize the quantity values according to the current
harness-native decimal-string schema; this table records approved arithmetic,
not JSON number types. The technical unit is exactly `sheet`. `lembar` and
`sheet EF` are ineligible in that field. Other required receipt and item fields
must follow the current closed schema and their previously approved facts;
missing values or ambiguity stop regeneration rather than inviting a default.

## Selected retained evidence and source of truth

The selected manifest identity remains
`9801b5e4-453d-429a-b51f-e8ffaa17a2c9`. No new source may be selected.
Before regeneration, independently revalidate the current retained manifest
and original as real, regular, non-symlink files; validate the manifest against
the current repository schema; prove manifest filename/ID, status, media and
metadata relationships; recompute exact manifest byte size and SHA-256; and
recompute the stored original's size and SHA-256 against manifest and metadata.
Bind the exact canonical manifest reference, received UTC instant, MIME when
present, and actual optional Registry ID. A missing file, changed identity,
integrity failure, or unsupported metadata stops regeneration. This is a
future read-only evidence gate, not a revalidation claim by this document.

Construct the new approved input only from current repository schema truth,
that retained manifest and source metadata, the unchanged approved business
facts above, merged governance, and the current reviewed harness/input
contract. Do not derive new business facts from OCR, LLM output, filenames,
history, defaults, or inference. Do not contact PostgreSQL. The retained
manifest is the evidence identity, not permission to select a replacement.

## Canonical approved input and provenance

Use the current authoritative harness-native **closed** approved-input schema.
Validate every required and optional field, type, null, state relationship,
item order, quantity, unit, timestamp, and source binding before hashing.
Reject missing or extra keys and duplicate JSON keys. Canonicalize with
`ensure_ascii=False`, `sort_keys=True`, `separators=(",", ":")`, and
`allow_nan=False`, encoded as UTF-8. Semantic bytes contain no terminal LF;
transport bytes are exactly those semantic bytes plus one `0x0A` LF and no
additional bytes.

Regenerate `trusted_fact_provenance` against the exact current pointer set:
four receipt pointers (`supplier_name`, `document_number`, `document_date`,
`received_at`) and eleven pointers for each item index, including explicit
nulls. For two items the map has exactly 26 entries. The item fields are
`candidate_material_description`, `canonical_display_name`,
`size_description`, `specification`, `material_id`, `full_colly_count`,
`qty_per_full_colly`, `partial_qty`, `total_qty`, `unit`, and `line_number`.
Each pointer must carry only `EVIDENCE_DERIVED` or
`PROJECT_OWNER_APPROVED`, according to its actual support. No pointer may be
missing or added; no evidence-derived label may be inferred from a previously
approved fact without direct retained-evidence support.

Preserve merged PR #280 Model B exactly:

```text
approval.package_payload.evidence.registry_record_id
==
approved_input.ingestion_result.registry_record_id
```

This is exact JSON equality without coercion. A failed registration requires
`null` in both locations; a successful registration requires the same positive
integer in both. This is package cross-validation and does not establish an
external Registry row. No PostgreSQL query is authorized.

## Fresh approval and new frozen bindings

Create a **new** closed-schema approval record only during the later controlled
regeneration. It requires a new canonical UUIDv4 `approval_id`, an absolute UTC
microsecond-Z `approved_at_utc`, and `not_after_utc` exactly 604,800 seconds
later under the current merged policy; expiry is exclusive (`now <
not_after_utc`). A stale approval must be replaced by a separately approved
fresh package, not edited or extended. The Project Owner approval identity or
reference must be governed, bounded, and non-secret. The approval must bind
the retained evidence, approved facts and provenance, exact item order,
repository and harness identities, all package digests, and actual byte counts.
It must identify a fresh approval for new bytes, never assert continuity of
the unavailable old approval object.

The later regeneration must calculate and freeze these values from the actual
canonical objects:

1. approved-input semantic SHA-256 and transport SHA-256;
2. `trusted_facts_sha256` over canonical `trusted_receipt_facts` bytes, without LF;
3. `package_payload_sha256` over canonical approval `package_payload` bytes,
   without LF, avoiding self-hashing;
4. complete approval semantic SHA-256 and transport SHA-256, with the latter
   explicitly recorded in independent package-verification evidence if the
   approval schema has no transport-hash field;
5. actual input and approval semantic and transport byte counts.

The approval record itself uses the current closed wrapper and the same UTF-8
canonicalization rules, with exactly one transport LF. Cross-check every
embedded hash and count against independently computed values. New values are
expected. The old 1,327/1,328 and 3,549/3,550 counts are not targets and must
not be forced. The historical hashes must not be reused as new bindings.
Independent review must verify the exact private objects, schema,
canonicalization, provenance, evidence identity, arithmetic, hashes, counts,
and fresh owner approval before any binding amendment.

## Authority impact and separated prerequisites

PR #278's authority and its executor currently bind the unavailable old
package-specific hashes and byte counts. Regenerated bytes are **ineligible**
under those bindings. A separate narrow amendment, after independent package
verification, must update only the package-specific frozen bindings and must
receive independent review and human merge. This governance neither amends
those bindings nor permits an installer run.

The reviewed executor identity remains SHA-256
`bc9ad237ed3a35d763ee2e609712bda26c7f8b05742847789cc2f4b3bb88af0d`.
No executor code or semantic change is authorized here. The future amendment
must explicitly reconcile the executor's embedded package constants and
authority self-binding with the new package values while preserving that
reviewed executor identity unless a separately authorized executor change is
independently required. Do not silently claim that a change to embedded
constants preserves the SHA-256.

Runtime checkout synchronization and correction of the governed evidence
directory to mode `0700` remain separate prerequisite actions; neither occurs
here. Do not materialize anything under
`/run/aios/stage-0.33c-p4s5-source` until the regenerated package and new
approval exist, their hashes and byte counts pass independent review, the
authority binding amendment is merged, and materialization is separately
authorized. Do not create `authorization.json`, invoke the harness, create a
candidate, contact PostgreSQL, or install the package under this governance.

## Required sequence and stop rule

1. Publish this regeneration governance for independent review and human merge.
2. Perform controlled package regeneration and obtain the fresh approval.
3. Independently verify the new private package, hashes, byte counts, facts,
   provenance, and retained evidence binding.
4. Publish a narrow authority frozen-binding amendment; independently review
   and human-merge it.
5. Separately synchronize the runtime checkout and remediate evidence-directory
   mode to `0700`.
6. Separately authorize and perform private-source materialization.
7. Repeat P4S7 post-merge verification.
8. Publish execution-authority governance for separate review and human merge.
9. Only then consider exactly one runtime installation attempt under its
   independently verified authority.

Any failed gate stops progression. No stage may be collapsed. This document is
ready for independent review only; it is not approval to regenerate the package
before its own human merge, not an authority-binding amendment, and not Step 5
authorization.
