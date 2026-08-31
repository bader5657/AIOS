# Stage 0.33C-P3 Harness Scope, Architecture, and Identity

## Authority and source gate

This documentation-only package governs Step 3 and nothing else. Its reviewed
remediation baseline is PR #272 commit
`10b6bbfd9daef978a5c73a735677a36a61f9b928`. Step 1 and Step 2 are `CLOSED /
VERIFIED`; Step 3 requires this governance remediation and later implementation
review; Step 4 is **NOT AUTHORIZED**.

This publication does not implement or invoke a harness, select real supplier,
document, item, or retained-evidence values, create `authorization.json`, create
first-write authority, contact PostgreSQL, create a candidate, activate traffic,
or merge PR #272.

## Frozen architecture and path

The future caller is one ephemeral Python process with at most one invocation
of the controlled callable. It is non-daemon, non-service, and not permanently
installed as a CLI. It is not an HTTP or Telegram adapter, cron job, scheduler,
agent/tool registration, background worker, or Universal Ingestion callback.
It has no resident state, polling, loop, retry, batch, fallback, or second-input
surface. After one bounded result or failure it exits.

The exact future source path remains:

`core/app/material_receipts/stage033c_one_shot_harness.py`

It may be executed only from a separately reviewed immutable checkout as:

```text
/opt/aios/runtime/venv/bin/python -m core.app.material_receipts.stage033c_one_shot_harness --input-envelope <ABSOLUTE_PATH> --expected-input-sha256 <LOWERCASE_SHA256>
```

This is an ephemeral module invocation, not a registered console script. Input
path and digest remain placeholders for later governance; interactive stdin,
inline JSON, environment-selected input, and additional arguments are
prohibited.

## Runtime, source, and first-write identity

Future execution must use Unix identity `aiosadmin:aiosadmin`; root execution
and sudo inside or around the harness are prohibited. The exact interpreter is
`/opt/aios/runtime/venv/bin/python`, and runtime source/import root and working
directory are `/opt/aios-src`. Governance must bind and verify a clean reviewed
repository commit before execution.

Step 3 can provide an exact binding set of repository commit, harness-source
SHA-256, Python interpreter identity/path and version, canonical input-envelope
SHA-256, externally computed bounded result-envelope SHA-256, and controlled
callable symbol
`core.app.material_receipts.controlled_candidate_create.controlled_create_review_candidate`.
It does not claim that harness output alone binds authorization internals,
consumption evidence, or DB state; those are later execution evidence.

The harness imports the application capability only through
`core.app.material_receipts.controlled_candidate_create` and calls only
`controlled_create_review_candidate`. Imports solely for exact DTO construction
and bounded error enums are not alternate capabilities. Direct repository use,
direct SQL or DB access, connection injection, authorization-function calls,
consumed-marker manipulation, or authorization-file mutation are prohibited.

The request remains exactly `ControlledCandidateCreateRequest`, containing one
exact `IngestionResult` and one exact `TrustedReceiptFacts`. Its closed input
projection is frozen in `01_INPUT_OUTPUT_ERROR_SECRET_AND_ONE_SHOT_CONTRACT.md`.
It carries only a retained manifest reference and bounded facts: no raw/base64
source content, arbitrary metadata, actor, status, DB connection, credential,
authorization payload, retry policy, or repository.


The envelope contract in document 01 freezes the only three decimal fields
(`qty_per_full_colly`, `partial_qty`, and `total_qty`) as canonical JSON
strings, precision 20 and scale 6, with their repository-specific ranges and
packaging relationship. It freezes no-rounding normalization and the jointly
valid limits `MAX_SEMANTIC_INPUT_BYTES = 4,255,677` and
`MAX_TRANSPORT_INPUT_BYTES = 4,255,678`. These values replace the prior limits.

Callable error governance is likewise repository-grounded now: all 8 current
`CandidateCreateControlFailureCode` values, all 7 current
`CandidateInputFailureCode` values, and all 9 current `ReviewFailureCode`
values map exhaustively by exact code/type. Callable failures map only to exits
10/20/30/40/50: authorization consumption durability is callable-origin exit
30; six stable review validation codes are exit 40; and three remaining review
application/domain/persistence codes are exit 50. Exits 60 and 70 are
harness-origin only. No unfrozen exception, message-text matching, or raw
persistence exception mapping remains.

Repository truth is that the callable returns `ReceiptForReview`. The harness
may report only its explicitly allowlisted safe subset and deterministic
harness-local state. It may not infer `AuthorizationClaim.correlation_id`,
consumption timestamp, authorization/path state, hidden actor claims,
transaction/repository internals, DB details, row effects, or internal evidence
events. The callable return type and every existing application/authorization
interface remain unchanged. Any expansion requires separate governance.

## Authorization, credential, and marker boundary

The harness never creates, installs, edits, removes, chmods, or chowns
`authorization.json`. It relies only on the existing controlled callable's
fixed authorization boundary. When authorization is absent or invalid, the
callable fails closed before repository/DB capability. Installation remains a
later first-write-authority action.

The future artifact remains `root:aiosadmin`, `0440`; this package creates no
artifact. The harness must not touch the `consumed` directory or create/read
markers directly. Only the merged authorization implementation owns marker
state. The harness must not read, copy, print, accept, serialize, hash, or
persist `AIOS_MATERIAL_RECEIPT_CANDIDATE_DB_PASSWORD`, inspect `runtime.env`, or
dump its environment.

## No permanent registration

Implementation review must prove that nothing is added to packaging entrypoints,
systemd, cron, Telegram, HTTP routing, schedulers, agent/tool registries,
background workers, Universal Ingestion, or `/usr/local/bin`. No permanent
registration, service, installation, or production activation is authorized.
