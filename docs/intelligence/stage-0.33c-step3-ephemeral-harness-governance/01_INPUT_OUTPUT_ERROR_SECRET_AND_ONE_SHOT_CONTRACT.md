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

The exact maximum file size is **4,259,775 bytes**, replacing the prior limit. The
contract calculation uses 500 items; four 512-character fields per item and two
128-character receipt fields at four UTF-8 bytes per scalar; every fixed key,
separator, longest enum, maximal bounded integer, UUID, timestamp, and decimal
spelling; and one LF. This yields 4,259,774 semantic bytes plus one LF. It cannot
honestly be low hundreds of KiB: the current DTO permits 500 x 4 x 512 Unicode
characters. A smaller text contract requires separate governance.

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

## Disjoint exit mapping and precedence

| Code | Exact classification/source |
|---:|---|
| `0` | `SUCCESS`: callable returned `ReceiptForReview` and finalization succeeded |
| `10` | `AUTHORIZATION_OR_ACTIVATION_REJECTED`: exact `AUTHORIZATION_DISABLED` or `AUTHORIZATION_EXPIRED` only |
| `20` | `AUTHORIZATION_ALREADY_CONSUMED`: exact `AUTHORIZATION_CONSUMED` only |
| `30` | `AUTHORIZATION_STATE_INVALID`: exact `AUTHORIZATION_INVALID`, `AUTHORIZATION_ACTOR_INVALID`, `AUTHORIZATION_BINDING_INVALID`, or `AUTHORIZATION_CONSUMPTION_STATE_INVALID` only |
| `40` | `INPUT_VALIDATION_REJECTED`: parser/schema rejection, DTO construction `TypeError`/`ValueError`, exact `CandidateInputError`, or governed business-input validation before persistence |
| `50` | `CONTROLLED_DOMAIN_OR_PERSISTENCE_FAILURE`: exact governed domain/application/persistence failure after eligibility, including `MaterialReceiptError` and implementation-review-frozen bounded types |
| `60` | `EVIDENCE_OR_OUTPUT_DURABILITY_FAILURE`: exact `AUTHORIZATION_DURABILITY_FAILED` or harness-local result/evidence finalization failure |
| `70` | `HARNESS_INTERNAL_FAILURE`: unexpected sanitized internal exception |

Precedence: (1) parser/DTO failures before call -> 40; (2) attempted call's exact
`CandidateCreateControlError.code` -> 10/20/30/60; (3) exact allowlisted
governed types -> 40 for business-input validation or 50 after eligibility;
(4) finalization failure -> 60; (5) unmapped exception -> 70. Mapping stops once.
No message matching or fallback reclassification exists. Codes 10 and 40 never
overlap. Any proposed class not distinguishable by exact type/code must be
merged into a deterministic parent class before approval.

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
