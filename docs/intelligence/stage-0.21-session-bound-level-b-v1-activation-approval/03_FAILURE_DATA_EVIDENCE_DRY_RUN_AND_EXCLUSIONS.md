# Failure, Data, Evidence, Dry-Run, and Exclusion Policy

Malformed output, schema failure, timeout, provider unavailability or failure,
resource-gate failure, unsafe memory pressure, excessive swap growth, OOM,
container restart, AIOS PID/restart drift, unhealthy PostgreSQL, Telegram
poller drift, source/config drift, network exposure drift, runtime mutation,
or accounting mismatch immediately transitions the session to
`FAILED_CLOSED`.

Failure stops admission, closes the composition/client, finalizes the journal,
and permits no retry, fallback, automatic restart, or return to active. A
postflight failure produces `FAILED_CLOSED`, never `CLOSED`.

Level B v1 accepts only explicit operator/test synthetic text. Telegram
messages, real user-authored prose, customer/order/product or Registry data,
files, voice, images, business content, Memory, Specialist routing, and
business actions are prohibited. Privacy/DLP is therefore not a blocker for
v1, but becomes mandatory governance before any real-user eligibility.

Journal evidence is secret-free and metadata-bounded: session ID, request
number, UTC timestamp, correlation/request IDs, latency, success/failure code,
provider/model IDs, schema result, bounded resource snapshots, and state
transitions. Bounded synthetic input may be retained. Raw provider responses,
secrets, production content, and user content must never be retained.

Before any first live session, a no-provider dry-run must verify state
transitions, exclusive journal creation, append-only behavior, counter and
five-request enforcement, duration and spacing enforcement, fail-closed
behavior, accounting mismatch detection, cleanup, finalization, read-only
closure, and SHA-256 calculation. Dry-run artifacts must remain under `/tmp`
and must not use the live session journal root or call the provider.

Production `aios.service` and Universal Ingestion remain unchanged and
inactive for Level B. No persistent daemon, Telegram command, production CLI,
public endpoint, production fallback, runtime configuration mutation, model
operation, Docker/network/firewall mutation, Level C activation, or production
inference is authorized.
