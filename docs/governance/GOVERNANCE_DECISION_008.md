# AIOS Governance Decision 008 — Operator Review Evidence Process

Status: **PROPOSED — NOT APPROVED — NOT ACTIVE**

Decision ID: GD-008

Classification: Governance and Documentation. Approval authority: Project Owner.

## Defect and proposed decision

The [PR #301 contract](../intelligence/stage-0.33c-p4s7-recovery-review-merge-evidence/00_RECOVERY_REVIEW_MERGE_EVIDENCE_CONTRACT.md#trust-root-and-separately-authorized-selector-publication)
requires an "existing operator evidence process". The
[PR #303 authority](../intelligence/stage-0.33c-p4s7-recovery-binding-supersession/00_FIRST_RECOVERY_EVIDENCE_BINDING_AUTHORITY.md#exact-component-reviewmerge-identities)
requires retained independent acceptance and human-merge evidence before
population. Neither identifies the external archive, record schema, custodian,
retention procedure, or complete authoritative succession source. GD-003 explicitly
leaves retention and archive mechanisms undefined. Git identity cannot fill this gap.

Adopt [the Operator Review Evidence Process](operator-review-evidence/00_PROCESS.md)
as the repository-governed retention and authentication process, initially only
for P4S7 recovery. Adopt the separately scoped
[legacy bootstrap amendment](../intelligence/stage-0.33c-p4s7-operator-evidence-bootstrap/00_LEGACY_BOOTSTRAP_AMENDMENT.md)
only for its four enumerated immutable PR identities. This decision proposes new
normative detail; it does not claim that the missing process previously existed.

## Authority and activation gate

[GD-001](GOVERNANCE_DECISION_001.md) requires authority audit, governance validation,
final governance review and Project Owner approval.
[GD-002](GOVERNANCE_DECISION_002.md) distinguishes review, approval, publication
and activation; [GD-003](GOVERNANCE_DECISION_003.md) rejects merge-as-approval;
[GD-007](GOVERNANCE_DECISION_007.md) preserves explicit scope and historical records.
The [Authority Hierarchy](../architecture/AIOS_AUTHORITY_HIERARCHY.md#4-approval-hierarchy)
reserves approval to the Project Owner and requires explicit scoped delegation.

All three proposed documents remain non-authoritative until independent review
and explicit Project Owner approval of their exact final reviewed head, human
merge with reviewed/merged byte equality, and explicit activation for this scope.
Approval of PR preparation is not approval of this decision or of any bootstrap
record. Do not label the proposal Approved, Published or Active by inference.

The process's initial commissioning is a separate, explicitly Owner-authorized
governance publication after that human merge. Its non-circular authentication
procedure is defined in the process. A missing authenticated commissioning
record blocks use; this proposal creates none. Commissioning does not require
or publish a runtime selector. Signed attestations, new keys, services and
reader implementation are outside this decision.

The initial Owner instruction may explicitly activate the exact merged package
for commissioning and authorize that single genesis publication, using the
already-established Owner identity. Retain that instruction and its independent
authentication as genesis source receipts. This bounded startup does not assume
an earlier archive record exists. Until genesis publication is independently
verified, no review-record admission or recovery action may rely on this process.

## Relationship to earlier authority

GD-008 supplies the previously unspecified process within its declared scope;
it does not replace GD-001/002/003/007 or create a new architecture authority.
The bootstrap addendum explicitly amends the evidentiary prerequisites of
PR #301/#303. Without its separate explicit approval and activation, their
original unavailable-evidence STOP remains binding. Preserve their historical
bytes. No original review is invented and no previous gate becomes satisfied
retroactively. Reviewers may record findings; only the Owner approves their
admission for a specified future governance action.

Bootstrap admission uses the process's dedicated `bootstrap_verification` GitRef
and the referenced verification's exact `bootstrap_review_records`, with no
generic-subjects or free-text substitute. Corrections preserve authenticated
historical event times and separately record current creation, verification,
acceptance, approval and publication times; unavailable required historical times
remain STOP. These clarifications grant no additional authority.

## Proposed file scope and disposition

Only this decision, `operator-review-evidence/00_PROCESS.md`, and the linked
bootstrap amendment are added. Their paths are normative; future archive records
and source receipts are not populated by this proposal.

No PR #304 change or merge; evidence re-review; selector publication; activation;
installation; authority consumption; approval-window renewal; Step-4 closure;
Step-5; source, test, policy, executor, runtime, service or database change is
authorized. Later actions retain their separate permissions and fresh gates.

Next action: independent governance/security review and explicit Project Owner
decision. Do not merge automatically. No approval or activation is recorded here.
