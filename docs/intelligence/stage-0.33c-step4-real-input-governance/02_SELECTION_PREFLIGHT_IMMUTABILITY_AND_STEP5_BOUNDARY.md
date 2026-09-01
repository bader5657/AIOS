# Stage 0.33C-P4 Selection Preflight, Immutability, and Step 5 Boundary

## Later selection workflow

A separately authorized real-data selection task must execute these gates in
order without invoking the harness or writing candidate state:

1. verify the selected repository commit is reviewed main and the harness bytes
   match SHA-256 `b9fc9fb22724184696eabf02525bcc0a626bdff5ce3943ed31ba2e21130f5cad`;
2. perform the bounded retained-evidence existence/integrity checks from
   document 00 for exactly one source;
3. construct the exact payload-free `IngestionResult` projection using only
   retained ingestion/registry facts;
4. resolve every trusted fact and explicit null with one allowed provenance;
5. enforce 1–10 items, bounds, units, canonical decimals, packaging equation,
   timestamps, uniqueness, closed schema, and the 86,836-byte input transport
   limit;
6. perform privacy/DLP and secret scanning before any approval;
7. execute a separately authorized, least-privilege, source-bound duplicate
   preflight and require active count zero;
8. canonicalize the two artifacts, calculate all hashes, and independently
   reproduce them, first rejecting every approval-record string that violates
   its exact field grammar or the shared `APPROVAL_SAFE_STRING` control, DEL,
   and surrogate exclusions;
9. obtain Project Owner approval of the exact package and hashes; and
10. install the two approved files only under separately reviewed filesystem
    authority, then verify metadata and bytes without invoking the harness.

A failure at any gate stops selection. No defaults, retries with changed facts,
or alternate source substitution are permitted under the same approval.

## Duplicate safety and mutable-state distinction

The existing database invariant is a unique active-source index on
`source_asset_reference`, active where status is not `REJECTED` or `CANCELLED`.
A conflicting controlled attempt yields `SOURCE_ACTIVE_RECEIPT_EXISTS`.

The future Step 4 selection preflight must be separately authorized and expose
only a count for the one bound manifest reference, semantically equivalent to:

```sql
SELECT count(*)
FROM public.material_receipts
WHERE source_asset_reference = $1
  AND status NOT IN ('REJECTED', 'CANCELLED');
```

`$1` is the already selected canonical manifest reference. The result must be
exactly zero. No row payload, supplier, document, actor, item, or broad receipt
listing may be returned. The query needs least-privilege read-only authority and
is not executed by this publication.

Duplicate state is mutable. A zero result at Step 4 does not guarantee Step 7
eligibility. Step 5 authority must bind a fresh duplicate check policy, and
Step 7 must revalidate immediately before the one controlled attempt. The
unique index remains the final concurrency guard. A changed state or
`SOURCE_ACTIVE_RECEIPT_EXISTS` stops without retry, source substitution, or a
second candidate attempt.

## Restricted runtime storage and installation

Real business values are prohibited from Git. The proposed exact future paths
are:

- `/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/approved-input.json`;
- `/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/approved-input-approval.json`.

Neither path is created by this package. Both final objects must be non-symlink
regular files, `root:aiosadmin`, and mode `0440`. `approved-input.json` is at
most 86,836 transport bytes; `approved-input-approval.json` is independently
bounded at exactly 13,620 transport bytes (13,619 semantic bytes plus one LF)
after exact safe-string validation. A separate filesystem
governance/installation task must verify the existing
non-symlink parent, absence of both final paths, and absence of staging debris;
create internally named same-directory staging files with `O_EXCL | O_NOFOLLOW`;
write bounded bytes; flush and file-fsync; install without overwrite; parent
fsync; and re-open without following symlinks to verify owner/group/mode/size
and SHA-256. Partial publication, overwrite, replacement, mutable correction,
and caller-selected staging names are prohibited. Failure must clean only exact
staging files and fail closed. The pair is usable only when both independently
verified files and all bound hashes agree.

Installation validation must reject rather than sanitize strings: C0 controls,
DEL, and surrogates are prohibited in bounded approval metadata, while each
UUID, hash, timestamp, enum, manifest reference, and software identity must
match its stricter closed grammar. The input file keeps its separately accepted
86,836-byte transport contract; this approval-record grammar does not alter the
harness-native input domain.

Because these files contain real business data, retention, deletion, recovery,
and post-use disposition also require separate governance. The existing
`authorization.json` and `consumed` contracts are not modified or repurposed.

## Step 4 closure and Step 5 boundary

Step 4 may close only after the later selection task proves:

- exactly one pre-existing retained source was selected and its identity,
  manifest, and any stored-original hashes were verified;
- all required trusted facts and explicit nulls were resolved with complete
  provenance;
- exact item order, values, quantities, units, equations, timestamps, DTO/domain
  validation, and operational size limits passed;
- candidate-bound duplicate preflight returned zero under separate read-only
  authority;
- canonical trusted-facts, input, payload, and approval-record hashes,
  repository commit, harness SHA, interpreter, callable, and item count were
  frozen;
- Project Owner explicitly approved the exact package before its seven-day
  expiry;
- privacy/DLP/secret scans passed; and
- no harness invocation, authorization artifact, candidate, or production write
  occurred.

Only after independent Step 4 closure review and unchanged merge may Step 5
become eligible. Step 5 is the separate publication of one first-production-
write authority. It must bind the exact unexpired Step 4 package, fresh mutable
preconditions, one operator identity, one authorization artifact contract, and
one attempt. This package does not create `authorization.json`, first-write
authority, or candidate state.

The seven-step sequence remains:

1. Step 1 — `CLOSED / VERIFIED`.
2. Step 2 — `CLOSED / VERIFIED`.
3. Step 3 — `CLOSED / VERIFIED`.
4. Step 4 — governance current; real selection and closure remain future work.
5. Step 5 — first-write authority, `NOT AUTHORIZED`.
6. Step 6 — independent authority review/merge.
7. Step 7 — exactly one bounded production write.

## Publication safety state

Project Owner authority in this task is limited to publication of this governance
package. It is not approval of any actual evidence, receipt, trusted fact, input
package, authorization, or production write.

Real evidence selected: `NO`.

Real business values committed: `NO`.

Production PostgreSQL contacted: `NO`.

Harness invoked: `NO`.

`authorization.json` created: `NO`.

Candidate created: `NO`.

Step 5 authorized: `NO`.

Candidate activation: `NO`.
