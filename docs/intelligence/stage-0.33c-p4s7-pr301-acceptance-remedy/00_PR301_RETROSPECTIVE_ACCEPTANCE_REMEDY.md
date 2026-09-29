# P4S7 PR #301 — Narrow Retrospective Acceptance Remedy

Status: **PROPOSED — NOT APPROVED — NOT ACTIVE**

Scope: governance and evidence preparation only, repository `bader5657/AIOS`.
Basis: [GD-008](../../governance/GOVERNANCE_DECISION_008.md), the commissioned
[Operator Review Evidence Process](../../governance/operator-review-evidence/00_PROCESS.md),
and the [Legacy Bootstrap Amendment](../stage-0.33c-p4s7-operator-evidence-bootstrap/00_LEGACY_BOOTSTRAP_AMENDMENT.md).
Their original proposal-status text is preserved; commissioning is established
by the authenticated genesis and subsequent retained publication evidence, not
by rewriting historical documents. This new proposal is not yet effective.

## Defect and exact exception

Authentic retained original acceptance evidence for PR #301 is unavailable.
Its [contract](../stage-0.33c-p4s7-recovery-review-merge-evidence/00_RECOVERY_REVIEW_MERGE_EVIDENCE_CONTRACT.md)
requires reviewed/merged contract acceptance before reader reliance (scope,
reader verification step 7, and bootstrap lifecycle step 1). The commissioned
process's retained determination therefore blocks acceptance of PR #302 as a
compliant governed reader while this prerequisite is unresolved.

This separate amendment permits a fresh retrospective re-validation of **only**:

| Identity | Exact value |
|---|---|
| PR | `301` |
| Historical reviewed HEAD | `fea48d292ad81182ae6f5327ce01f4e0ee6c6e88` |
| Actual historical merge | `7f124e307d9a516b4ce278d800c92d29d476cf5e` |
| Governed artifact | `docs/intelligence/stage-0.33c-p4s7-recovery-review-merge-evidence/00_RECOVERY_REVIEW_MERGE_EVIDENCE_CONTRACT.md` |
| Historical artifact transport SHA-256 | `7b9e5ee9daf7b9ffe387b63ebff6629d97546a27eb0f5207271ac5ec1fb9f957` |

Once this remedy is effective and its required review record is published and
verified, that approved CLEAN record may prospectively satisfy **only PR #301's
missing contract-acceptance prerequisite** for the bounded legacy bootstrap
re-validation/admission of the exact PR #302 reader:
reviewed HEAD `f379a15eb5f64b5b5a6ffd7cb7ca0d27c847e368`, merge
`b5fa2acaa66db799ebd8ec03d2a06a04e34753a2`.
It does not establish that implementation originally followed the required
review-before-implementation ordering. No historical gate is retroactively
certified; this is a prospective evidence substitution for that named dependency.

For this subject and purpose only, this amendment expressly supplements the
Process section 3 rule limiting retrospective records to the legacy allowlist
and supplies the separate governance demanded by the Legacy Amendment's PR #301
exclusion. It permits disclosed solo-Owner acceptance of the fresh review in
place of the unavailable original independent acceptance **for this bootstrap
use only**. It does not establish original review, historical independence, or
production acceptance. Every other contract and process requirement remains.

The existing four-subject exception remains unchanged: PRs #299, #300, #302 and
#303, with their original exact identities. PR #301 is not added to that table,
the four-record `bootstrap_review_records` array, or the five-subject
`admit-bootstrap` set. No new first-record entitlement, second admission, or
expanded historical allowlist is created. No PR #301 historical bytes change.

## Effectiveness and separate decisions

Preparation or publication of this proposal is not approval or activation.
Before this remedy may be used, require disclosed human governance review,
explicit Project Owner approval and merge authorization naming its exact final
HEAD, an actual two-parent human-authorized merge with reviewed HEAD as second
parent, and authenticated post-merge verification of exact document equality.
Retain those receipts under Process sections 1 and 6; no future merge is guessed.

Explicit activation and scoped authority to conduct the PR #301 re-validation
must then be recorded through the existing serial Owner decision register.
Use its existing `supersede` decision type solely for this narrow procedural
acceptance restriction: identify the affected commissioned decision(s) in
`subjects`, include the exact merged remedy and GD-008/process/legacy basis in
`governance_basis`, and limit `effect` to this PR #301 evidence substitution.
Preserve all other effects of those decisions, the four-subject exception and
all operational restrictions. Follow the existing predecessor, sequence,
reviewer-acceptance, separate Owner-approval, publication and verification rules;
`bootstrap_verification` and `selector` are null and `appointments` is empty.
No new decision type or schema field is introduced. Activation is ineffective
until that decision's authenticated publication is verified. A direct instruction
or this proposal alone cannot bypass the register's positive-authority rule.

