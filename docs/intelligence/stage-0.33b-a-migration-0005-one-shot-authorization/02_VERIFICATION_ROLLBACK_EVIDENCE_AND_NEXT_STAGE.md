# Stage 0.33B-A Verification, Rollback, Evidence, and Next Stage

## Pre-COMMIT structural and privilege proof

After the exact UP artifact executes but before COMMIT, PostgreSQL catalog proof
must establish:

- creator column present, type `TEXT`, NOT NULL true, and default none;
- exact named creator CHECK present with the reviewed UUIDv4/operator grammar;
- no new provenance index and unchanged Stage 0.32 index;
- candidate writer `INSERT(created_by_actor_reference)` yes;
- candidate creator UPDATE, posting creator UPDATE, and reader write all no; and
- roles/attributes, memberships, ADMIN OPTION, and owners unchanged.

No synthetic INSERT, business write, or privilege write-test is permitted.

## Preservation and rollback contract

ALTER TABLE, CHECK, and GRANT must remain in the same explicit transaction. If
any pre-COMMIT gate fails, ROLLBACK must remove the creator column, creator
CHECK, and creator-column INSERT grant. No partial schema or ACL delta may
persist.

Before COMMIT, freshly recompute the four canonical fingerprints and require
exact equality with the locked pre-DDL baseline. Migration 0005 must create zero
business rows. Compare the complete locked security/object state and permit only
the creator column, creator CHECK, and candidate-writer creator INSERT grant.
Owners, roles, memberships, ADMIN OPTION, triggers/functions,
schemas/extensions, relations, unrelated ACLs/indexes/constraints, and all other
objects must remain unchanged. Any data, security, or object difference requires
ROLLBACK and STOP.

Before COMMIT also require the same `aios-postgres` identity, running/healthy
state, unchanged restart count, normal PostgreSQL response, unchanged
`aios.service`, unchanged `runtime.env`, and absent candidate activation. Any
failure requires ROLLBACK and STOP.

COMMIT is permitted only if every source/authorization/evidence/target/health/
lock/prestate/index/zero-row/fingerprint/security/hash/DDL/structural/privilege/
preservation gate passes. There is no partial acceptance, warning-as-PASS, or
inferred evidence.

## Mandatory during-execution evidence retention

Stage 0.33B-D must not begin until a validated immutable, bounded, secret-safe
evidence destination is provisioned before production connection. Evidence must
be captured during execution without post-hoc reconstruction and retain:

- authority identity, reviewed authorization head, authorization merge commit,
  and current main;
- execution/session identity and timestamps;
- target/control-plane and exact command identity;
- Migration UP SHA;
- pre-DDL gate results, DDL result, pre-COMMIT verification, and data/security/
  object/health preservation results;
- COMMIT or ROLLBACK result;
- bounded post-COMMIT completion result, final classification, and evidence
  hashes.

The mechanism must not retain passwords, tokens, `DATABASE_URL`,
credential-bearing DSNs, `runtime.env` contents, private keys, raw unrelated
session context, or raw business rows. Failure to provision and validate this
mechanism is a pre-connection activation failure: do not execute; authority
remains unconsumed.

This mandatory during-execution retention rule also governs future production
preflight, deployment, and post-deployment verification sessions, including
Stage 0.33B-D and Stage 0.33B-V.

## Post-COMMIT completion and failure policy

After successful COMMIT, perform only the bounded execution-completion checks
already governed: same container identity, running/healthy state, unchanged
restart count, PostgreSQL responsive, `aios.service` unchanged, `runtime.env`
unchanged, Telegram unchanged, Universal Ingestion unchanged, and candidate
activation NO. This is not Stage 0.33B-V.

If COMMIT succeeded but completion health is FAIL or INCONCLUSIVE, authority
remains consumed: do not rerun Migration 0005, do not execute DOWN, and return
to governance.

## Remaining gates and production non-authority

After Stage 0.33B-D PASS, a separate newly published, independently reviewed
authorization must permit exactly one fresh Stage 0.33B-V `BEGIN READ ONLY`
production post-deployment verification session. The actor-provenance
operational gate remains OPEN through authorization and deployment and closes
only after Stage 0.33B-D PASS and Stage 0.33B-V PASS.

Migration deployment does not activate candidate creation traffic, Telegram
actor binding, Universal Ingestion provenance flow, confirmation, posting, or
any runtime feature. Production candidate activation remains independently
governed and unauthorized.

## Publication safety record

| Control | Publication result |
|---|---|
| Production PostgreSQL contacted / SELECT | NO / NO |
| Production mutation | NONE |
| Migration 0005 / Migration 0004 / DOWN | NOT EXECUTED |
| Ownership / roles / grants / memberships | UNCHANGED |
| Runtime / `runtime.env` | UNCHANGED |
| Telegram / Universal Ingestion | UNCHANGED |
| Candidate activation | NO |

```text
STAGE 0.33B-A MIGRATION 0005 ONE-SHOT EXECUTION AUTHORIZATION PUBLISHED
— REVIEWED STAGE 0.33B-PE EVIDENCE BOUND
— EXECUTION-EVIDENCE RETENTION REQUIRED BEFORE DEPLOYMENT
— READY FOR INDEPENDENT AUTHORIZATION REVIEW
— MIGRATION 0005 NOT YET AUTHORIZED TO EXECUTE
— PRODUCTION CANDIDATE ACTIVATION NOT AUTHORIZED
```
