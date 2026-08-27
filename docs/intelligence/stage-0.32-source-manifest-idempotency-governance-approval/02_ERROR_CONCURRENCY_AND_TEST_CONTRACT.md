# Stage 0.32 Error, Concurrency, and Test Contract

## Error and exception-graph contract

The repository may observe a PostgreSQL unique violation internally. Before it
crosses the Stage 0.31B boundary, only bounded enum/value information may remain:

- `SOURCE_ACTIVE_RECEIPT_EXISTS` for the approved source-active conflict;
- existing bounded integrity outcomes for unrelated failures.

The outward exception graph must retain no Psycopg exception, SQL, repository,
configuration, DSN, password, connection, traceback locals, or infrastructure
object through `__cause__`, `__context__`, `__traceback__`, exception
attributes, nested exceptions, or exception groups.

## Concurrency and rollback

Two independent PostgreSQL transactions attempting the same manifest must yield
exactly one committed active receipt. The losing transaction must receive the
bounded duplicate outcome and roll back its receipt and all items. Movements and
stock remain unchanged. No retry, confirmation, posting, or movement creation
is permitted.

If the winner rolls back, the other transaction may proceed. If an active row is
terminalized before a later insert, replacement is allowed according to the
partial-index predicate.

## Required unit tests

Implementation tests must prove:

- first create succeeds;
- sequential active duplicate returns the bounded outcome;
- unrelated unique/integrity failures do not map to the duplicate outcome;
- active status matrix covers EXTRACTED, NEEDS_REVIEW, CONFIRMED, POSTED;
- REJECTED and CANCELLED replacement is allowed and history remains;
- no fact comparison or active-row overwrite occurs;
- source authority and Registry-ID independence remain intact;
- exception graphs are recursively credential-safe.

## Required disposable PostgreSQL tests

Using a fresh admitted PostgreSQL 17 target only:

- migration up, down, and up/down/up;
- exact partial-index predicate and preservation of the existing non-unique
  source index;
- same active source rejected, different source accepted;
- terminal replacement accepted;
- multiple terminal historical rows coexist;
- candidate restricted identity remains sufficient;
- stock and movements unchanged;
- no confirmation or posting authority.

## Mandatory real concurrency test

Use separate actual connections and transactions with synchronization sufficient
to exercise a real race. Assert exactly one success, exactly one
`SOURCE_ACTIVE_RECEIPT_EXISTS`, at most one active row, zero committed loser
items, and unchanged stock/movements. Mock-only concurrency evidence is
insufficient.