Missing, conflicting, revoked or unverifiable authority is STOP. This proposal
creates no decision entry, activation, review record or attestation.

## PR #301 review and evidence lifecycle

After effectiveness and the separately scoped instruction above:

1. Verify exact GitHub PR identity, original two-parent topology, reviewed-head
   second parent and required lineage using replacement/graft-resistant Git
   objects. Compare the exact reviewed and merged contract bytes and their
   transport SHA above, including preservation at the exact PR #302 reader.
2. Obtain direct authenticated firsthand Owner/merger corroboration of PR #301's
   actual human merge and sourced historical occurrence time. Git/API metadata,
   a merge message or ancestry alone is insufficient. Missing corroboration or
   required historical time is STOP; do not infer it from PR #302 confirmation.
3. Perform a fresh substantive review now against applicable historical
   governance and current bounded bootstrap compatibility. Examine the contract's
   trust, history, custody, supersession and external freshness requirements.
   Do not assert a CLEAN verdict from hashes alone or infer PR #302 correctness.
4. Reuse the unchanged `aios-operator-review-evidence-v1` closed schema, canonical
   UTF-8/LF JSON, paths, source digests, authentication and custody rules. Set
   `classification` to `retrospective-revalidation`, `permitted_use` to
   `p4s7-recovery-evidence-gate-only`, and `predecessor` to null for the first
   PR #301 review record. Corrections follow the existing same-subject rules.
   `process_authority` remains the exact commissioned GD-008 GitRef.
   **For this PR #301 record only**, `bootstrap_authority` is a GitRef to this
   remedy's actual verified merge, path and transport digest, rather than the
   unchanged four-subject amendment. This explicitly permits that value without
   adding fields. The review source must bind the original bootstrap authority,
   this remedy's activation decision and its verified publication receipts.
5. Use actual current `reviewed_at_utc`, `merge_verified_at_utc` and
   `record_created_at_utc`, and the separately sourced historical
   `merge_occurred_at_utc`. Preserve source precision. State exactly:
   "Fresh retrospective re-validation; not the original pre-merge review;
   original acceptance record unavailable." No backdating, invented original
   review time, historical acceptance fabrication or silent receipt correction.
6. Preserve `solo-project-owner-bootstrap` and every combined role in the
   digest-bound disclosure. The authenticated appointed Owner may act as reviewer,
   approver, custodian and verifier for this scope; no second human or independent
   human acceptance is claimed. AI assistance is advisory only. Blocking findings
   require CHANGES_REQUIRED and STOP; only a CLEAN payload may satisfy this gate.
7. Freeze the payload before the accountable human's personal reviewer acceptance.
   Obtain separate later Owner approval of the same digest. Prepare a separate
   governance-only record publication PR with exact sources, exact-HEAD human
   publication review, and explicit Owner publication authorization naming the
   final HEAD and custodian. Human-authorized merge publishes the record; verify
   actual merge identity/topology and reviewed/merged bytes, and retain the
   authenticated human verifier's post-merge adoption before PUBLISHED / VERIFIED.

## Gate closure and unchanged boundaries

The PR #301 acceptance blocker remains unresolved until the complete sequence
above passes. Only then may a separate Owner instruction resume PR #302 review.
Its review source must cite the exact published PR #301 review-record GitRef,
its valid acceptance/approval and authenticated post-merge verification, and
this effective remedy/activation chain. Carry those references in existing
source receipts; do not change the closed PR #302 payload or bootstrap schemas.
Later bootstrap action verification must verify this additional dependency
alongside, not instead of or as a fifth member of, the original four records.
No PR #302 CLEAN verdict, reviewer acceptance or publication follows automatically.

No new production authority is created. This remedy does not approve PR #302,
review PR #303, modify or merge PR #304, admit bootstrap evidence, supersede R34's
operational runtime/executor binding, publish a selector, create activation,
run a one-shot install, consume recovery authority, change runtime/services/
databases, close Step 4 or start Step 5. Approval windows are not renewed,
extended or reserved. No fresh no-conflict/no-revocation PASS is supplied.
Process section 1's high-risk production boundary and every action-specific
external verification and authorization gate remain mandatory. Bootstrap-only
solo acceptance never becomes independent human production evidence by reuse.

Stop after proposal preparation. Next: exact-HEAD human governance review and
separate explicit Owner approval. Do not merge automatically or resume PR #302.
