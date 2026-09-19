# AIOS Stage 0.33C-P4S7-R3B — Trusted-facts hash contract governance amendment

Classification: `P4S7_TF_A_HASH_GOVERNANCE_READY_FOR_REVIEW`.

## Scope and authority

This governance amendment selects exactly **MODEL TF-A — DTO-PROJECTION FACTS
HASH** to resolve the P4S7-R3A byte-domain conflict. It preserves the original
approval/authorization meaning of `trusted_facts_sha256`. Independent review
and human merge are required; this document is not execution authority.

Repository truth was checked at merged `main` commit
`c102b81cbbb0fd2c02fa66b8b4ebbb7a04864601` (PR #281). The authoritative DTO
definitions and validation are `TrustedReceiptFacts` and
`TrustedReceiptItemFacts` in
[`candidate_input.py`](../../../core/app/material_receipts/candidate_input.py).
The exact approval/authorization projection and serialization are
`trusted_facts_sha256`, `_item_value`, and `_decimal_text` in
[`candidate_create_authorization.py`](../../../core/app/material_receipts/candidate_create_authorization.py).
The latter is the current repository hash helper; the former supplies the
validated DTO contract. Any future equivalent must preserve these exact
semantics, not silently redefine the hash domain.

## Three distinct hash bindings

| Field | Authoritative byte domain and purpose |
| --- | --- |
| `trusted_facts_sha256` | SHA-256 of the canonical deterministic DTO projection of validated `TrustedReceiptFacts`; semantic facts approval binding for Project Owner-approved business facts. |
| `input_semantic_sha256` | SHA-256 of the exact canonical harness-input semantic bytes, covering the entire closed input object, without a transport LF. |
| `input_transport_sha256` | SHA-256 of the exact harness-input transport bytes: those semantic bytes followed by exactly one LF (`0x0a`). |

`trusted_facts_sha256` does **not** directly hash the raw
`trusted_receipt_facts` subobject bytes from the harness input. It and
`input_semantic_sha256` serve different purposes and must not be collapsed.

**One `trusted_facts_sha256` digest is sufficient for facts approval because
exact input bytes are separately bound by semantic/transport input hashes.**
No second facts digest is introduced. **TF-C is not adopted.**

## Exact DTO projection

The receipt projection contains exactly these five keys, including explicit
nulls for optional values:

| Receipt key | Projection rule |
| --- | --- |
| `supplier_name` | Validated string unchanged. |
| `document_number` | Validated string unchanged, or null. |
| `document_date` | Validated `date.isoformat()` string, or null. |
| `received_at` | Validated `datetime.isoformat()` string, with its default arguments. |
| `items` | JSON array of item projections in the DTO tuple's original order. |

Each item projection contains exactly these eleven keys:

| Item key | Projection rule |
| --- | --- |
| `line_number` | Validated integer unchanged. |
| `candidate_material_description` | Validated string unchanged, or null. |
| `canonical_display_name` | Validated string unchanged, or null. |
| `size_description` | Validated string unchanged, or null. |
| `specification` | Validated string unchanged, or null. |
| `material_id` | `str(UUID)` in canonical UUID form, or null. |
| `full_colly_count` | Validated integer unchanged. |
| `qty_per_full_colly` | `format(Decimal, "f")` string, or null. |
| `partial_qty` | `format(Decimal, "f")` string. |
| `total_qty` | `format(Decimal, "f")` string. |
| `unit` | Validated string unchanged. |

No extra fields, missing fields, omitted nulls, generated identifiers,
ingestion metadata, evidence, provenance, or approval metadata belong in this
projection. Sorted object keys do not permit sorting the items array.

## Timestamp and canonical serializer

The existing authorization helper calls `validated.received_at.isoformat()`.
For UTC DTO values this uses `+00:00`; with zero microseconds it omits the
fractional part, and with nonzero microseconds it emits six fractional digits.
The helper does not itself normalize timezones. The future mapping must create
an aware UTC datetime from the validated harness-native UTC timestamp.

For example, the synthetic harness lexical value
`2000-01-01T00:00:00.000000Z` maps to the DTO projection string
`2000-01-01T00:00:00+00:00`. A nonzero fraction such as `.123456Z` maps to
`.123456+00:00` at the same instant. These are representation changes only.
Do not substitute the harness-native six-digit-Z lexical form inside the
facts digest. Do not force `timespec="microseconds"` in place of the existing
default `isoformat()` behavior.

The exact existing facts hash serialization is:

```python
json.dumps(
    value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
).encode("utf-8")
```

SHA-256 is applied to those bytes and returned as lowercase hexadecimal.
There is no BOM, indentation, or transport LF. Dates, datetimes, Decimals and
UUIDs are converted as specified above before JSON serialization; nulls,
strings and integers retain their governed types. No float conversion,
Decimal rounding, quantization, normalization, or generic `default=str`
serializer may replace the existing helper contract.

The current facts helper does not explicitly pass `allow_nan=False`.
Its validated projection admits no floating-point values and rejects
non-finite Decimals before converting Decimals to strings. Existing harness
input and approval canonicalization uses `allow_nan=False` and must retain
it. Use `allow_nan=False` where supported by the repository helper contract;
do not introduce a second incompatible facts serializer or silently claim
that the current facts helper already passes that option. Any separately
reviewed helper hardening must preserve identical bytes for every valid DTO.

## Required deterministic input-to-DTO mapping

The future installer amendment must explicitly implement and test this order:

1. Parse and validate the closed harness-native input, including exact schema,
   canonical bytes, native timestamp syntax, field types, and value rules.
   Reject unknown or missing fields; do not repair invalid input.
2. Construct the authoritative DTO deterministically: copy strings, integers
   and nulls unchanged; parse `document_date` into a date; parse six-digit-Z
   `received_at` into an aware UTC datetime preserving every microsecond;
   parse a non-null `material_id` into a UUID; construct Decimal values
   directly from validated decimal strings without a float intermediate.
   Build `TrustedReceiptItemFacts` in input array order and place them in the
   `TrustedReceiptFacts.items` tuple. Run the authoritative DTO validation.
3. Compute `trusted_facts_sha256` through the existing authorization helper
   over that validated DTO and its exact projection.
4. Compare it with `approval.package_payload.trusted_facts_sha256`; mismatch
   must fail closed. Independently preserve the full-input semantic and
   transport hash checks and all other governed package validation.

No supplier, document field, received-at semantic value, item order,
description, material ID, unit, or quantity may change. Decimals must not be
rounded. Only representation changes required by the authoritative DTO
serialization are allowed. The mapper must not generate candidate IDs,
create a candidate, or invoke the harness to obtain this projection.

## Required future installer tests

The separately reviewed installer amendment must include tests proving:

1. Deterministic closed-input-to-DTO construction and the exact five receipt
   and eleven item fields, including nulls and original item order.
2. The governed `isoformat()` timestamp representation for zero and nonzero
   microseconds, including UTC `+00:00`.
3. Harness six-digit-Z timestamps map to the same semantic aware datetime
   with every microsecond preserved.
4. The DTO projection digest equals the approval facts hash using the
   authoritative helper; a wrong approval hash is rejected.
5. A direct raw-subobject digest differs where representation differs,
   demonstrating why that digest cannot replace TF-A.
6. The input semantic digest still binds the entire raw canonical
   harness-native input without LF, including its native timestamp spelling.
7. The input transport digest still binds the exact input bytes with one LF;
   missing or extra transport LF is rejected.
8. No business-value drift across projection, covering supplier, document
   fields, timestamps, order, all descriptions, UUIDs, units, quantities and
   Decimal precision/scale without rounding. Cover Unicode, optional nulls
   and invalid values as well as valid conversion paths.

These are future amendment requirements, not claims that an installer has
been repaired or that these tests have been executed by this governance PR.

## PR #278 installer impact and executor identity

Merged [PR #278](https://github.com/bader5657/AIOS/pull/278), merge commit
`4782aef7b6ab63aeccf3c2c813ce588b615173be`, introduced
[`one_shot_install.py`](../stage-0.33c-step4-one-shot-runtime-install-authority/one_shot_install.py).
Its current `validate_frozen_package` hashes the canonical raw
`trusted_receipt_facts` input subobject. That behavior is inconsistent with
TF-A. **A separate installer amendment is required.**

The current executor SHA-256 remains
`bc9ad237ed3a35d763ee2e609712bda26c7f8b05742847789cc2f4b3bb88af0d`.
It is considered superseded only after the installer amendment is separately
reviewed and merged. This governance PR changes no executor code, SHA,
package constants, runtime files, or installation authority and does not
declare the current executor TF-A compliant.

## Exact supersession of PR #281

Merged [PR #281](https://github.com/bader5657/AIOS/pull/281), merge commit
`c102b81cbbb0fd2c02fa66b8b4ebbb7a04864601`, states in
[`00_CONTROLLED_PACKAGE_REGENERATION.md`, “Fresh approval and new frozen bindings”, item 2](../stage-0.33c-p4s7-package-regeneration/00_CONTROLLED_PACKAGE_REGENERATION.md):

> `trusted_facts_sha256` over canonical `trusted_receipt_facts` bytes, without LF;

This amendment explicitly supersedes **only that conflicting direct
raw-subobject `trusted_facts_sha256` definition** with SHA-256 of the canonical
deterministic DTO projection of validated `TrustedReceiptFacts`, according to
the authoritative helper contract above, without LF. Other PR #281 controlled
regeneration governance remains unchanged, including Model B registry
cross-validation, provenance, retained evidence identity, fresh approval,
independent package verification, package-specific binding amendments, and
execution boundaries. This amendment is not a general waiver of PR #281.

## PR #282 block and required sequence

Open [PR #282](https://github.com/bader5657/AIOS/pull/282) remains blocked.
It must not merge until this governance amendment is merged, the separate
installer amendment is merged, PR #282 is amended to reference TF-A, and
PR #282 receives a fresh independent review. This task does not modify or
merge PR #282.

The official sequence is mandatory, with no collapsed gates:

```text
hash governance amendment
→ independent review
→ human merge
→ installer amendment
→ independent review
→ human merge
→ amend PR #282
→ fresh independent review
→ human merge
→ controlled regeneration
```

## Old package and future regeneration

The old unavailable package remains unavailable. This amendment does not
recover it, reconstruct its bytes, or retroactively claim that old bytes
satisfy the reconciled contract.

Only later, under the separately merged controlled regeneration authority,
may future regeneration compute the facts digest using TF-A. It must also
compute fresh input semantic SHA-256, input transport SHA-256,
`package_payload_sha256`, complete approval semantic and transport hashes,
and actual input and approval semantic and transport byte counts, each under
its respective domain. Package payload hashing remains over the canonical
payload without LF or self-hashing; approval transport retains exactly one
LF. Record approval transport evidence where the closed schema requires it.
Do not add a second facts digest or reuse historical hashes/counts as new
bindings. All other PR #281 verification and binding requirements remain.

## Privacy, non-actions, and disposition

This artifact contains no raw package JSON, OCR, retained image, credentials,
or secrets. No private sources are materialized and no package bytes are
regenerated. There is no installer execution, runtime change, PostgreSQL
contact, harness import or invocation, candidate creation, or
`authorization.json` creation. Step 5 is not authorized.

The known downstream blocker is the existing installer hash mismatch; it
requires the separate amendment and tests above before PR #282 can proceed.
Next official action: independent review of this narrow governance PR,
followed by human merge if accepted. No automatic merge is authorized.
