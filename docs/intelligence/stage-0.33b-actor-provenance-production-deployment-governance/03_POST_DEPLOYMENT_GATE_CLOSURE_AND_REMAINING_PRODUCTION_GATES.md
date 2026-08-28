# Post-Deployment Verification, Gate Closure, and Remaining Gates

## Separate read-only verification

The canonical sequence is **0.33B-G → 0.33B-P → 0.33B-A → 0.33B-D →
0.33B-V**: governance review and merge; separately authorized production
READ-ONLY preflight; separately reviewed and merged one-shot Migration 0005
execution authorization; exactly one controlled production Migration 0005
execution attempt; and separately authorized new-session READ-ONLY
post-deployment verification. No stage may be omitted, and a preflight PASS
cannot skip 0.33B-A.

After a successful COMMIT, 0.33B-V must separately authorize one bounded
read-only verification from a new PostgreSQL session independent from both the
0.33B-P preflight and 0.33B-D execution sessions. Reusing the execution
transaction/session as final proof is prohibited; the verifier must observe
already committed state. It must literally begin and configure the transaction:

```sql
BEGIN READ ONLY;
SET LOCAL TIME ZONE 'UTC';
SET LOCAL DateStyle = 'ISO, YMD';
SET LOCAL IntervalStyle = 'iso_8601';
SET LOCAL bytea_output = 'hex';
```

It may perform only SELECT, catalog reads, and bounded health/status inspection.
DDL, DML, `LOCK TABLE`, GRANT, REVOKE, repair, migration rerun, DOWN, and
activation are prohibited. Using the same fixed target, transport, canonical
representation settings, snapshot queries, and minimized evidence, it must
reverify:

- production container/PostgreSQL/database/schema health and identity;
- creator column, `text`, NOT NULL, no default, and exact named CHECK;
- absence of a provenance index and all unexpected schema objects;
- Stage 0.32 index structure, validity, readiness, uniqueness, sole key, and
  predicate;
- exact candidate-writer creator INSERT delta, runtime inheritance, absence of
  creator UPDATE, posting creator UPDATE, reader writes, membership/ADMIN
  OPTION/owner drift, and unrelated ACL drift;
- all four business-table counts and canonical digests against the locked
  execution baseline;
- owners, roles, memberships, triggers, functions, schemas/extensions,
  relevant relations, indexes, constraints, and other security/object state;
- runtime/service identity and configuration state; and
- unchanged Telegram, Universal Ingestion, confirmation/posting, OCR/Vision/
  LLM/Brain, and production activation state.

The harmless read-only transaction is then closed with `COMMIT;` or `ROLLBACK;`.
Neither close path may mutate production.

A mismatch is BLOCKED or INCONCLUSIVE and keeps the operational gate open. It
does not authorize mutation, retry, repair, DOWN, restart, credential rotation,
or activation.

## Actor-provenance operational gate

The gate closes only after all six requirements are recorded:

1. Stage 0.33A merged and verified;
2. 0.33B-G independently reviewed and merged;
3. 0.33B-P zero-row production preflight PASS;
4. 0.33B-A separately reviewed, merged, and ACTIVE;
5. 0.33B-D one-shot Migration 0005 deployment committed with every
   pre-COMMIT verifier PASS; and
6. 0.33B-V new-session READ-ONLY post-deployment verification PASS.

A 0.33B-P → 0.33B-D shortcut is prohibited.

Only then may governance classify:

```text
ACTOR-PROVENANCE OPERATIONAL GATE: CLOSED
```

Migration deployment alone is insufficient.

## Gates deliberately left open

Even after actor-provenance closure:

- **Runtime-secret rotation / activation safety: OPEN**;
- **Explicit production safety review: OPEN**; and
- **Production candidate activation: NOT AUTHORIZED**.

Stage 0.33B changes no runtime wiring, secret, service, Telegram or Universal
Ingestion behavior, confirmation/posting capability, or production traffic.

Publication classification:

```text
STAGE 0.33B ACTOR PROVENANCE PRODUCTION DEPLOYMENT GOVERNANCE APPROVED
— READY FOR INDEPENDENT GOVERNANCE REVIEW
— PRODUCTION PREFLIGHT NOT YET AUTHORIZED
— MIGRATION 0005 EXECUTION NOT AUTHORIZED
— PRODUCTION CANDIDATE ACTIVATION NOT AUTHORIZED
```
