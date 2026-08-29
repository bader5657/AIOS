# Stage 0.33B-V2A Authority Basis, Consumed Predecessor, and Owner Approval

Date: 2026-08-29 (Asia/Jakarta)

## Source and reviewed basis

This authorization package was cut from clean synchronized `main` at
`4b9bdfa43050c657e6fd868dc0568964ab62b902`. PR #256, PR #257, and PR #258
are merged and independently verified. PR #258 reviewed head
`7a2361637f3d45b1a322f040c2b063a8fbf6d33e` was merged as
`4b9bdfa43050c657e6fd868dc0568964ab62b902`.

Original Stage V remains **FAILED**. Its authority accounting is permanently
`authorized=1, consumed=1, remaining=0`. The new Stage V2 authority is not a
retry, resurrection, transfer, continuation, or reuse of that authority or its
PostgreSQL session. Migration 0005 remains **COMMITTED** and rerun is
**PROHIBITED**. Historical Stage D semantic evidence remains **PERMANENTLY
INCOMPLETE**.

## Distinct authority accounting

The Project Owner approves exactly one future Stage 0.33B-V2 production
verification session, read-only, after this authority PR receives independent
review, merges unchanged, source is synchronized, the evidence root is
verified, and every activation gate passes.

At publication the new Stage V2 accounting is `authorized=1, consumed=0`.
After independent review, unchanged merge, source synchronization, and all
activation gates, its accounting is `remaining=1`. This approval grants no
second session, alternate connection, migration, DDL, DML, DOWN,
GRANT/REVOKE, repair, runtime restart, or candidate activation.

The authority becomes permanently consumed at the first attempt to launch the
exact governed production Docker/psql process, including a Docker, connection,
psql, or stdin failure. After that attempt there is no retry, second connection,
alternate argv, or automatic repeat.

This publication itself launches nothing, contacts no PostgreSQL endpoint,
creates no session, and mutates no production or historical evidence.
