# Transaction Contract

## Register

One register operation owns one Registry-local transaction: obtain connection,
begin, execute one complete parameterized insert, fetch the generated row,
commit on complete success, and roll back on persistence exception.

## Read

Read is one bounded operation under PostgreSQL default transaction semantics,
with no write lock or cross-component transaction.

## Update

One update owns one Registry-local transaction: parameterized update, return
the resulting row if found, commit on success, roll back on database error, and
return `None` when absent.

No transaction spans Storage, Metadata, Manifest creation, Asset Pipeline, or
external services. Registry rollback must not alter original/Manifest artifacts.
