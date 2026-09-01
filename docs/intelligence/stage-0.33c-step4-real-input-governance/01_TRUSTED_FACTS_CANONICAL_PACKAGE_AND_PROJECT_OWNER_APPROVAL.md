# Stage 0.33C-P4 Trusted Facts, Canonical Package, and Owner Approval

## Current DTO and trusted-fact truth

The later input must map without interface changes to
`ControlledCandidateCreateRequest(IngestionResult, TrustedReceiptFacts)` and to
the merged harness's exact closed JSON schema. Unknown keys and missing fields
are rejected. Harness transport keeps `stored_path: null`, `metadata: {}`,
`text: ""`, and `brain_result: null`; this is the governed payload-free
projection and does not copy retained content or manifest metadata into input.
Input/recognized media types and all registration/event state fields must be
supported by retained ingestion/registry evidence and must satisfy the harness
state relationships. They may not be guessed. The current exact media projection
is: PDF, DOC, and spreadsheet use `input_type: "document"`; web and YouTube
links use `input_type: "text"`; text, image, voice, video, and audio use the same
input and recognized value. `recognized_input_type` preserves the specific
recognized type. Values outside the current `InputType` vocabulary or inconsistent
with the retained manifest media type are ineligible.

The permitted trusted business facts are exactly:

- receipt: `supplier_name`, optional `document_number`, optional
  `document_date`, timezone-aware `received_at`, and `items`;
- each item: positive unique `line_number`; optional
  `candidate_material_description`, `canonical_display_name`,
  `size_description`, `specification`, and `material_id`; nonnegative
  `full_colly_count`; conditional `qty_per_full_colly`; `partial_qty`, positive
  `total_qty`, and governed `unit`.

`supplier_name` is canonical nonblank trusted text of at most 128 Unicode
scalars. Current candidate creation has no supplier-registry or supplier-master
foreign-key requirement; Step 4 must not invent one. Item creation is
primarily description-based. `material_id` is an optional UUID, not a mandatory
material-master binding. For first-write clarity, each selected item must have
at least one evidence-supported `candidate_material_description`,
`canonical_display_name`, or explicitly verified/approved `material_id`; this
is a conservative selection rule, not an interface change.

Item `line_number` is an integer from 1 through 500 and must be unique in the
input. Each optional description/specification field is either null or canonical
nonblank text of at most 512 Unicode scalars. `material_id` is null or a canonical
UUID. `full_colly_count` is an integer from 0 through 1,000,000.

The exact units are `sheet`, `pcs`, `kg`, `roll`, and `pack`. No other spelling
or free-form unit is allowed. `sheet` quantities must be integral.

## Provenance and no-silent-derivation rule

Every trusted fact, including each item field and explicit null, must have one
of exactly two provenance values in the approval record:

- `EVIDENCE_DERIVED`: directly and unambiguously supported by the selected
  retained evidence; or
- `PROJECT_OWNER_APPROVED`: explicitly supplied or confirmed by the Project
  Owner when evidence is absent or ambiguous.

Provenance is keyed by exact JSON Pointer into `trusted_receipt_facts`, including
item indices. No third class exists. The selected evidence identity fields are
system evidence bindings, not human business facts.

OCR assumptions, LLM guesses, supplier history, previous receipts, defaults,
quantity inference, unit inference, and business heuristics are prohibited.
Missing required facts block selection until the Project Owner explicitly
supplies and approves them. Optional null is itself an exact approved fact and
must have provenance.

## Quantity, packaging, and timestamp contract

Decimal values remain canonical JSON strings. They are finite fixed-point only,
with no exponent, leading plus, leading-zero ambiguity, trailing fractional
zero, trailing point, rounding, quantization, or float conversion. Precision is
20 and scale is at most 6. Current maxima are 1,000,000 for
`qty_per_full_colly` and 1,000,000,000 for `partial_qty` and `total_qty`.
`partial_qty` may be zero; `total_qty` must be positive.

The exact equation is:

