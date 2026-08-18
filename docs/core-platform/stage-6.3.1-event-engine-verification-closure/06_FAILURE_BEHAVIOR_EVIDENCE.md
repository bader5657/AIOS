# Failure Behavior Evidence

- Invalid non-envelope input returns `INVALID_ENVELOPE`, count zero, and invokes
  no handler.
- A valid envelope with no match returns `NO_HANDLER`, never silent success.
- A handler exception returns `HANDLER_FAILURE`, preserves the number of earlier
  completed handlers, and prevents later handlers from running.
- Complete successful delivery returns the exact completed count and null
  failure fields.

No failure path retries or compensates work.
