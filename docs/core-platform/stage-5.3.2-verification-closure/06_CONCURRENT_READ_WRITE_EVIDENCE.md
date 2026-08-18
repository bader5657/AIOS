# Bounded Concurrent Read/Write Evidence

Connection A updated a row without committing. An independent Registry read on
connection B observed the last committed metadata/status and did not observe
the dirty values. After A committed, a later independent Registry read
observed the new committed values.

This proves the approved bounded `READ COMMITTED` behavior only.

`CONCURRENT SAME-ROW UPDATE POLICY = UNRESOLVED / NOT DEFINED BY STAGE 5.3.2`

`LOST-UPDATE PREVENTION = NOT AUTHORIZED`

No broader concurrency guarantee is claimed.
