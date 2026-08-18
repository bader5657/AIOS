# Status Treatment

`registration_status` is nullable text and may persist only an already-approved
upstream registration status/disposition when one exists.

Stage 5.2.1 creates no status vocabulary, enum, default value, transition,
state machine, or status-specific CHECK constraint. Missing status must not be
fabricated. Exact status semantics remain unresolved until separate authority
establishes them.
