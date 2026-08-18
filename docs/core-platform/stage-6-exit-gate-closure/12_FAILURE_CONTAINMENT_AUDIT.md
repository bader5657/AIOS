# Failure Containment Audit

- Invalid input returns `INVALID_ENVELOPE`, count zero, and invokes no handler.
- No matching handler returns `NO_HANDLER`, count zero, and is not silent success.
- Handler failure returns `HANDLER_FAILURE`, preserves only earlier completed
  count, stops remaining snapshot entries, and performs no retry or compensation.
- Later explicit invocations remain usable after prior bounded failures.

Handler isolation is limited to snapshot, sequential execution, failure-stop,
immutable event boundary, no parallel shared task, and invocation independence.
Completed side effects are not transactionally rolled back.
