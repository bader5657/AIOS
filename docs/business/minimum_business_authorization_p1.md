# Minimum Business Authorization P1

Implementation contract for the six points approved by the Project Owner in
the “OWNER APPROVAL — Minimum Business Authorization P1” conversation.
Base: `49bd23166556c13969814b65bb29092cb4f05b6d` (PR #324).
This document records the authorized development scope, not production
enrollment, activation, deployment approval, or a new Frozen P1 decision.

## Authority and identity

- Owner decisions approve scope. A PR approval authorizes the specified code
  change; neither it nor a Receipt grants business runtime authority.
- Telegram transport supplies numeric sender/chat identity. A username,
  RequestContext, forwarded message, or self-declared role never enrolls Owner.
- Administrative bootstrap is the trust root: an authorized administrator must
  verify control of the intended numeric Telegram ID via trusted Telegram
  evidence and an independently agreed, fresh challenge before enrollment.
  Record the raw numeric sender, private chat, nonce response, verification
  time, custodian, and immutable evidence location/hash. Screenshots or a
  user-supplied JSON alone are insufficient provenance.
- The bootstrap command does NOT authenticate evidence references. The
  administrator must validate their provenance before invoking it. This is an
  explicit external trust boundary, not a claimed automated verifier.
- Enrollment is one persistent PostgreSQL row, positive numeric ID, active
  status, evidence reference, activation-approval reference, administrator and
  time. No self-enrollment, username lookup, upsert, or automatic replacement.
- Capability activation requires both runtime configuration and active
  enrollment. Production enrollment/activation and deployment require separate
  Owner approval; this PR does not supply those approvals.

## Narrow user flow

Private chat with the bot, from the enrolled non-bot sender whose chat ID equals
the sender ID. Send ordinary text (not slash commands):

```text
catat_pelanggan {"name":"Ani","address":"Jalan 1","city":"Solo","notes":null}
```

The bot validates with CustomerDraft and returns the exact snapshot plus an
unguessable confirmation token. Send the provided `konfirmasi_pelanggan TOKEN`.
No Customer is saved before confirmation. Notes retain their original value;
unknown/duplicate JSON fields and oversized previews fail closed.

Each complete replacement message is a new draft. A newer invalid replacement
also cancels the old pending confirmation. Retried messages retain their
original token/expiry and cannot supersede newer messages. Editing the latest
draft message cancels its pending confirmation and requires a new message.
Telegram updates not yet delivered cannot be known: edit and confirmation
are ordered by their arrival/transaction lock. A commit already completed
before an edit arrives is not undone.

## Transaction and replay contract

- Every request uses a fresh non-autocommit READ COMMITTED transaction.
- Lock the singleton enrollment row, check current active numeric Owner, and
  serialize draft/confirmation operations. Revocation uses the same row lock.
- Confirmation is persistent, bound to Owner, private chat, original message ID,
  immutable validated snapshot, and exactly ten minutes from creation.
  Use database wall clock after acquiring locks; retries never extend expiry.
- A changed draft supersedes previous pending confirmation. Unknown tokens,
  wrong identity/chat, old message IDs, revoked Owner, and expiry cannot save.
- Confirmation first constructs Customer via CustomerApplication. Domain creates
  its single CustomerCreated event. Existing repository saves within the same
  connection. No domain event dispatch/outbox is introduced.
- Repository upsert is reused behind a create-only absence check under a Customer
  table write lock. This prevents an identity collision from overwriting a row,
  including competing writers. Table locking is acceptable for this single-owner
  minimum and is a documented throughput limitation.
- Customer, append-only audit row and confirmation consumption commit together.
  Recheck expiry in consumption after persistence/lock waits. Any error rolls
  back all three. Return success only after commit.
- Successful confirmation retries return the same Customer ID, even after TTL,
  but require the Owner still active. Unique token/audit/customer constraints and
  serialization prevent duplicate success from concurrent requests.
- Telegram delivery is outside the transaction. Failed delivery is retried using
  the same token; it must not create another Customer.
- Audit records action, numeric Owner/chat, Customer, confirmation, snapshot
  SHA-256 and database time. Runtime cannot update/delete/truncate audit.
  A database administrator can change schema/disable triggers; this is not a
  cryptographic claim of tamper-proof storage.

## Database privileges and administrative procedure

Apply migrations 0006 and 0007 as a schema administrator. Do not run production
migrations as part of development or tests. Create a separate runtime role
without superuser, CREATEROLE, schema ownership/membership or schema CREATE.
Grant only:
- USAGE on the application schema;
- SELECT, INSERT, UPDATE on customers (published repository uses upsert);
- SELECT and UPDATE(last_draft_message_id) on business_owner;
- SELECT, INSERT, UPDATE on customer_confirmations;
- SELECT, INSERT on customer_registration_audit.

Use a trusted, fixed search_path containing only administrator-controlled
schemas. Database login secrets remain environment configuration. The runtime
checks dangerous enrollment/audit privileges and refuses overprivileged roles.
Do not grant runtime membership in administrative roles.

After identity verification and separate environment-specific activation
approval, an authorized administrator runs the bootstrap command with a
separate administrative DSN, numeric ID, verification evidence reference and
Owner activation approval reference. It defaults to dry-run; `--apply`
is explicit. Do not put DSNs in command-line arguments or logs.
A duplicate bootstrap fails; replacement requires a separate reviewed process.
To revoke, an authorized administrator updates active=false; no Telegram
revocation or enrollment endpoint is added.

Runtime is disabled unless `AIOS_CUSTOMER_REGISTRATION_ENABLED=1` and
`AIOS_CUSTOMER_REGISTRATION_DATABASE_URL` is explicitly configured.
No production values or Owner IDs are committed.

## Reuse and limits

Customer, Draft, Application, domain event semantics, existing PostgreSQL
repository and generic Telegram ingestion remain the foundations.
New business messages terminate in the narrow application workflow; ordinary
messages retain the ingestion path. No IAM/RBAC framework, Receipt reuse,
generic policy engine, LLM interpretation, migration runner, or notification
subsystem is introduced. Telegram polling remains the existing trusted transport.
The transaction and adapter are synchronous/async boundary components respectively.

## Verification and gates

Unit policy and adapter tests plus disposable PostgreSQL integration cover
unauthorized users, group/bot/forwarded messages, edit/retry, TTL, revocation,
rollback, concurrent confirmation, persistent receipts, privilege boundaries,
audit mutation and collision protection. Existing domain/app/repository and
Telegram boundary regressions must remain green.

Run `scripts/verify_customer_registration_disposable.sh EXACT_HEAD_SHA`
from a trusted copy of the reviewed script on an isolated development/VPS
environment with Git, Docker and Python. It creates a new temporary checkout,
venv and disposable PostgreSQL container, records HEAD/blob hashes, test counts
and exit codes; no production configuration is used.

Merge gate: independent review and disk-based regression + disposable database
tests on the exact final head. In-memory unit results are supplemental only.
Production migration, runtime configuration and Owner activation remain separate
Owner-approved gates.
