# Health, Operational Closure, and Remaining Gates

## Bounded external preservation checks

Without mutation, record before/after metadata sufficient to prove:

- `aios-postgres` remains the same running, healthy `postgres:17-alpine`
  production container with restart count zero/unchanged and the governed data
  mount;
- PostgreSQL remains 17.x;
- `aios.service` remains running with no Stage 0.32 restart;
- `runtime.env` file metadata remains unchanged without reading its values;
- Telegram and Universal Ingestion remain unchanged; and
- candidate, confirmation, and posting activation remain absent.

No restart, repair, configuration readout, secret emission, runtime wiring, or
traffic activation is authorized.

## Verification classifications

A mismatch in target, identity, environment, canonical calculation, or required
evidence is **POST-DEPLOYMENT VERIFICATION INCONCLUSIVE — STOP**. An index,
duplicate, business-preservation, or security/object mismatch is
**POST-DEPLOYMENT VERIFICATION BLOCKED** with its bounded reason. Verification
never authorizes repair, migration rerun, DOWN, reconciliation, or retry.

Exactly one post-deployment verification session is authorized after activation.
After that session completes or fails, this authority is consumed. A further
session requires new governance.

## Source-manifest idempotency closure

The source-manifest idempotency operational gate may close only if the one
read-only verification proves every condition:

1. production identity and health PASS;
2. the new partial unique index structure PASS;
3. the existing source index remains correct;
4. active duplicate groups equal zero;
5. all four counts equal the locked execution baseline;
6. all four canonical digests equal the locked execution baseline;
7. roles, memberships, ACLs, owners, triggers, functions, schemas, extensions,
   governed relations, and unrelated indexes are preserved;
8. service/runtime/Telegram/Universal Ingestion state is unchanged; and
9. candidate, confirmation, and posting activation is absent.

Only then may the verification classify:

```text
SOURCE-MANIFEST IDEMPOTENCY OPERATIONAL GATE: CLOSED
STAGE 0.32: OPERATIONALLY VERIFIED AND CLOSED
```

Until the separate verification succeeds, the gate remains OPEN.

## Gates deliberately left open

Stage 0.32 closure grants no production candidate traffic authority. These
remain independently OPEN:

- **DURABLE CANDIDATE-CREATION ACTOR PROVENANCE**;
- **RUNTIME-SECRET ROTATION / ACTIVATION SAFETY**; and
- **EXPLICIT PRODUCTION SAFETY REVIEW**.

Production candidate activation remains **NOT AUTHORIZED**.

Publication status: **STAGE 0.32 POST-DEPLOYMENT VERIFICATION AUTHORIZATION
PROPOSED — READY FOR INDEPENDENT AUTHORIZATION REVIEW / MERGE — PRODUCTION
POST-DEPLOYMENT VERIFICATION NOT YET EXECUTED — MIGRATION 0004 MUST NOT BE
EXECUTED AGAIN**.
