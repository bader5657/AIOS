# Stage 0.33B-P Consumption, Classification, and Next Stage

## One-session consumption

This new authority permits exactly one future production preflight session after
activation. Before the production PostgreSQL session materially starts, it is
UNCONSUMED. Once that session materially starts, it is permanently CONSUMED
regardless of PASS, BLOCKED, INCONCLUSIVE, query/connection failure after
material start, or session completion. There is no automatic rerun.

Pre-connection source, content/hash, target, control-plane, or validation failure
does not consume authority. PR `#244` and PR `#245` remain independently and
permanently consumed.

## Full-preflight classifications

PASS requires corrected target identity, health, source and hashes, absent
Migration 0005 objects, exact Stage 0.32 index state, receipt count exactly zero,
all four comparable fingerprints, complete structural/object and role/ACL
snapshots, evidence minimization, and harmless READ ONLY close.

Only then classify:

```text
PRODUCTION ACTOR-PROVENANCE PREFLIGHT PASS
— CORRECTED PRODUCTION TARGET IDENTITY VERIFIED
— ZERO EXISTING MATERIAL RECEIPTS
— FULL PRESERVATION BASELINE CAPTURED
— ELIGIBLE TO REQUEST STAGE 0.33B-A ONE-SHOT MIGRATION 0005 AUTHORIZATION
```

If Z01 is positive, classify exactly:

```text
PRODUCTION ACTOR-PROVENANCE PREFLIGHT BLOCKED
— EXISTING MATERIAL RECEIPTS REQUIRE HISTORICAL PROVENANCE GOVERNANCE
```

Then STOP. No synthetic actor, backfill, nullable migration, row deletion,
rewrite/cancellation, or Migration 0005 execution is authorized. Any other
substantive mismatch is BLOCKED; unreliable evidence is INCONCLUSIVE. Neither
permits repair, surface expansion, or rerun.

## Continuing prohibitions and next stage

This package grants no Migration 0005 or 0004 execution, DDL, DML, lock,
ownership mutation, GRANT/REVOKE, role/membership/ACL normalization,
runtime/service or integration change, candidate activation, or production
business operation.

Only after a new full-preflight PASS may the Project Owner publish a separate
Stage 0.33B-A one-shot Migration 0005 execution authorization for fresh
independent review and merge. Preflight and migration authority must not be
combined. No execution is eligible before that separate authority activates.

## Publication production-safety record

| Control | Publication result |
|---|---|
| Production PostgreSQL contacted | NO |
| Production SELECT | NO |
| Production mutation | NONE |
| Ownership mutation | NONE |
| Roles/grants | UNCHANGED |
| Migration 0005 executed | NO |
| Migration 0004 executed | NO |
| `runtime.env` | UNCHANGED |
| Runtime service | UNCHANGED |
| Telegram | UNCHANGED |
| Universal Ingestion | UNCHANGED |
| Candidate activation | NO |

```text
STAGE 0.33B-P FRESH FULL PREFLIGHT REAUTHORIZATION PUBLISHED
— CORRECTED OWNERSHIP CONTRACT BOUND
— PREVIOUS AUTHORITIES REMAIN CONSUMED
— READY FOR INDEPENDENT AUTHORIZATION REVIEW
— FRESH FULL PREFLIGHT NOT YET EXECUTED
— MIGRATION 0005 EXECUTION NOT AUTHORIZED
— PRODUCTION CANDIDATE ACTIVATION NOT AUTHORIZED
```
