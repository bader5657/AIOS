# READ COMMITTED Evidence

A real PostgreSQL transaction executed
`SHOW transaction_isolation` after setting the runtime-approved transaction
isolation and observed:

`read committed`

The runtime source remained unchanged and continues to issue
`SET TRANSACTION ISOLATION LEVEL READ COMMITTED` inside each bounded
operation.

No `SERIALIZABLE`, explicit locking, optimistic lock, or version field was
introduced.
