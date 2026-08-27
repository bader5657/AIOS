# AIOS Intelligence Stage 0.33A — Authority Basis, Scope, and Owner Approval

## Classification

**STAGE 0.33A IMPLEMENTATION AUTHORIZATION PUBLISHED — IMPLEMENTATION NOT YET AUTHORIZED**

This package authorizes independent review of one bounded, future, non-production Stage 0.33A implementation authority. Publication and merge of this package are governance actions. Implementation authority remains inactive until every activation condition below is satisfied.

## Verified repository baseline

- Source branch: `main`
- Verified `HEAD == main == origin/main`: `1b3d744df7b373322ee0ca56fe8079d8c010a355`
- Source worktree: clean
- Governance PR: `#239`
- Governance reviewed head: `2b60d7c366b9e6ca3bec5ed33711eeceaac7a2b9`
- Governance merge commit: `1b3d744df7b373322ee0ca56fe8079d8c010a355`
- Stage 0.32: operationally verified and closed
- Migration 0004: deployed once and must not be executed again
- Migration inventory at publication: `0001` through `0004`; no `0005` exists
- Expected next migration: `0005`, subject to mandatory revalidation immediately before implementation begins

The actor-provenance operational gate remains open. Production candidate activation remains unauthorized.

## Authority purpose

After activation, this package permits one non-production branch and one implementation PR implementing exactly the merged Stage 0.33A governance contract. The bounded categories are:

- candidate-specific actor authorization and exact bounded errors;
- propagation through the existing typed candidate-creation API and capability chain;
- removal of the exported creator-less `MaterialReceiptService.create_receipt_candidate` bypass while retaining the service class and its unrelated operations;
- atomic receipt creator persistence;
- Migration 0005 `UP` and disposable-test-only `DOWN` files;
- the exact candidate-writer column-`INSERT` grant delta;
- unit, disposable PostgreSQL, privilege, security, adversarial, and Stage 0.32 regression tests; and
- narrow maintenance of the existing bootstrap grant-verification literals required to represent the new approved column, without executing that helper or changing credential behavior.

No production deployment, runtime activation, Telegram binding, confirmation/posting enablement, credential rotation, or production database contact is authorized.

## Frozen implementation outcome

The implementation target is exactly:

```text
public.material_receipts.created_by_actor_reference TEXT NOT NULL
```

The only candidate-authorized representation is:

```text
operator:<canonical-lowercase-uuidv4>
```

The existing `material_receipts.created_at` remains the authoritative creation time. There is no provenance table, generic audit/event platform, second provenance timestamp, generic provenance getter, public provenance read API, or provenance index. An index requires separate query evidence and approval.

## Project Owner approval

The Project Owner approves publication of this bounded implementation-authorization package and, only after its independent review and merge plus every activation condition below, one non-production Stage 0.33A implementation attempt within the exact allowlist.

The approval preserves:

1. the broader existing generic `ActorContext` grammar;
2. the operation-specific operator/canonical-lowercase-UUIDv4 candidate policy;
3. deterministic `ACTOR_REQUIRED`, `ACTOR_INVALID`, and `ACTOR_UNAUTHORIZED` behavior;
4. exact PostgreSQL enforcement with no silent weakening;
5. immutable, atomic creator persistence;
6. Stage 0.32 source idempotency and Migration 0004 closure;
7. least-privilege candidate `INSERT` only and no creator `UPDATE`;
8. no provenance read exposure;
9. exactly one governed externally reachable candidate-creation path and no raw-actor service bypass; and
10. no production authority.

## Authority activation conditions

Implementation authority becomes active only after all of the following occur:

1. this implementation-authorization PR receives an independent governance/architecture/security review;
2. that review records zero blocking findings;
3. the authorization PR is merged;
4. the Project Owner approval above is accepted in the merged record;
5. local `HEAD`, `main`, and `origin/main` are synchronized and the worktree is clean;
6. the migration inventory is reverified and `0005` remains free; and
7. the exact implementation file allowlist in this package is confirmed unchanged and sufficient.

If `0005` is occupied, the allowlist is insufficient, or exact database enforcement is impractical, implementation must not begin or must stop and return to governance.

Only after all seven conditions:

**STAGE 0.33A IMPLEMENTATION AUTHORITY: ACTIVE**

## Explicit exclusions

This package does not authorize:

- production PostgreSQL access, preflight, migration deployment, or mutation;
- production `DOWN`;
- changes to `runtime.env`, systemd, Docker, or services;
- Telegram or Universal Ingestion changes;
- a Telegram identity resolver;
- OCR, Vision, LLM, or Brain invocation;
- confirmation, posting, stock, or movement activation;
- production role, ownership, membership, credential, or grant mutation;
- production candidate traffic; or
- more than one implementation branch/PR.

## Remaining gates

After implementation merge, the actor-provenance operational gate remains open until separately authorized Stage 0.33B production deployment and verification. These also remain open:

- **RUNTIME-SECRET ROTATION / ACTIVATION SAFETY**
- **EXPLICIT PRODUCTION SAFETY REVIEW**

Production candidate activation is **NOT AUTHORIZED**.
