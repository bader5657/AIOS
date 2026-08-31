# Stage 0.33C-P3 Input, Output, Error, Secret, and One-Shot Contract

## Closed, reference-based input envelope

Step 3 selects no real values. A future input is one regular, non-symlink file
containing exactly one closed JSON object. Every object rejects duplicate,
unknown, and missing keys. No `extras`, extensions, arbitrary maps, or free-form
dictionaries exist.

Top level contains exactly:

| Key | Exact contract |
|---|---|
| `schema_version` | exactly `aios-stage-0.33c-one-shot-input-v1` |
| `ingestion_result` | exact object below |
| `trusted_receipt_facts` | exact object below |

`ingestion_result` is the fact-based projection sufficient to construct the
exact `IngestionResult` in `ControlledCandidateCreateRequest`:

| Key | Exact contract |
|---|---|
| `input_type` | exact `InputType`: `text`, `image`, `voice`, `document`, `pdf`, `doc`, `spreadsheet`, `video`, `audio`, `web_link`, `youtube_link`, or `unknown` |
| `recognized_input_type` | same closed vocabulary and compatible with `input_type` under the existing classifier |
| `stored_path` | exactly null |
| `manifest_path` | exactly 76 ASCII bytes: `/opt/aios/data/documents/manifests/` + canonical lowercase UUID + `.json` |
| `metadata` | exactly `{}`; no key permitted |
| `text` | exactly `""` |
| `register_handoff_ready` | exactly true |
| `process_handoff_ready` | exactly false |
| `route_handoff_ready` | boolean; true only if delivery succeeded |
| `respond_acknowledgement_ready` | exactly true |
| `registration_succeeded` | boolean |
| `registry_record_id` | null iff registration failed; otherwise integer 1–9,223,372,036,854,775,807 |
| `event_publication_attempted` | boolean; true only if registration succeeded |
| `event_delivery_succeeded` | boolean; false unless publication was attempted |
| `event_delivery_failure_code` | null unless attempted and failed; then `invalid_envelope`, `no_handler`, or `handler_failure` |
| `brain_result` | exactly null |

Empty `metadata` and `text` are fixed DTO-construction values, not payloads; the
candidate-input path does not derive its retained source from them. The only
retained-evidence input is the supported manifest reference. The existing
callable validates and hashes that retained manifest. No digest field is
invented because `IngestionResult` has none.

`trusted_receipt_facts` contains exactly:

| Key | Exact contract |
|---|---|
| `supplier_name` | nonblank canonical string, 1–128 Unicode scalar values |
| `document_number` | null or nonblank canonical string, 1–128 Unicode scalar values |
| `document_date` | null or valid `YYYY-MM-DD`, exactly 10 ASCII bytes |
| `received_at` | UTC `YYYY-MM-DDTHH:MM:SS.ffffffZ`, exactly 27 ASCII bytes |
| `items` | array of 1–500 exact item objects |

Each item contains exactly:

| Key | Exact contract |
|---|---|
| `line_number` | unique integer 1–500 |
| `candidate_material_description` | null or canonical nonblank string, 1–512 Unicode scalar values |
| `canonical_display_name` | null or canonical nonblank string, 1–512 Unicode scalar values |
| `size_description` | null or canonical nonblank string, 1–512 Unicode scalar values |
| `specification` | null or canonical nonblank string, 1–512 Unicode scalar values |
| `material_id` | null or canonical lowercase UUID, exactly 36 ASCII bytes |
| `full_colly_count` | integer 0–1,000,000 |
| `qty_per_full_colly` | null when count is zero; otherwise canonical decimal string, precision <=20, scale <=6, >0 and <=1,000,000 |
| `partial_qty` | canonical decimal string, precision <=20, scale <=6, 0–1,000,000,000 |
| `total_qty` | canonical decimal string, precision <=20, scale <=6, >0 and <=1,000,000,000 |
| `unit` | `sheet`, `pcs`, `kg`, `roll`, or `pack` |

