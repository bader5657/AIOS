# Bounded Concurrency Scope

One bounded concurrent read/write test is authorized:

- connection A holds an uncommitted update;
- connection B reads under `READ COMMITTED` and observes the last committed
  value, not the dirty value;
- A commits; and
- a later independent read may observe the committed value.

`CONCURRENT SAME-ROW UPDATE POLICY = UNRESOLVED / NOT DEFINED BY STAGE 5.3.2`

`LOST-UPDATE PREVENTION = NOT AUTHORIZED`

Do not add optimistic locking, compare-and-swap, application locks, conflict
retry, versioning, or a same-row application guarantee. Serialization anomaly
claims are excluded. Deadlock injection is optional and is not a closure gate.
