# Session, Input, Route, Identifier, and Journal Contract

## Session scope and input

Generate exactly one session identifier with this format:

`stage-0.21-level-b-session-YYYYMMDDTHHMMSSffffffZ-<uuid4hex>`

Admit exactly these operator-controlled synthetic inputs, in order:

1. `Temperature stable and vibration within normal range.`
2. `System pressure is stable and motor temperature remains within normal range.`

No other text, Telegram data, user data, or business data is authorized.
Each request must call repository `project_text_semantics` exactly once. A
manual semantic substitute is prohibited.

For each request, use one prebuilt exact eligible `CoreRouteResult` with
`success=True`, `route_target=AIOS_BRAIN_BOUNDARY`, `failure_code=None`, and
`failure_reason=None`. Universal Ingestion and real AIOSCore routing remain
inactive.

Provenance is frozen as follows:

| Request | `input_reference` | `context_references` |
|---|---|---|
| 1 | `stage-0.21-session-request-1` | `()` |
| 2 | `stage-0.21-session-request-2` | `()` |

No reference lookup or dereference is permitted. Generate a unique normal
UUIDv4 correlation ID for each request; the two correlation IDs must differ.
`CoreToBrainMapper` remains the sole owner of Brain request IDs, and its two
request IDs must differ. Record all exact values in the journal. Stage 0.20
fixed identifiers must not be reused.

## Journal contract

Create exactly:

`/opt/aios/runtime/intelligence/staging/level-b-sessions/<session_id>.jsonl`

Use exclusive-create semantics. If that exact path exists, stop; no alternate
filename is permitted under this execution authority. Append only during the
session and flush plus `fsync` after every governed event. At finalization,
append the final record, flush, `fsync`, close, compute SHA-256, and thereafter
treat the journal as immutable governance evidence. Never overwrite or rewrite
prior entries.

The state machine is exactly:

`INACTIVE → PREFLIGHT → ACTIVE_SYNTHETIC → STOPPING → CLOSED`

Any failure transitions immediately to `FAILED_CLOSED`; reactivation is
prohibited.

