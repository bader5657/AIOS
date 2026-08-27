# Test, Security, and Implementation Gates

## Permanent future test requirements

A separately authorized implementation must add permanent tests proving:

1. a valid operator actor persists;
2. the stored value is a canonical lowercase UUIDv4 with the exact `operator:` prefix;
3. a missing actor fails before mapper, capability, or database mutation;
4. invalid actors are rejected;
5. forged `ActorContext` state is rejected;
6. actor identity remains separate from ingestion and trusted facts;
7. Telegram content cannot supply an actor;
8. a Telegram sender ID cannot directly become an actor;
9. OCR, Vision, LLM, and Brain cannot supply an actor;
10. actor provenance is inserted atomically with receipt and items;
11. rollback leaves no receipt, items, or provenance;
12. the actor is immutable on revision;
13. the actor is immutable on confirmation, rejection, cancellation, and posting;
14. a terminal replacement receives its own newly authenticated actor;
15. a same-source attempt by a different actor returns `SOURCE_ACTIVE_RECEIPT_EXISTS`;
16. a duplicate response does not disclose the existing creator;
17. the candidate runtime has only the restricted privilege required by the approved contract;
18. posting, stock, and movement authority remains unchanged;
19. the exception graph leaks no credential or authentication internals;
20. Migration 0005 `UP` and `DOWN` are tested only in disposable PostgreSQL; and
21. the production zero-row preflight fails closed.

Tests must also cover blank values, unknown prefixes, malformed and noncanonical UUIDs, non-v4 UUIDs, uppercase UUID text, control characters, Unicode lookalikes, path-shaped values, SQL-shaped values, DSNs, credential-shaped values, overlength values, and forged/subclassed DTOs wherever the exact-type policy applies.

## Security invariants

- Actor identity is accepted only from the authenticated trusted AIOS application identity boundary.
- Actor references remain non-secret identity metadata and never carry credentials or secrets.
- Candidate creation revalidates `ActorContext` at every governed boundary and fails closed.
- Creator provenance is immutable and unavailable through a generic update surface.
- Duplicate-source behavior neither changes provenance nor leaks the existing creator.
- The privilege envelope remains least-authority and does not expand posting, movement, stock, admin, or database-owner capabilities.
- No Telegram, Universal Ingestion, OCR, Vision, LLM, or Brain path gains actor authority through this decision.

## Frozen stage sequence

### Stage 0.33A

```text
governance merge
→ separate implementation authority
→ implementation + Migration 0005 files
→ disposable PostgreSQL/security tests
→ independent implementation review
→ merge
```

The governance merge is not implementation authority. Migration files, application changes, role/grant changes, and production operations require their own explicit authority.

### Stage 0.33B

```text
separate production read-only preflight
→ one-shot Migration 0005 deployment
→ post-deployment verification
→ actor-provenance operational gate closure
```

Migration 0005 deployment is contingent on the immediately preceding production zero-row result and every applicable approval. A positive row count is a hard stop. Production activation remains outside Stage 0.33B until all other gates close.

## Remaining gates

These gates remain open:

- **RUNTIME-SECRET ROTATION / ACTIVATION SAFETY**
- **EXPLICIT PRODUCTION SAFETY REVIEW**

Production candidate traffic remains **NOT AUTHORIZED**.

## Publication closure condition

Stage 0.33A repository publication is complete only when this Markdown-only package is committed on its narrow documentation branch and an unmerged governance PR is open. The resulting classification is:

**STAGE 0.33A GOVERNANCE DECISION FROZEN**
**— REPOSITORY GOVERNANCE PR OPEN**
**— IMPLEMENTATION NOT YET AUTHORIZED**
