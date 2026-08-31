# Stage 0.33C-P3 Input, Output, Error, Secret, and One-Shot Contract

## Closed input-envelope schema

Step 3 selects no real values. A future separately governed artifact must be a
regular non-symlink file, 1–8,388,608 bytes, containing one strict JSON object
with no duplicate or unknown keys and these top-level keys only:

| Key | Contract |
|---|---|
| `schema_version` | exact `aios-stage-0.33c-one-shot-input-v1` |
| `session_id` | 1–128 safe ASCII characters matching `[a-z0-9][a-z0-9._-]{0,127}` |
| `ingestion_result` | exact reconstruction fields below |
| `trusted_receipt_facts` | exact governed facts fields below |

`ingestion_result` contains exactly the `IngestionResult` field names:
`input_type`, `recognized_input_type`, `stored_path`, `manifest_path`,
`metadata`, `text`, `register_handoff_ready`, `process_handoff_ready`,
`route_handoff_ready`, `respond_acknowledgement_ready`,
`registration_succeeded`, `registry_record_id`,
`event_publication_attempted`, `event_delivery_succeeded`,
`event_delivery_failure_code`, and `brain_result`. Enum values use their exact
string values. `brain_result` must be null. All other values must satisfy the
merged `IngestionResult` and candidate-input validation without coercion.

`trusted_receipt_facts` contains exactly `supplier_name`, `document_number`,
`document_date`, `received_at`, and `items`. Each item contains exactly
`line_number`, `candidate_material_description`, `canonical_display_name`,
`size_description`, `specification`, `material_id`, `full_colly_count`,
`qty_per_full_colly`, `partial_qty`, `total_qty`, and `unit`. Dates use
`YYYY-MM-DD`, timestamps are timezone-aware ISO 8601 strings, UUIDs are
canonical lowercase strings, and decimal quantities are canonical finite
base-10 strings. The harness performs explicit parsing and constructs exact
DTO types; it does not add actor or status data.

No supplier, document, item, quantity, retained-evidence reference, or other
production value is frozen here. The envelope must contain no DB password,
`DATABASE_URL`, token, private key, authorization bytes, or environment value.

## Canonical serialization and identity

Canonical input bytes are UTF-8 JSON produced with lexicographically sorted
object keys, no insignificant whitespace, `,` and `:` separators, non-ASCII
characters emitted directly, JSON numbers rejected for decimal fields, and one
terminal LF. NaN, Infinity, duplicate keys, trailing bytes, and alternate
encodings are rejected. Re-serialization must byte-match the artifact before
its lowercase SHA-256 is accepted. The command's expected digest must match.

The same canonical rule applies to the result envelope. This makes input and
result bytes deterministic and hashable. Future authority can bind the exact
input SHA-256, result-schema version, repository commit, harness source SHA-256,
interpreter path/version, and exact entrypoint symbol.

## One-shot state machine

Within one process, a private invocation gate begins `UNUSED`, transitions to
`CLAIMED` immediately before the sole controlled-call attempt, and never
returns to `UNUSED`. Any second attempt is prohibited even if the first raises.
The program parses exactly one envelope and performs zero or one controlled
call. There is no loop, retry, batch, fallback, recursive entry, or second
input. After emitting at most one bounded JSON result record it exits.

Missing/invalid authorization is normalized before any repository capability
is reached by the merged callable. The harness does not pre-read authorization
bytes or marker state and cannot weaken successful authorization consumption.

## Bounded result and evidence fields

Stdout is exactly one canonical JSON object plus LF, at most 4096 bytes, and no
other output. Its closed schema is:

- `schema_version`: exact `aios-stage-0.33c-one-shot-result-v1`;
- `result_classification`: `CREATED`, `REJECTED`, or `FAILED`;
- `session_id` and `correlation_id`;
- `candidate_id` or null and `candidate_status` or null;
- `receipt_row_effect`, `item_row_effect`, `confirmation_effect`,
  `posting_effect`, `inventory_effect`, and `stock_effect`;
- `transaction_classification`: `COMMITTED`, `ROLLED_BACK`, or
  `NOT_ATTEMPTED`;
- `authorization_classification`: `CLAIMED`, `CONSUMED`, `INVALID`, or
  `NOT_ATTEMPTED`;
- `durability_classification`: `COMPLETE`, `INCOMPLETE`, or `NOT_ATTEMPTED`;
- `db_capability_attempted`;
- `input_envelope_sha256`, `harness_source_sha256`, `repository_commit`,
  `result_envelope_sha256`, `python_interpreter`, and `entrypoint_symbol`;
- `error_classification` or null and the exact governed `exit_code`.

`result_envelope_sha256` is computed over the canonical object with that field
set to null, avoiding self-reference; the emitted object then carries the
digest. No raw business payload, actor reference, paths other than the frozen
interpreter, exception text, SQL detail, authorization payload, environment
data, or secret is emitted. Safe row effects and semantic classifications are
required; status-only output is insufficient.

Stderr is empty for all governed outcomes. If the harness cannot serialize its
bounded result, it may write only the fixed ASCII line
`AIOS_STAGE_0_33C_HARNESS_RESULT_UNAVAILABLE` and exit `70`. Tracebacks and
arbitrary exception strings are prohibited.

## Exact exit-code mapping

| Code | Classification |
|---:|---|
| `0` | governed success |
| `10` | pre-authorization or eligibility rejection |
| `20` | authorization already consumed |
| `30` | invalid, binding-invalid, actor-invalid, or consumption-state-invalid authorization state |
| `40` | input-envelope or business validation failure |
| `50` | bounded persistence or domain failure |
| `60` | authorization, marker, or result-evidence durability failure |
| `70` | harness/internal contract failure |

No other exit code is permitted. Exception types and merged bounded failure
enums must be mapped exhaustively; unknown exceptions become `70` without
exposing exception text.

The merged authorization codes map exactly: `AUTHORIZATION_DISABLED` and
`AUTHORIZATION_EXPIRED` to `10`; `AUTHORIZATION_CONSUMED` to `20`;
`AUTHORIZATION_INVALID`, `AUTHORIZATION_ACTOR_INVALID`,
`AUTHORIZATION_BINDING_INVALID`, and
`AUTHORIZATION_CONSUMPTION_STATE_INVALID` to `30`; and
`AUTHORIZATION_DURABILITY_FAILED` to `60`.