Existing packaging-formula, integral-`sheet`, canonical-text, and DTO validation
remain mandatory. JSON numbers are rejected for decimal fields; strings parse
to finite `Decimal` values. The 128/512 character bounds are the narrowest
existing `TrustedReceiptFacts` bounds. Control/surrogate characters,
leading/trailing whitespace, blanks, and invalid dates, UUIDs, timestamps, or
decimals are rejected.

### Frozen decimal transport and grammar

These are all decimal-valued input fields; there is no generic unowned decimal
category:

| Field | Meaning | Precision | Scale | Minimum | Maximum | Negative | Zero | Occurrences |
|---|---|---:|---:|---:|---:|---|---|---:|
| `items[].qty_per_full_colly` | quantity in each full package | 20 | 6 | exclusive `0` when present | `1000000` | NO | NO | 0–500; null exactly when `full_colly_count == 0` |
| `items[].partial_qty` | unpackaged remainder | 20 | 6 | `0` | `1000000000` | NO | YES | 1–500 |
| `items[].total_qty` | total received quantity | 20 | 6 | exclusive `0` | `1000000000` | NO | NO | 1–500 |

All three are JSON strings. Let `I = [1-9][0-9]*` and
`F = [0-9]{0,5}[1-9]`. The sole lexical grammar is
`0|I|0\.F|I\.F`; the field-specific range, zero rule, precision <= 20,
and scale <= 6 in the table are additional mandatory predicates. Thus a
fraction has 1–6 digits and its last digit is nonzero. This grammar prohibits
negative values, leading zeroes, a leading plus, a bare decimal point,
trailing fractional zeroes, exponent notation, whitespace, NaN, Infinity,
hexadecimal, locale separators, and thousands commas. Examples accepted by
the applicable range are `0`, `1`, `1.5`, `1.25`, and
`999999999.999999`; examples rejected are `00`, `01`, `+1`, `1.`, `1.0`,
`1.500000`, `1e3`, `1E3`, `1,000`, and `-1`.

Canonicalization is fully ordered: (1) parse the JSON string to an exact
`Decimal`; (2) require it to be finite; (3) enforce the field's range and zero
rule; (4) enforce repository precision and scale; (5) render fixed-point form,
never exponent form; (6) remove trailing fractional zeroes; (7) remove the
decimal point when the fraction becomes empty; (8) normalize negative zero to
`0` before applying the non-negative field rule; and (9) require the result to
match the grammar and byte-match the input string. No rounding or quantization
is allowed. More than six fractional digits or precision beyond 20 rejects the
input.

Exact longest canonical spellings are:

| Field | Longest value example | Characters | JSON bytes including quotes |
|---|---|---:|---:|
| `qty_per_full_colly` | `999999.999999` | 13 | 15 |
| `partial_qty` | `999999999.999999` | 16 | 18 |
| `total_qty` | `999999999.999999` | 16 | 18 |

Those three independent examples cannot be added to an arbitrary maximum
`full_colly_count`. The invariant is
`total_qty == full_colly_count * qty_per_full_colly + partial_qty`; count zero
requires null per-colly quantity, and `sheet` requires integral quantities.
The jointly maximal numeric spelling is 48 unquoted characters per item. One
witness is count `100` (3), per-colly `999999.999999` (13), partial
`800000000.000001` (16), and total `899999999.999901` (16). It uses unit
`pack`; choosing the one-byte-longer `sheet` loses more bytes by forcing all
quantities integral. Counts with 4–7 digits reduce the available per-colly or
partial spelling so none exceeds 48. Line numbers are unique 1–500, so their
joint digit count is `9*1 + 90*2 + 401*3 = 1,392`, not `500*3`.

Raw image, PDF, DOC/DOCX, voice/audio, video, spreadsheet, or other document
bytes; base64 document content; arbitrary binary blobs; full retained-source
payloads; unbounded free text; and arbitrary metadata maps are prohibited. So
are passwords, database URLs, tokens, private keys, authorization bytes, and
environment values. If exact DTO construction cannot obey this projection
without an existing-interface change, implementation must block for separate
architecture/interface governance.