`total_qty = full_colly_count * qty_per_full_colly + partial_qty`.

When `full_colly_count == 0`, `qty_per_full_colly` must be null. When it is
positive, `qty_per_full_colly` is required and positive. All selected values
must pass this equation and every DTO/domain check before Step 5 publication.

`document_date` is either null or an absolute ISO calendar date `YYYY-MM-DD`.
`received_at` is an absolute UTC instant in the harness's exact
`YYYY-MM-DDTHH:MM:SS.ffffffZ` form. Relative dates such as “today” and naive or
local timestamps are prohibited. The manifest's UTC RFC3339 `received_at` is a
separate retained-evidence fact; any receipt `received_at` relationship must be
explicitly evidence-derived or owner-approved, never silently equated.

## Conservative first-write selection

Although the DTO supports 1–500 items, the first-write selection is limited to
1–10 items and should prefer 1–3. More than 3 requires an explicit owner
justification in the approval record. More than 10 is ineligible and requires a
separate governance amendment. Prefer one clear retained receipt, simple units,
unambiguous quantities, and no unusual edge case. This is blast-radius
minimization, not permission to fabricate a simpler receipt.

The frozen constants are:

`MAX_STEP4_SEMANTIC_PACKAGE_BYTES = 86835`

`MAX_STEP4_TRANSPORT_PACKAGE_BYTES = 86836`

The exact operational input limit is therefore 86,835 canonical semantic bytes
and 86,836 bytes including its one LF. This supports every simultaneously valid
1–10-item input at the current field maxima and remains strictly below the
Step 3 harness ceilings of 4,255,677 and 4,255,678. The arithmetic is:

| Input component | Bytes |
|---|---:|
| Fixed/top-level subtotal | 1,784 |
| Ten item structures | 2,060 |
| Ten items × four maximum 512-scalar text values | 82,000 |
| Ten UUID/unit value sets | 440 |
| Ten jointly valid decimal sets | 510 |
| Ten unique three-digit line numbers | 30 |
| Array delimiters and nine separators | 11 |
| **Canonical semantic total** | **86,835** |
| Exactly one LF | **+1** |
| **Transport total** | **86,836** |

The witness remains jointly valid: ten unique line numbers in 491–500; four
maximum allowed astral-scalar strings and a canonical UUID per item; unit
`pack`; full-colly count `100`; and the already reviewed jointly valid decimal
spellings `999999.999999`, `800000000.000001`, and `899999999.999901`.
Text/identity maxima do not affect the packaging equation. The higher ceiling is
a validity/safety bound, not a size target; selection still prefers 1–3 small,
clear items. Any input exceeding it is ineligible even though the harness has a
larger bound.

## Canonical two-artifact approval package

The sensitive approved package is exactly two separately installed canonical
JSON files:

1. `approved-input.json`: the exact harness-native closed input envelope,
   compact/sorted UTF-8 with `ensure_ascii=False`, `allow_nan=False`, no
   duplicate keys, plus exactly one LF. Its semantic SHA-256 excludes LF. Its
   transport SHA-256 includes LF.
2. `approved-input-approval.json`: a compact/sorted UTF-8 approval record plus
   one LF. It contains no raw source content and does not itself go to the
   harness.

The approval record has a closed wrapper:

