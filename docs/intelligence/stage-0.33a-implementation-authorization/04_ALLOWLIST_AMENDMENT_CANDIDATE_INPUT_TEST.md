# Stage 0.33A Implementation Allowlist Amendment — Candidate-Input Security Test

## Amendment classification and purpose

**23RD PATH PROPOSED — AMENDMENT REVIEW AND MERGE REQUIRED BEFORE USE**

Stage 0.33A governance is merged and verified, and its implementation authorization is merged and active. Implementation PR `#241` remains the sole authorized implementation PR. This amendment proposes exactly one additional existing test path:

```text
tests/unit/app/material_receipts/test_candidate_input.py
```

The authoritative allowlist in `01_EXACT_IMPLEMENTATION_FILE_ALLOWLIST_AND_API_CONTRACT.md` therefore resolves to exactly **23 paths**: nine application/support paths, two migration paths, seven unit-test paths, and five integration-test paths. No other path expansion is proposed or authorized.

This amendment exists solely to repair a stale Stage 0.31A/0.33A security-test monkeypatch while preserving or strengthening the test's original zero-operational-capability intent. It does not authorize broad cleanup, refactoring, or unrelated changes in the newly listed file.

## Implementation stop and preservation record

Implementation remediation for PR `#241` already exists locally and remains uncommitted. Full-suite verification correctly stopped when the pre-existing stale monkeypatch was found outside the then-active 22-path allowlist. This amendment does not require that remediation to be discarded, stashed, restarted, or committed before amendment activation. After this amendment independently passes review and is merged, the existing local PR `#241` remediation may continue under the amended authority.

The observed stale reference was around `tests/unit/app/material_receipts/test_candidate_input.py:781`:

```python
monkeypatch.setattr(
    MaterialReceiptRepository,
    "create_receipt_candidate",
    forbidden("persist"),
)
```

## Narrow authority for the 23rd path

The newly allowlisted file may be modified only to:

- remove or update the stale monkeypatch against the removed public repository create method;
- preserve the original invalid-input zero-operational-capability security intent;
- point a sentinel/monkeypatch to the exact current authorized private/internal persistence boundary when technically appropriate; or
- remove the obsolete persistence patch when repository-construction, credential, and database-connect sentinels already prove equivalent or stronger zero-side-effect behavior.

All unrelated candidate-input tests must remain unchanged. No broad cleanup or refactor is authorized.

The preferred remediation order is:

1. when existing repository-construction, credential, and database-connect sentinels already establish zero operational capability before persistence can occur, remove the obsolete public-method monkeypatch and retain/assert those stronger boundaries; otherwise
2. if a direct persistence sentinel remains materially useful, monkeypatch the exact current private/internal persistence seam.

No production API may be invented for test convenience.

## Public and private persistence-surface policy

The remediation decision is preserved: public `MaterialReceiptRepository.create_receipt_candidate` must remain absent. It must not be restored to satisfy the stale test. No test-only public alias may be created, raw actor creation may not be exposed, and production architecture may not be changed for test convenience.

Candidate persistence may remain behind a private/internal repository seam, conceptually `_create_receipt_candidate(...)` or the exact current implementation equivalent. The amended test may sentinel that private/internal seam only when necessary and stable.

## Security proof that must remain intact

Invalid ingestion/candidate input must continue to prove zero operational capability, as applicable:

```text
MaterialReceiptRepository construction = 0
InventoryPostingRepository construction = 0
candidate credential loading = 0
posting credential loading = 0
database connection = 0
confirmation activity = 0
posting activity = 0
candidate persistence through the current architecture = 0
```

The security proof must not be weakened merely to make the suite pass.

## Test-to-file mapping

- Candidate-input zero-operational-capability non-regression → `tests/unit/app/material_receipts/test_candidate_input.py`
- Stale repository-create monkeypatch migration → `tests/unit/app/material_receipts/test_candidate_input.py`

No other mandatory requirement is moved to this file.

## Contracts preserved without change

This amendment does not change creator storage architecture; `ActorContext` policy; operator UUIDv4 policy; deterministic actor taxonomy; canonical creator capture-once design; TOCTOU remediation; removal of the global `ActorContext` registry; removal of the public repository raw-actor create seam; service create-method removal; Migration 0005 semantics; the privilege contract; trust-boundary requirements; PostgreSQL proof requirements; schema/object preservation; exception-graph requirements; Stage 0.32 preservation; or production isolation.

No second implementation PR is authorized. PR `#241` remains the one implementation PR.

## Project Owner approval

The Project Owner records:

> I approve adding exactly `tests/unit/app/material_receipts/test_candidate_input.py` to the Stage 0.33A implementation allowlist solely to repair the stale repository-create monkeypatch while preserving or strengthening the original zero-operational-capability security test.
>
> I do NOT approve restoring a public repository create method.
>
> I do NOT approve any other implementation path expansion.
>
> I do NOT approve production deployment or activation.

## Amendment activation conditions

The 23rd-path authority becomes usable only after all of the following:

1. this amendment PR receives an independent governance/architecture/security review with `PASS`;
2. that review records zero blocking findings;
3. this amendment PR is merged;
4. the Project Owner approval above is recorded in the merged amendment; and
5. local `HEAD`, `main`, and `origin/main` are synchronized and the worktree is clean.

Until all five conditions are satisfied, the existing active implementation authority remains limited to its prior 22 paths and the proposed 23rd path may not be modified. Once satisfied, the same Stage 0.33A implementation authority is amended from 22 to 23 exact paths and the existing PR `#241` remediation may resume. The amendment does not authorize a second implementation PR.

## Production safety record

During preparation and publication of this amendment:

```text
Production PostgreSQL contacted: NO
Production mutation: NONE
Application code changed: NO
Test code changed: NO
Migration files changed: NO
runtime.env: UNCHANGED
Runtime service: UNCHANGED
Telegram: UNCHANGED
Universal Ingestion: UNCHANGED
Production candidate activation: NOT AUTHORIZED
```

## Next official action

Independent governance/architecture/security review of this amendment PR. Do not merge or use the 23rd-path authority until the review records `PASS` with zero blocking findings. After review and merge, synchronize clean `main`; then continue the preserved local remediation in the existing implementation PR `#241` under the amended 23-path authority. Production deployment and activation remain unauthorized.