## Canonical serialization, size, and input identity

Semantic canonical bytes are UTF-8 JSON with lexicographically sorted keys,
separators exactly `,` and `:`, no insignificant whitespace, non-ASCII scalar
values emitted directly, and no LF. NaN, Infinity, duplicate keys, trailing
data, and alternate encodings are rejected. File transport is those bytes plus
exactly one LF. SHA-256 covers semantic bytes **without LF**. The file must
byte-match canonical serialization plus LF. Raw input is never echoed.

Canonical text rejects Unicode categories `Cc` and `Cs`, blank strings, and
leading/trailing whitespace. With `ensure_ascii=False`, an allowed astral
scalar is the actual worst case at four UTF-8 bytes. A quote or backslash costs
two bytes after JSON escaping; other permitted BMP scalars cost at most three.
Control characters cannot occur and therefore contribute no hypothetical
six-byte `\\uXXXX` expansion. JSON string quotes add two bytes per value.

The exact reproducible maximum is:

| Component | Occurrences | Max characters/value | Max encoded bytes/value | JSON syntax/key overhead | Subtotal |
|---|---:|---:|---:|---:|---:|
| top-level fixed fields (`schema_version` value) | 1 | 34 | 36 | 64 (3 keys/colons, 2 commas, outer braces) | 100 |
| `IngestionResult` fields, jointly valid failed-delivery registered state | 1 object | field-specific | 184 values total | 353 (16 keys/colons, 15 commas, braces) | 537 |
| `TrustedReceiptFacts` fixed values (two 128-scalar strings, date, timestamp) | 1 object | 128/128/10/27 | 1,069 total | 78 (5 keys/colons including `items`, 4 commas, braces) | 1,147 |
| per-item fixed structure | 500 | 11 fields | 0 | 206 each (keys/colons, 10 commas, braces) | 103,000 |
| per-item bounded text (four 512-scalar strings) | 2,000 | 512 | 2,050 | 0 | 4,100,000 |
| per-item UUID and longest jointly valid unit (`pack`) | 500 each | 36 / 4 | 38 / 6 | 0 | 22,000 |
| per-item decimals, jointly valid witness | 500 sets | 13 / 16 / 16 | 15 / 18 / 18 | 0 | 25,500 |
| `full_colly_count` in witness | 500 | 3 | 3 | 0 | 1,500 |
| unique `line_number` values 1–500 | 500 | 1–3 | 1,392 total | 0 | 1,392 |
| `items` array separators and delimiters | 1 array | — | 0 | 499 commas + 2 brackets | 501 |
| **semantic total** | | | | | **4,255,677** |

The `IngestionResult` row uses `spreadsheet` twice; a 76-character manifest
reference (78 quoted bytes); registered ID `9223372036854775807`; attempted but
failed delivery with `invalid_envelope`; and the longest jointly legal boolean
state. Summing the subtotals gives
`100 + 537 + 1,147 + 103,000 + 4,100,000 + 22,000 + 25,500 + 1,500 + 1,392 + 501 = 4,255,677`.
Therefore `MAX_SEMANTIC_INPUT_BYTES = 4,255,677` and
`MAX_TRANSPORT_INPUT_BYTES = 4,255,678`, the latter adding exactly one LF.

Validation order is frozen: raw byte-size cap; UTF-8 decode; exactly one JSON
document parse; duplicate-key rejection; closed-schema validation; field
validation; decimal canonical validation; exact DTO construction; canonical
reserialization; canonical semantic-byte bound; then SHA-256. The controlled
callable cannot be invoked before every stage succeeds.

## Callable-observable result contract

Repository truth: `controlled_create_review_candidate` returns
`ReceiptForReview`, whose fields are `receipt_id`, `supplier_name`,
`document_number`, `document_date`, `received_at`, `source_asset_reference`,
`status`, `version`, `confirmed_version`, `confirmed_at`,
`confirmation_actor_reference`, and `items` of `ReceiptItemView`. The safe
output subset is receipt ID, status, source reference, version, confirmed
version, and deterministic item count. Business text/dates/quantities,
material/item IDs, and actor reference are omitted.

