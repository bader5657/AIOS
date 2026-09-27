# P4S7 Operator Evidence — One-Time Legacy Bootstrap Amendment

Status: **PROPOSED — NOT APPROVED — NOT ACTIVE**

Authority: proposed [GD-008](../../governance/GOVERNANCE_DECISION_008.md) and
[Operator Review Evidence Process](../../governance/operator-review-evidence/00_PROCESS.md).

## Defect, explicit substitution and limits

Original retained independent operator acceptance records are currently unavailable
for the four exact subjects below. Their existence, historical acceptance or
pre-merge review timestamps must not be asserted without authentic source records.
The PR #303 statement that PR #302's CLEAN review was retained is a historical
assertion, not an available source receipt or permission to reconstruct it.

PR #301's retained-acceptance requirements and PR #303's before-population STOP
do not themselves permit fresh retrospective verification to replace original
pre-merge acceptance. This is an explicit proposed exception to:

- [PR #301: component review identity](../stage-0.33c-p4s7-recovery-review-merge-evidence/00_RECOVERY_REVIEW_MERGE_EVIDENCE_CONTRACT.md#closed-evidence-schema),
  [trust-root evidence](../stage-0.33c-p4s7-recovery-review-merge-evidence/00_RECOVERY_REVIEW_MERGE_EVIDENCE_CONTRACT.md#trust-root-and-separately-authorized-selector-publication),
  and [bootstrap ordering](../stage-0.33c-p4s7-recovery-review-merge-evidence/00_RECOVERY_REVIEW_MERGE_EVIDENCE_CONTRACT.md#bootstrap-anti-circularity-and-supersession),
  only insofar as they require these four unavailable original acceptance records
  or a second human for the corresponding prospective bootstrap acceptance;
- [PR #303: exact component review/merge identities](../stage-0.33c-p4s7-recovery-binding-supersession/00_FIRST_RECOVERY_EVIDENCE_BINDING_AUTHORITY.md#exact-component-reviewmerge-identities)
  and [later population gates](../stage-0.33c-p4s7-recovery-binding-supersession/00_FIRST_RECOVERY_EVIDENCE_BINDING_AUTHORITY.md#later-population-gates-and-exclusions),
  only for the corresponding acceptance prerequisite and the prospective
  disposition of the already-populated, unmerged first record.

Keep PR #301/#303 and all historical artifacts byte-identical. This separate addendum
supplies the exception; no historical gate is represented as having passed. For this
limited development/bootstrap path, disclosed solo-Owner review replaces the
second-human requirement; it does not establish historical independence or authorize
production execution. The process section 1 role model and high-risk production boundary
apply to every step below. Every non-excepted requirement, including topology, blobs,
human merge, no-conflict verification and fresh external operator gates, remains
mandatory.

## Exhaustive immutable allowlist

| PR | Exact historical reviewed HEAD | Exact actual merge |
|---|---|---|
| 299 | `fd36b9abe6920ea807a070ea63589622e1d2e2cb` | `ba717f6990d775748f46d62ef03a696f1618077b` |
| 300 | `ed7f75551a118a96fc26e805057c1a875345c55a` | `8e9a8023742773b055e17dba002b2ebf07528118` |
| 302 | `f379a15eb5f64b5b5a6ffd7cb7ca0d27c847e368` | `b5fa2acaa66db799ebd8ec03d2a06a04e34753a2` |
| 303 | `dfdf98fbee0405b188530e9f374515ebc72ce1b2` | `5e296cd907c2e9f0c016097cb3c97e646893031f` |

No other PR, replacement SHA or arbitrary historical certification is eligible.
PR #301's own acceptance is not covered by this exception; if required evidence
for it or another prerequisite is unavailable, STOP and seek separate governance.
No authority to expand this table is delegated to a custodian or reviewer.

## Required one-time sequence after separate approval

1. Review this complete amended proposal under the disclosed process role model;
   the sole human Owner may perform this bootstrap governance review. Obtain explicit
   Project Owner approval of the exact final head and this exception, human
   merge, reviewed/merged document equality, and explicit activation. Commission
   the process with real appointed identities and complete authority inventory.
2. Obtain a separately scoped Owner instruction to perform fresh human
   re-reviews of all four exact subjects under that disclosed role model. The current design task performs none.
   Review both the historical changes against their applicable governance and
   their compatibility with the now-proposed bootstrap chain. Record limitations;
   do not silently grade historical scope against unrelated later requirements.
3. For each subject, verify actual PR identity, original two-parent merge topology
   with exact reviewed-head second parent, and required lineage using original,
   replacement/graft-resistant Git objects. Independently authenticate actual
   human-merge evidence. Git/API evidence alone does not establish human intent
   or acceptance. Missing human evidence remains STOP even if topology passes.
4. Compare exact reviewed/merged blobs: PR #299 amendment, executor and policy;
   PR #300 recovery activation governance; PR #302 executor and policy; PR #303
   first-binding authority addendum. Confirm PR #301 contract lineage and its
   preserved bytes at the reader. Preserve all fixed runtime, executor, policy,
   authority, approval, payload and predecessor identities from PR #303.
5. Record each fresh review's actual current UTC timestamp, current merge
   verification timestamp, reviewer identity, findings and real sources under
   `retrospective-revalidation`. Explicitly state: "Fresh retrospective
   re-validation; not the original pre-merge review; original acceptance record
   unavailable." The accountable human Owner in solo mode must adopt any AI-assisted
   result as advisory evidence, never independent human acceptance. Record
   role_context and disclose every combined role and absence of a second human. Never backdate a source, review, authentication or approval.
   Record current assembly time as `record_created_at_utc`; preserve the sourced
   actual historical `merge_occurred_at_utc`. Apply the process's correction and
   unavailable-timestamp rules: no original pre-merge time is invented, and a
   required historical time that cannot be authenticated is STOP.
6. Publish four records through the new process, with separate explicit Owner
   approval of each record's admission scope and role-disclosed verification of human
   publication merges. CLEAN is required for admission; blocking findings require
   a new correction/review under separate authority, never a fabricated PASS.
7. Perform fresh authoritative no-conflict/no-revocation verification against the
   commissioned register and directly authenticated Owner inventory. It must
   cover competing first records for the R34 baseline, conflicting supersession
   authorities, hidden/pending successors, revocations and the current selector
   decision. Git search alone is insufficient. Publish and verify under the disclosed role model
   a `bootstrap-admission` action-verification record whose `target` is the exact
   held candidate below and whose `bootstrap_review_records` contains the four
   published retrospective records in PR order 299, 300, 302, 303. Pin the exact
   register tip/sequence, authority inventory and governance references, and
   retain its authenticated publication/verification timestamps.
8. The Owner may then publish one `admit-bootstrap` decision using its required
   `bootstrap_verification` GitRef to that previously completed verification,
   following [the process's exact reference and validation rules](../../governance/operator-review-evidence/00_PROCESS.md#bootstrap-admission-verification-reference).
   `subjects` contains exactly the four review GitRefs followed by the candidate
   target; `governance_basis` identifies GD-008 and this amendment. The dedicated
   `bootstrap_verification` field is mandatory and cannot be replaced by subjects
   or free text. Require PASS, exact identities, matching register predecessor
   and inventory, completion before decided_at_utc, current unexpired/unrevoked
   authority through publication, and no reuse for another admission. This is a
   prospective remedy for the missing evidentiary prerequisite, not historical ratification of the
   population event, a merge instruction or operational activation.

Admission consumes only this single bootstrap admission opportunity, never the
recovery installation authority. A later corrected record may supersede its
earlier version only for the same allowlisted subject under the process; it
does not admit another chain or issue another first-record entitlement. Close the
bootstrap register entry after the first evidence's eventual separately authorized
merge and verification, or on abandonment. Reopening requires new explicit
governance, not reuse of an old CLEAN verdict.

## Prospective disposition of PR #304

The held candidate is PR #304 HEAD
`e1a4459dc55ad9a15fe6dfc28dc11758a799c8c0`, adding only
`docs/intelligence/stage-0.33c-p4s7-recovery-review-merge-evidence/records/1b8e3152-e315-43f4-9396-28776bd87947.json`.
Its transport SHA-256 is
`11a609eaf580d3283b84d4994fb7f79a2995da6bab529ca722032f69c98523b2`.
Its predecessor remains R34 merge `8e9a8023742773b055e17dba002b2ebf07528118`,
the existing recovery activation governance path, transport SHA-256
`299296d106d6d661ac2fd55b1442b9980485d7f2bdf64b228fbfebbbb73dcf31`.

PR #304 remains blocked until this amended governance is reviewed and explicitly
approved. That approval alone does not release the hold: all steps 1–8 and the separate
prospective review/merge authorization remain required. No merge is authorized by this
amendment or by the instruction to prepare it.

Only after steps 1–8 may these retrospective records substitute for the four
unavailable original acceptances for a separately authorized fresh review of
that exact first-record candidate. Do not alter its fifteen-field schema, JSON
bytes, binding UUID or claim that population was originally compliant. Any HEAD
or byte change requires explicit disposition and new review; this amendment
does not approve a replacement candidate or a second record.

Because this governance is necessarily later than the held candidate, the
candidate is not required to contain or descend from this new amendment.
Instead, its eventual actual two-parent merge must have the exact reviewed HEAD
as second parent and an authorized main first parent containing this approved
amendment, commissioned process, admitted records and admission decision. Verify
reviewed/merged evidence byte equality afterward. This narrowly replaces only
an impossible candidate-ancestry requirement for this new remedy; the candidate
must still descend from the original PR #303 and reader/runtime lineage.
No future merge SHA is guessed or embedded.

The separate PR #304 review/merge and later separately authorized selector
publication still require their own retained acceptance, actual human merge,
post-merge equality and fresh action gates. This amendment itself is insufficient
to declare PR #304 CLEAN or safe to merge.

## Unchanged boundaries

Runtime remains pinned at `b5fa2acaa66db799ebd8ec03d2a06a04e34753a2`.
Later governance or archive commits do not advance runtime. No executor/policy
change, selector, activation, one-shot install, recovery authority consumption,
service/database action, Step-4 closure or Step-5 is authorized. The existing
approval window is unchanged and is neither renewed nor reserved; expiry still
blocks every applicable later action. Record admission cannot cure expired
operational approval. No old activation or unavailable original review is reused.

This proposal creates no evidence records, source receipts, appointments, approval
statements, register entries or freshness PASS. Stop after disclosed governance review
preparation; no automatic merge or bootstrap execution.
