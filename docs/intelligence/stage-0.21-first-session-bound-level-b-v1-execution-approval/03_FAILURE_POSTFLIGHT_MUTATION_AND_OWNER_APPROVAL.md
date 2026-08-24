# Failure, Postflight, Mutation Boundary, and Project Owner Approval

## Failure and deterministic closure

Any safety-gate failure, malformed output, schema failure, timeout, provider
failure/unavailability, accounting mismatch, overlap, source/config drift,
AIOS PID/restart drift, PostgreSQL failure, Telegram poller drift, RAM/swap/load
or disk violation, container OOM/restart, network-isolation drift, or runtime
mutation transitions the session immediately to `FAILED_CLOSED`.

After failure, admit no more requests, close the composition/client, finalize
the journal, perform no retry, and make no second attempt under this authority.
If request 1 fails, request 2 is prohibited.

After successful request 2, transition `ACTIVE_SYNTHETIC → STOPPING` and verify
the same AIOS `MainPID`, `NRestarts=0`, healthy PostgreSQL, exactly one Telegram
poller, clean unchanged source, running non-OOM non-restarted container,
unchanged `RestartCount`, safe RAM, session swap growth at most 64 MiB, safe
load and disk, unchanged network, exact request count 2, and exact provider
call count 2. Close the composition/client deterministically. Only a complete
pass may transition `STOPPING → CLOSED`; otherwise transition to
`FAILED_CLOSED` and finalize the journal accordingly.

## Mutation and exclusion boundary

The only permitted execution artifacts are one temporary `/tmp` harness and
one Level B session journal. Service restart, Docker/network/firewall changes,
model or resource-limit changes, forced unload, source changes, production
configuration changes, production startup changes, Universal Ingestion,
Level C, Memory, Specialist routing, business action, and all other runtime
mutation are prohibited. Production must remain unaffected.

## Project Owner approval

I, as Project Owner, authorize the first Stage 0.21 Session-Bound Level B v1
live staging session after governance activation.

Although the Level B v1 session model permits at most five requests or thirty
minutes, this first live session is deliberately limited to exactly two fixed
synthetic requests.

The session must use one Stage 0.19 composition, one client/provider lifecycle,
native warm reuse, per-request safety gates, at least sixty seconds between
request start timestamps, no retry, no fallback, 120-second timeout, exact
accounting, append-only exclusive journal evidence, and fail-closed semantics.

No third request, real user data, business data, production activation,
Universal Ingestion activation, Level C, Memory, Specialist routing, business
action, or runtime mutation is authorized.

Publication requires a normal governance-only PR into `main`, without force or
history rewrite. Publication performs no session execution or inference. After
merge and synchronized clean-main audit, authority activates as:

`STAGE 0.21 FIRST SESSION-BOUND LEVEL B V1 EXECUTION APPROVED — READY FOR FRESH SESSION PREFLIGHT AND TWO SYNTHETIC REQUESTS`

The next official action is a separate execution task that performs fresh
preflight and, only on full pass, runs the one authorized two-request session.