Stdout is exactly one canonical JSON object plus LF with this closed schema:

| Field | Exact contract |
|---|---|
| `schema_version` | exactly `aios-stage-0.33c-one-shot-result-v1` |
| `outcome` | `SUCCESS` or `FAILURE` |
| `receipt_id` | canonical UUID on success; else null |
| `status` | exact returned `ReceiptStatus` on success; else null |
| `source_manifest_reference` | exact returned reference on success; else null |
| `version` | returned nonnegative integer on success; else null |
| `confirmed_version` | returned integer/null on success; else null |
| `item_count` | returned tuple length, 1–500, on success; else null |
| `input_sha256` | 64 lowercase hex characters |
| `harness_sha256` | 64 lowercase hex characters |
| `exit_classification` | exact classification paired with `exit_code` |
| `exit_code` | one permitted integer |
| `error_classification` | null on success; otherwise one mapped closed-vocabulary failure code or `HARNESS_INTERNAL_FAILURE` |
| `message` | fixed safe closed-vocabulary message, never exception-derived |

Repository commit, Python identity/path/version, and callable symbol are
supervisor evidence. With input SHA, harness SHA, and the supervisor-computed
SHA-256 of complete result bytes including LF, they form Step 3's honest
first-write binding set. No self-referential `result_sha256` field exists. The
harness alone does not claim full authorization-evidence bindability.

The result must not invent `AuthorizationClaim.correlation_id`, authorization
ID/consumption time, actor claim, authorization path/marker state, transaction
classification, row effects, DB capability/connection details, repository
internals, or precise evidence events. These are not returned. No payload,
secret, exception text, SQL detail, environment value, or authorization content
is emitted.

## Harness result versus later evidence

The harness result is only the observable schema above. Later governance may
combine it with authorization-artifact metadata, marker evidence, bounded
DB-side verification, and supervisor facts without changing this schema. Step
3 changes no callable return, authorization interface, or application
interface. Later interface expansion requires separate governance.

## One-shot invariant

A private gate begins `UNUSED`, transitions irreversibly to `CLAIMED`
immediately before the sole call attempt, and never returns. A second attempt is
rejected before invocation. The process parses one envelope and makes zero or
one call. No retry, loop, batch, fallback, recursion, or second input exists.

## Repository-grounded error inventory and disjoint exit mapping

The current callable can expose these bounded repository families:

- `CandidateCreateControlError` from the authorization/consumption layer, with
  exactly `AUTHORIZATION_DISABLED`, `AUTHORIZATION_INVALID`,
  `AUTHORIZATION_EXPIRED`, `AUTHORIZATION_ACTOR_INVALID`,
  `AUTHORIZATION_BINDING_INVALID`, `AUTHORIZATION_CONSUMED`,
  `AUTHORIZATION_CONSUMPTION_STATE_INVALID`, and
  `AUTHORIZATION_DURABILITY_FAILED`.
- `CandidateInputError` from retained-ingestion/trusted-facts mapping, with
  exactly `INVALID_INGESTION_EVIDENCE`, `RETAINED_MANIFEST_INVALID`,
  `TRUSTED_FACTS_INVALID`, `LIMIT_EXCEEDED`, `DECIMAL_POLICY_INVALID`,
  `PACKAGING_FORMULA_INVALID`, and `ID_GENERATION_INVALID`.
- `ReviewApplicationError` from review orchestration, with every currently
  defined `ReviewFailureCode`: `ACTOR_REQUIRED`, `ACTOR_INVALID`,
  `ACTOR_UNAUTHORIZED`, `SOURCE_IDENTITY_INVALID`,
  `SOURCE_IDENTITY_CONFLICT`, `INVALID_REVIEW_REQUEST`,
  `CANDIDATE_OPERATION_FAILED`, `INTERNAL_FAILURE`, and
  `SOURCE_ACTIVE_RECEIPT_EXISTS`.

