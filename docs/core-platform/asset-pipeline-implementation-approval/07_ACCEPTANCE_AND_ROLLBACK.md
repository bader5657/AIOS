# Acceptance Criteria and Rollback

## Acceptance Criteria

Implementation is complete only if:

- it is a new contract-first implementation rather than restored history;
- the bounded orchestrator works for every approved input variant;
- Request Context and recognized identity are passed upstream-first;
- the result contains no more than the approved runtime transport surface;
- no persistent state machine or duplicate semantics exist;
- Stage 3 storage, metadata, Manifest, lifecycle, and failure semantics remain
  unchanged;
- Stage 4.1.1 authority and Stage 4.1.2 REPLACE disposition are satisfied;
- Registry/PostgreSQL and architecture expansion remain absent;
- all mandatory verification gates pass; and
- only the three runtime and five test paths listed in `03` change.

## Rollback Conditions

Rollback the scoped code/test implementation if:

- it requires or recreates the historical state model or signature;
- lifecycle, media, storage, metadata, Manifest, or failure behavior changes;
- any Stage 3 regression occurs;
- Registry/PostgreSQL or a new dependency direction appears;
- a canonical/domain Asset concept or new architecture becomes necessary;
- any ninth path is required; or
- any mandatory gate fails.

Rollback is code/test only. No database, production-data, migration, deployment,
or governance rollback exists. This approval and historical disposition remain
audit records.
