# AIOS Intelligence Stage 0.33A — Package Control, Baseline, and Owner Decisions

## Classification

**STAGE 0.33A GOVERNANCE DECISION FROZEN — IMPLEMENTATION NOT YET AUTHORIZED**

This package publishes a repository-governance decision only. It does not authorize application implementation, Migration 0005 creation or deployment, PostgreSQL access or mutation, runtime configuration changes, service restarts, candidate traffic, privilege changes, Telegram or Universal Ingestion changes, or OCR/Vision/LLM/Brain invocation.

## Publication baseline

- Publication baseline branch: `main`
- Publication baseline commit: `32d2fb7134a3bec066816877582b34631881dc40`
- At branch creation, `HEAD`, local `main`, and refreshed `origin/main` were identical.
- At branch creation, the worktree contained no tracked or untracked changes.
- Stage 0.32 is operationally verified and closed.
- The Stage 0.32 source-manifest idempotency gate is closed and remains authoritative.
- Migration 0004 was deployed once and **must not be executed again**.
- Stage 0.33 architecture evaluation is complete.

## Scope of the frozen decision

Stage 0.33A freezes governance for durable creator provenance on production-created material-receipt candidates. The direct field is:

```text
public.material_receipts.created_by_actor_reference
```

The governed type is `TEXT`. The production-created candidate contract is `NOT NULL`. The canonical value is:

```text
operator:<lowercase-uuidv4>
```

The initial and only authorized actor class is `operator`. The existing `material_receipts.created_at` remains the authoritative creation timestamp.

The v1 design deliberately has no separate provenance relation, generic audit/event platform, new provenance timestamp, or provenance read API.

## Project Owner approval

The Project Owner explicitly approves and freezes:

1. the direct `created_by_actor_reference` column;
2. the operator-only initial actor class;
3. the canonical `operator:<lowercase-uuidv4>` representation;
4. the zero-row, fail-closed production policy for Migration 0005;
5. no provenance read exposure in v1; and
6. database-owner mutation remaining exceptional governance authority.

The Project Owner also approves these clarifications of the same frozen design:

7. the existing generic `ActorContext` contract remains broader and unchanged;
8. candidate creation applies a separate, operation-specific authorization policy requiring `operator:<lowercase-uuidv4>`;
9. production `DOWN` is prohibited without separately approved destructive rollback governance; and
10. database UUIDv4 enforcement may not be weakened without an explicit governance decision.

Items 7–10 clarify the application of the original six decisions. They do not expand the approved architecture or authorize implementation.

This approval grants governance-publication authority only. It does **not** grant implementation, migration-file creation, database deployment, privilege modification, runtime activation, or production candidate-traffic authority.

For avoidance of doubt, Stage 0.33A does not authorize Migration 0005 creation, production PostgreSQL contact, a Telegram identity resolver, runtime activation, or production candidate traffic.

## Open gates and non-authorized activity

The following gates remain open:

- **RUNTIME-SECRET ROTATION / ACTIVATION SAFETY**
- **EXPLICIT PRODUCTION SAFETY REVIEW**

Production candidate traffic is **NOT AUTHORIZED**. Production activation remains outside Stage 0.33B until other required gates close.

## Package contents

- `00_PACKAGE_CONTROL_BASELINE_AND_OWNER_DECISIONS.md`
- `01_ACTOR_IDENTITY_TRUST_AND_API_BOUNDARY.md`
- `02_SCHEMA_IMMUTABILITY_AND_MIGRATION_0005_POLICY.md`
- `03_TEST_SECURITY_AND_IMPLEMENTATION_GATES.md`

## Next official action

After governance review and merge, the next official action is a separate, explicit implementation authorization for the frozen contract. This package must not be treated as that authorization.