`ReviewApplicationError.candidate_code`, when present, is a current exact
`MaterialReceiptFailureCode`. The current create path can attach
`DATABASE_UNAVAILABLE`, `DATA_INTEGRITY_ERROR`, or
`SOURCE_ACTIVE_RECEIPT_EXISTS`; all map through their enclosing review code.
The terminal adapter quarantines raw `MaterialReceiptError` and all other
repository exceptions, so raw persistence exceptions are not callable-facing
governed types. The callable's exact-request `TypeError` is prevented by DTO
construction; if it nevertheless escapes the invocation boundary it is
unexpected and maps to 70.

| Code | Exact classification/source |
|---:|---|
| `0` | `SUCCESS`: callable returned `ReceiptForReview` and finalization succeeded |
| `10` | `AUTHORIZATION_OR_ACTIVATION_REJECTED`: exact `AUTHORIZATION_DISABLED` or `AUTHORIZATION_EXPIRED` only |
| `20` | `AUTHORIZATION_ALREADY_CONSUMED`: exact `AUTHORIZATION_CONSUMED` only |
| `30` | `AUTHORIZATION_STATE_INVALID`: exact `AUTHORIZATION_INVALID`, `AUTHORIZATION_ACTOR_INVALID`, `AUTHORIZATION_BINDING_INVALID`, or `AUTHORIZATION_CONSUMPTION_STATE_INVALID` only |
| `40` | `INPUT_VALIDATION_REJECTED`: harness parser/schema/field/decimal/canonical rejection; pre-call DTO-construction `TypeError`/`ValueError`; or `CandidateInputError` with any of its seven codes enumerated above |
| `50` | `CONTROLLED_APPLICATION_FAILURE`: `ReviewApplicationError` with any of the nine `ReviewFailureCode` values enumerated above; a valid optional `candidate_code` does not change this exit |
| `60` | `HARNESS_OUTPUT_OR_DURABILITY_FAILURE`: exact `AUTHORIZATION_DURABILITY_FAILED`, or harness-local stdout serialization, output-size, or finalization/durability failure |
| `70` | `HARNESS_INTERNAL_FAILURE`: unexpected sanitized internal exception |

Precedence is specific stable code first, stable exception class second, then
harness fallback: pre-call deterministic input failures -> 40; exact
`CandidateCreateControlError.code` -> 10/20/30/60; exact
`CandidateInputError.code` -> 40; exact `ReviewApplicationError.code` -> 50;
harness output/finalization -> 60; every other exception -> 70. Mapping stops
once. No message, substring, `repr`, traceback, or unfrozen type is used.

Exhaustiveness follows by enum cardinality: all 8 control codes map once
(2 to 10, 1 to 20, 4 to 30, 1 to 60); all 7 candidate-input codes map once to
40; all 9 review codes map once to 50. Consumed is code 20 only and cannot be
invalid-state code 30; parser/DTO and `CandidateInputError` paths are code 40,
whereas application/repository quarantine is `ReviewApplicationError` code 50;
unknown exceptions alone reach 70. Harness-local parsing occurs before the
call, while output/durability occurs after it, so neither is reclassified as a
controlled callable failure.

## Stdout, stderr, and sanitization

Stdout is at most **4096 bytes including LF**. Serialize to an in-memory bounded
buffer, verify full length, then make one write; partial JSON is prohibited. An
oversized normal result becomes a fixed valid bounded code-60 result. If fixed
finalization is impossible, stdout is empty, stderr may be exactly
`AIOS_STAGE_0_33C_HARNESS_BOUNDARY_FAILURE\n`, and exit is 70.

Stderr is empty for governed outcomes. The catastrophic ASCII line is exactly
42 bytes including LF; **42 bytes is the maximum**. No traceback, repr/message,
path, secret, or user-controlled value is written. Errors use enumerated
classifications and fixed safe messages only.
