# Failure and Preservation

Registry failure preserves Stage 5.4.1 behavior and prevents any event attempt.
If Registry committed but Event Engine returns bounded failure, the Registry
row, original, metadata, and Manifest remain intact.

No Event Engine outcome rolls back, deletes, updates, compensates, or retries
Registry work. No handler result opens a Registry transaction. Unexpected
programming/cancellation errors continue to follow existing runtime behavior
rather than being silently reclassified.
