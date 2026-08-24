# Session ID, Artifact, Journal, and Accounting Contract

## Session identifier

Every session ID must match exactly:

`stage-0.21-level-b-session-YYYYMMDDTHHMMSSffffffZ-<uuid4hex>`

The timestamp is the UTC session-start instant with six decimal digits and no
punctuation; `<uuid4hex>` is the 32 lowercase hexadecimal digits of a newly
generated UUIDv4. The corresponding regular expression is:

`\Astage-0\.21-level-b-session-[0-9]{8}T[0-9]{12}Z-[0-9a-f]{32}\Z`

The identifier is filesystem-safe, bounded, unique, immutable after
generation, recorded in the journal, and never derived from request or user
data.

## Authorized operational artifacts

Each future authorized session may create exactly:

1. one temporary operator harness under `/tmp`; and
2. one journal at
   `/opt/aios/runtime/intelligence/staging/level-b-sessions/<session_id>.jsonl`.

No persistent runtime flag, repository config, service file, production CLI,
or other per-session artifact is authorized. The journal target must be absent
and opened using exclusive-create, fail-if-exists semantics with owner-only
write access. If it exists, stop without choosing another identifier for that
attempt.

The shared journal directory does not exist at this approval baseline. This
governance publication does not create it. A first-session authority must
either explicitly authorize its one-time controlled creation with restrictive
permissions or establish it through a separately governed provisioning step.

## Append-only journal

While active, the journal is append-only JSON Lines. Every accepted state or
request event is one bounded complete JSON object, appended once and flushed.
Existing lines are never rewritten, deleted, truncated, reordered, or
replaced. The monotonic request counter starts at zero and increments exactly
once immediately before each admitted Brain boundary call. Provider and HTTP
call counters must reconcile with admitted requests; hidden calls are
prohibited.

At `CLOSED` or `FAILED_CLOSED`, append one final record containing final state,
request count, session duration, pinned source/config identity, production
preservation, container/network state, cleanup result, and final UTC timestamp.
Flush, make the file read-only, close it, and calculate SHA-256 by read-only
access. Never reopen it for modification.
