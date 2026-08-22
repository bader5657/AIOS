# Timeout and Malformed-Output Authority

## One timeout test

Authorize exactly one normal bounded synthetic request using the same runtime,
model, generation bounds, and resource controls. Set only the benchmark
client's deadline to `1 ms`. Concurrency remains one. The request is expected
to fail at the client timeout boundary; a client timeout is not a runtime
crash.

The harness must record that the timeout occurred, close or cancel the client
request, and perform no retry and no fallback. It must later map the benchmark
boundary outcome to `FailureCode.TIMEOUT`, while making no provider-adapter
implementation claim. Before proceeding, verify that bounded runtime work has
ceased and that the container is healthy, AIOS is active with `NRestarts=0`,
PostgreSQL is healthy, and exactly one Telegram poller remains.

## One malformed-output containment test

Authorize exactly one controlled synthetic schema/syntax stress case using the
existing runtime, model, schema, and resource ceilings. Production data,
tools, business actions, persistence changes, and permanent schema-authority
changes are prohibited.

Any malformed or schema-invalid result must be detected, rejected as
successful structured output, mapped to `FailureCode.MALFORMED_OUTPUT`, and
prevented from downstream use. Raw malformed content may be retained only as
benchmark evidence. Repair, coercion, fallback parsing, retry, or downstream
propagation is prohibited.

If the model instead returns perfectly valid output, record that outcome
honestly. Do not manufacture malformed model output. The controlled validator
containment evidence required by the existing Stage 0.6.4 authority must still
be preserved, and the runtime must remain healthy.
