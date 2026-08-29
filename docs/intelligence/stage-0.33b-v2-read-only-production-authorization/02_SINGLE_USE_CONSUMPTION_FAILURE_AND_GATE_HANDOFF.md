# Stage 0.33B-V2A Single-Use Consumption, Failure, and Gate Handoff

Date: 2026-08-29 (Asia/Jakarta)

## Activation and pre-launch gates

Independent review and unchanged merge of this authorization are necessary but
not sufficient to launch. Immediately before launch, a future executor must
verify synchronized clean source, exact bundle bytes and SHA-256, frozen nonce,
semantic-contract identity, the evidence-root type/ownership/mode, expected
container/runtime identity, unique-session exclusive initialization, and the
exact argv.

If any source, bundle, nonce, evidence-root, runtime, evidence initialization,
or semantic-contract check fails before launch: do not launch, do not repair,
and stop. The authority remains unconsumed.

## First-attempt consumption and failure

The first attempt to launch the governed production Docker/psql process
permanently consumes the authority, even if Docker, connection, psql, or stdin
fails. There is no retry, second connection, alternate argv, or automatic
repeat.

After launch, any frame, process, evidence, or semantic mismatch requires
`ROLLBACK` in the same read-only session if it remains alive, then immediate
stop. No repair or second connection is authorized.

The fresh V2 session must execute the complete bundle. Prior observations may
not be used to skip `I01/I02`, `S01`, `F01-F04`, `O01-O08`, `R01-R04`,
`V01-V05`, or `N01`. All 25 queries must execute within the new repeatable-read
current-state snapshot.

## Historical and operational handoff

Even after a future V2 PASS, original Stage V remains **FAILED**, its authority
remains **CONSUMED**, and historical Stage D semantic evidence remains
**PERMANENTLY INCOMPLETE**. No historical evidence is rewritten.

A future V2 PASS may make the actor-provenance operational gate **ELIGIBLE FOR
SEPARATE CLOSURE**. It does not close that gate and does not activate candidate
traffic. At authorization publication the gate remains **OPEN** and production
candidate activation remains **NOT AUTHORIZED**.

This package authorizes only one future read-only verification session after
all gates. It authorizes no migration, mutation, repair, runtime restart, or
production business traffic. Stage V2 is not executed by publication.