```text
{
  "schema_version": "aios-stage-0.33c-step4-approved-input-v1",
  "package_payload": {
    "approval_id": <canonical UUIDv4>,
    "approved_at_utc": <absolute UTC microsecond-Z timestamp>,
    "not_after_utc": <approved_at plus exactly 604800 seconds>,
    "project_owner_approval_reference": <canonical non-secret text, maximum 128 scalars>,
    "repository_commit": <40 lowercase hex>,
    "harness_sha256": "b9fc9fb22724184696eabf02525bcc0a626bdff5ce3943ed31ba2e21130f5cad",
    "python_path": "/opt/aios/runtime/venv/bin/python",
    "python_version": "3.12.3",
    "controlled_callable": "core.app.material_receipts.controlled_candidate_create.controlled_create_review_candidate",
    "evidence": {
      "manifest_reference": <canonical retained reference>,
      "manifest_id": <matching canonical UUID>,
      "manifest_sha256": <64 lowercase hex>,
      "manifest_size_bytes": <integer 0 through 4194304>,
      "represented_media_type": <current manifest enum>,
      "manifest_received_at": <the manifest instant normalized to exact UTC microsecond-Z>,
      "stored_original_size_bytes": <integer 0 through 9223372036854775807 or null>,
      "stored_original_sha256": <64 lowercase hex or null>,
      "mime_type": <exact supported metadata value, maximum 255 scalars, or null>,
      "registry_record_id": <integer 1 through 9223372036854775807 or null>
    },
    "trusted_facts_sha256": <64 lowercase hex from the current authorization binding algorithm>,
    "input_semantic_sha256": <64 lowercase hex>,
    "input_transport_sha256": <64 lowercase hex>,
    "input_semantic_bytes": <integer at most 86835>,
    "input_transport_bytes": <semantic plus one, at most 86836>,
    "item_count": <integer 1 through 10>,
    "trusted_fact_provenance": {<exact JSON Pointer>: <one provenance enum>},
    "more_than_three_items_justification": <canonical text, maximum 512 scalars, or null>
  },
  "package_payload_sha256": <SHA-256 of canonical package_payload bytes>
}
```

Angle-bracket terms are type placeholders, not approved values. The wrapper,
`package_payload`, and `evidence` object are closed; no unlisted key is allowed.
The provenance map contains exactly four receipt pointers plus eleven pointers
for every present item index, and no other pointer. Thus ten items produce
exactly 114 entries. The payload hash avoids impossible self-hashing: canonicalize only `package_payload` with
the same JSON rules and hash those bytes without LF. The separately recorded
approval-record SHA-256 covers the complete approval file including LF. The
future selection evidence must bind both artifact hashes.


### Exact approval-record size bound

The approval record has its own exact bound; it does not reuse the input limit:

`MAX_STEP4_APPROVAL_RECORD_SEMANTIC_BYTES = 13619`

`MAX_STEP4_APPROVAL_RECORD_TRANSPORT_BYTES = 13620`

At 10 items, the maximum canonical record assumes all optional evidence values
are present, the longest `youtube_link` media enum, 19-digit size/registry
integers, 128-scalar approval reference, 255-scalar MIME value, 512-scalar
justification, maximum four-byte allowed UTF-8 scalars, and all 114 provenance
values set to the longer `PROJECT_OWNER_APPROVED` enum.

| Approval-record component | Bytes |
|---|---:|
| Closed keys/syntax, fixed/scalar maxima, empty bounded-text contents, and empty provenance object | 1,684 |
| Maximum UTF-8 contents: approval reference 512, MIME 1,020, justification 2,048 | 3,580 |
| Exact 114-entry provenance map beyond its two braces | 8,355 |
| **Canonical approval-record semantic total** | **13,619** |
| Exactly one LF | **+1** |
| **Approval-record transport total** | **13,620** |

Null optional values and shorter item counts only reduce this result. The exact
future filesystem maxima are therefore 86,836 bytes for `approved-input.json`
and 13,620 bytes for `approved-input-approval.json`.

Project Owner approval must explicitly bind the exact retained evidence
identity/hash, every `PROJECT_OWNER_APPROVED` fact, all provenance entries, the
exact item order/list/quantities/units, manifest reference, item count,
repository commit, harness SHA, trusted-facts hash, input semantic/transport
hashes, payload hash, and approval-record hash. Any byte, fact, item, evidence identity, provenance,
unit, or quantity change invalidates approval. Silent correction, substitution,
or extension is prohibited.

Approval validity is exactly 604,800 seconds (seven days) from
`approved_at_utc`; `not_after_utc` is exclusive. Expiry requires a new bounded
selection validation and new Project Owner approval—never an edited or extended
record. Step 5 and Step 7 may impose shorter windows.
