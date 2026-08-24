# Journal, Postflight, Failure Policy, and Project Owner Approval

The new session journal must be append-only JSONL, flushed and `fsync`ed after
every event, and never rewrite earlier bytes. Its final record must contain
final state, request count, duration, frozen source/runtime identity, bounded
result summaries, safety result, production preservation, and cleanup result.
After the final append, flush, `fsync`, close once, compute SHA-256, and never
reopen it for mutation.

After successful request 2, transition `ACTIVE_SYNTHETIC → STOPPING` and verify
the same AIOS PID, `NRestarts=0`, healthy PostgreSQL, exactly one Telegram
poller, clean unchanged source, healthy non-OOM/non-restarted container,
unchanged `RestartCount`, safe RAM, swap growth no greater than 64 MiB, safe
load and disk, unchanged network, and exact request/provider/HTTP accounting.
Close the composition/client deterministically. Only a complete pass permits
`STOPPING → CLOSED`; otherwise transition immediately to `FAILED_CLOSED`.

Any failure admits no further request, permits no retry, fallback, alternate
ID, or second session, and finalizes the journal fail-closed. Successful totals
are projector 2, mapper 2, Brain 2, provider 2, `/api/chat` 2, request counter
2, retry 0, and fallback 0.

Authorized operational artifacts are one temporary `/tmp` harness, one new
session journal, and bounded privileged pre-session evidence. Source changes,
service restart, Docker/network/firewall mutation, model pull/unload,
production configuration change, real user data, business data, production
activation, Universal Ingestion, and Level C are prohibited.

## Project Owner approval

I, as Project Owner, authorize one new Stage 0.21 first Session-Bound Level B
v1 attempt after the accepted zero-inference preflight failure.

The previous FAILED_CLOSED session remains immutable and consumed.

For the new attempt, interactive privileged read-only network inspection must
complete successfully before any session ID, session journal, composition, or
request is created.

Only after that deterministic PASS may one new session execute exactly two
fixed synthetic requests under the previously frozen Level B v1 safety,
spacing, resource, accounting, no-retry/no-fallback, and fail-closed controls.

No third request, second session, real user data, business data, production
activation, Level C, or runtime/network mutation is authorized.

Publication requires a normal governance-only PR into `main`, without force or
history rewrite. Publication executes no operational phase. After merge and a
synchronized clean-main audit, authority activates as:

`STAGE 0.21 FIRST SESSION REAUTHORIZED — READY FOR OPERATOR PRIVILEGED PREFLIGHT THEN NEW TWO-REQUEST SESSION`

The next official action is a separate operator-controlled execution task. It
must begin with Phase 0 interactive privileged read-only inspection and stop
without creating a session if that inspection is not determinately `PASS`.
