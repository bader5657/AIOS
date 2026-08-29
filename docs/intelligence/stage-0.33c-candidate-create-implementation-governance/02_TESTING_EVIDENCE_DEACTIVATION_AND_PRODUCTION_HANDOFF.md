# Testing, Evidence, Deactivation, and Production Handoff

## Required executable validation

PR #261 correctly disclosed that pytest was unavailable and not run in its
documentation workspace. That limitation is not acceptable for implementation
closure. The future implementation environment must execute and retain the
complete required test results without using production data or a production
network.

The three allowlisted unit files must prove:

- missing/disabled/malformed/expired authorization yields zero repository,
  credential, connection, persistence, confirmation, posting, inventory, and
  stock capability;
- invalid or caller-supplied actor attempts fail before mapping/persistence;
- invalid request type, ingestion evidence, manifest, approval binding, item
  count, quantity, unit, or facts digest fails before connection;
- eligible input calls the existing create function exactly once and propagates
  only the artifact-derived canonical actor;
- output is exact `ReceiptForReview`, receipt and all items are `NEEDS_REVIEW`,
  and confirmation fields are absent;
- no confirmation symbols (`MaterialReceiptService.confirm_receipt` or
  `MaterialReceiptRepository.confirm_receipt`) are called;
- no posting symbols (`InventoryPostingService.post_confirmed_receipt` or
  `InventoryPostingRepository.post_confirmed_receipt`) are constructed/called;
- no inventory or stock mutation path, event, task, or retry is invoked;
- successful authorization uses `O_EXCL | O_NOFOLLOW`; exact file creation is
  irreversible consumption before payload serialization or durability;
- the winner writes bounded JSON, flushes, file-fsyncs, and parent-directory-
  fsyncs before DB capability, with no post-create chmod/chown;
- a pre-existing safe regular file with governed owner/group and mode `0600`
  returns `AUTHORIZATION_CONSUMED` from metadata only, without content parsing;
- zero-byte, partial, or unfsynced safe records remain authorization `CONSUMED`
  while evidence quality may be `INCOMPLETE`;
- symlink, directory, socket, FIFO, device, unexpected type, wrong-owner, or
  wrong-mode state returns `AUTHORIZATION_CONSUMPTION_STATE_INVALID` before DB;
- a deterministic paused-winner test stops A after `O_EXCL` and before its first
  write; B must return `AUTHORIZATION_CONSUMED` with zero repository, connection,
  persistence, wait, and retry calls before A resumes;
- arbitrary bounded N same-authorization callers yield one winner and N-1
  metadata-only `AUTHORIZATION_CONSUMED` losers;
- a crash-after-claim test leaves an empty/partial marker; B and a simulated new
  process still classify authority consumed with DB connection zero;
- write, file-fsync, or parent-fsync failure after claim leaves the object, keeps
  authority consumed, starts no DB connection, and makes subsequent B consumed;
- no file lock, polling, wait, timeout takeover, stale-lock recovery, marker
  deletion, or retry exists;
- authorization disablement prevents new unclaimed calls while historical
  consumed records remain;
- evidence is bounded, sanitized, durably written before advance, and failure to
  initialize/write/flush/fsync evidence prevents or fails the operation safely;
  and
- secrets, environment contents, raw unrestricted facts, and credentials cannot
  enter logs, exceptions, or evidence.

## Isolated PostgreSQL 17 validation

The allowlisted integration test must run against isolated PostgreSQL 17 only
and prove with real constraints and privileges:

1. the exact candidate runtime-to-writer membership and absence of owner/admin
   authority;
2. one eligible request creates exactly one receipt and exactly N linked items,
   all `NEEDS_REVIEW`, in one `READ COMMITTED` transaction;
3. creator provenance equals the authorization-derived Actor A and cannot be
   replaced by caller or downstream data;
4. a failure on a later item rolls back the receipt and every earlier item;
5. repeated active-source creation returns `SOURCE_ACTIVE_RECEIPT_EXISTS` with
   no extra row using the lower governed persistence harness or independently
   valid test authorization identities, never one consumed authorization twice;
6. source-race testing yields one DB success and one bounded duplicate
   independently of the same-authorization `O_EXCL` contention test;
7. confirmation/posting state is unchanged and inventory/stock row counts and
   bounded fingerprints are unchanged;
8. reader, posting-only, and unrelated roles cannot create candidates, while the
   exact candidate runtime path can perform only its governed effects; and
9. no migrations, GRANTs, production endpoints, production data, or production
   network are used.

Required implementation evidence includes exact changed paths, commit identity,
test commands, exit codes, test counts/results, PostgreSQL version, static call
graph, activation-default proof, zero-capability matrix, transaction/rollback
evidence, role/privilege results, duplicate/concurrency results, non-escalation
results, and a bounded secret scan. The implementation record must not contain
production business payloads or credentials.

## Durable future execution evidence

The evidence module defines a sink protocol; implementation tests must use a
real durable-file test sink proving write, flush, and fsync ordering. It does not
create a production evidence directory. A later first-write package must bind an
exact persistent root, exclusive session directory, file identities/modes, and
final hashes.

For a future first production write, PASS/status-only evidence remains
insufficient. Bounded evidence must retain the request/correlation and session
identities, safe authorization/source/facts digests, governed actor
representation or digest, created candidate ID, `NEEDS_REVIEW` status, receipt
and item affected counts, confirmation/posting state, zero inventory/stock
effects, transaction result, runtime health, assertion payloads, and failure
classification. Unrestricted business payloads and raw secrets remain excluded.

## First-write separation and no escalation

Implementation PASS does not authorize activation. The mandatory sequence is:

```text
implementation governance review and merge
→ allowlisted implementation
→ implementation review and merge
→ isolated validation closure
→ separate first-production-write governance
→ exact approved real-business input
→ separately authorized first write
```

The future first-write authority must freeze the one attempt, exact executor,
commit, authorization-artifact bytes/hash/window, input source and safe digests,
operator identity, roles, transaction, expected one receipt plus N items,
forbidden effects, evidence root/session, post-write verification, consumption
boundary, rollback/failure behavior, and no automatic retry.

Telegram remains `OUT OF SCOPE`. No handler, command, routing, or sender identity
binding is authorized. Universal Ingestion remains evidence-only and must not
trigger candidate creation. HTTP, CLI, service registration, agents, and
background jobs also remain disconnected under this implementation contract.

## Architecture and final classification

No new external service or API is necessary for the internal/manual controlled
callable, so `ARCHITECTURE_DECISION_REQUIRED = NO`. Discovery that an external
service/API or any out-of-allowlist dependency is required is a hard stop and
requires new governance.

Project Owner approval is limited to allowlisted implementation after fresh
independent review and unchanged merge. No code implementation, production
authority, candidate write, synthetic data, runtime mutation, Telegram change,
confirmation, posting, inventory movement, or stock mutation is authorized by
this publication.

The next official action after publication is fresh independent review of this
governance PR. Production candidate activation remains **NOT AUTHORIZED**.
