# Operator Review Evidence Process — v1

Status: **PROPOSED — NOT APPROVED — NOT ACTIVE**

Authority: [proposed GD-008](../GOVERNANCE_DECISION_008.md).
Scope: `bader5657/AIOS`, P4S7 recovery review evidence and authoritative succession.
This is a human-operated governance process, not a runtime reader extension.

## 1. Archive, roles and authentication

The normative archive is in accepted `main` history in this repository:

| Artifact | Exact path |
|---|---|
| Review record | `docs/governance/operator-review-evidence/reviews/<record_id>.json` |
| Owner decision register entry | `docs/governance/operator-review-evidence/decisions/<record_id>.json` |
| Action verification record | `docs/governance/operator-review-evidence/verifications/<record_id>.json` |
| Authentic source receipt | `docs/governance/operator-review-evidence/sources/<source_id>.txt` |

IDs are canonical lowercase UUIDs. Records are regular Git blobs, mode `100644`.
These paths never confer authenticity through existence, ownership or Git ancestry.
No runtime evidence, selector, claim/result or private-source directory is reused.

### Temporary SOLO PROJECT OWNER bootstrap role model

AIOS is in development/bootstrap with one human Project Owner/operator and no
independent second human reviewer available. No second person or independence may be
inferred, fabricated or attributed to an AI review.

The Project Owner remains the approval authority under GD-001/002/003. For
**development, bootstrap, governance preparation, non-destructive validation, and
evidence/process commissioning only**, `solo-project-owner-bootstrap` mode permits that
same authenticated human to review, approve, act as custodian, verify publication,
operate this governance process and commission it. Explicitly appoint the Owner to the
reviewer/custodian/verifier roles with the real identity, channel and scope. Combining
roles does not combine or skip the review, approval, human merge, post-merge
verification and commissioning steps.

Every payload must carry the closed `role_context` below, covered by its attested
digest. In solo mode its source receipts and pre-record governance approval, review,
commissioning and publication instructions must explicitly disclose the combined roles,
that only one human is participating, that no independent human acceptance is claimed,
and any advisory AI assistance. Reviewer acceptance and Owner approval remain separate,
sequential attestations by that same human. AI findings are advisory evidence only; the
accountable human must personally review and adopt findings against the exact PR/HEAD.
AI cannot authenticate, approve, commission or supply independent human acceptance.

In `independent-human` mode, the reviewer is a different person from the Owner and
independent of the subject's author/implementer; the publication verifier is independent
of the custodian and may be the reviewer. The Owner explicitly appoints each named
accountable human and channel. Solo mode does not claim these independence properties.
An AI agent may prepare drafts/copies when instructed but cannot impersonate any
principal.

Solo mode is temporary and must be explicitly selected for each instruction or record;
it is not an inferred default or a perpetual production waiver. When an independent
human becomes available, an authenticated `appoint-actors` decision may establish the
independent mode for future work. Mode changes never rewrite the role disclosures or
acceptance status of earlier evidence.

### High-risk production execution boundary

Solo-owner mode must not by itself authorize destructive production changes,
irreversible data mutation, recovery authority consumption, one-shot install execution
or final production activation. Crossing that boundary requires either (A) an
authenticated independent human reviewer accepting the exact proposed production action,
in addition to Owner approval and every existing action gate, or (B) a separately
reviewed and explicitly approved **future governance amendment** accepting solo-owner
production risk and defining its scope, evidence and execution gates. This proposal is
not that future amendment. An Owner instruction, combined-role appointment, bootstrap
admission, AI review or PASS cannot substitute for it. Until A or an effective B and all
existing prerequisites are satisfied, STOP at this boundary. Production use of bootstrap
evidence requires that additional action-specific acceptance; it never becomes
independent human evidence by reuse. Ambiguous or mixed scopes are STOP.

`solo-project-owner-bootstrap` permits PASS only for `bootstrap-admission`,
`evidence-review` and `evidence-merge` when strictly within the permitted governance
scope. It cannot yield a production-authorizing PASS for `selector-publication`,
`activation-creation` or `installation-attempt`. Non-destructive preparation may be
reviewed as `evidence-review`; it confers no execution authority. Decisions such as
`authorize-binding` or `authorize-selector` in solo mode can record only governance
preparation, with execution explicitly withheld in `effect`.

Authentication uses direct human confirmation with the already-known Project
Owner, in person or through an independently authenticated established channel,
and the Owner's explicit appointment of the other principals/channels. A channel
identifier is an exact public account/contact identifier and medium, never a secret.
For a new actor, the Owner must personally authenticate and appoint them before
their evidence is usable. Merely recognizing a GitHub username is insufficient.
No copied statement, GitHub review/comment, commit signature or JSON identity is
the sole authentication source. If the real Owner cannot be authenticated
independently of the proposed records, STOP; no self-enrollment or inferred trust.

For each attestation, the custodian obtains the actor's direct confirmation of the exact
payload digest, meaning, current timestamp and scope over an appointed channel. The
appointed publication verifier repeats the authentication check and compares the
retained receipts against that confirmation before accepting publication. In solo mode
the Owner performs and records this check through the established channel, disclosing
that it is self-verification, not independent human corroboration. Authentication
independent of the proposed records still applies; it does not require inventing a
second human. An identity/channel change requires a new Owner decision authenticated
using the previously trusted channel or fresh direct Owner identity verification;
ambiguity stops the process. There is no automatic trust of new contact details in a
record.

Source receipts retain exact UTF-8 statements/transcripts approved for publication
by their speakers: actor, authenticated channel, confirmation method, actual UTC
time, exact subject digest/identities and statement. Preserve their original bytes;
do not silently normalize, edit or redact an authenticated receipt. Obtain a new
sanitized source statement when needed; never commit credentials or private-source
contents. A receipt documenting a confirmation made now must say so. A source
copy is evidence to authenticate, not a signature or self-proving authority.

## 2. Closed types and canonical bytes

All objects below are closed: exactly the listed keys, no optional or unknown
keys. Types are strict; integers exclude booleans, floats and strings. Reject
duplicate keys at every depth, invalid UTF-8, NaN/Infinity and unsupported types.
Nullable fields accept only JSON `null` or the specified type. No empty identity,
scope, finding or source-description strings; no silent coercion or repair.

`UUID`: canonical lowercase UUID. `SHA`: 40 lowercase hex characters. `Digest`:
64 lowercase hex characters. `UTC`: real RFC3339 UTC timestamp in exactly
`YYYY-MM-DDTHH:MM:SS.ffffffZ` form. Times are actual event times, never invented,
backdated, or copied from a merge date to suggest a prior review.

| Closed type | Exact keys and constraints |
|---|---|
| `GitRef` | `commit: SHA`, `path: string`, `transport_sha256: Digest`; exact regular committed blob, repository-relative path, no traversal/symlinks |
| `SourceRef` | `path: string`, `transport_sha256: Digest`; exact `sources/<UUID>.txt` path under this archive, resolved in the same published tree as the referring record |
| `Actor` | `principal_id: UUID`, `name: string`, `channel_id: string`; authenticated human and channel from the active appointment |
| `Attestation` | `actor: Actor`, `at_utc: UTC`, `payload_sha256: Digest`, `source: SourceRef`; source explicitly adopts the payload and the field's meaning |
| `PRIdentity` | `pr_number: positive integer`, `reviewed_head_sha: SHA`, `merge_sha: SHA` |
| `BlobCheck` | `path: string`, `reviewed_sha256: Digest`, `merged_sha256: Digest`; digests must equal for acceptance |
| `Selector` | `schema_version: "aios-p4s7-recovery-review-merge-trust-v1"`, `evidence_commit: SHA`, `evidence_path: string`, `evidence_transport_sha256: Digest`; obey PR #301's exact path and value rules |
| `RoleContext` | `mode: "independent-human"` or `"solo-project-owner-bootstrap"`; `combined_roles: unique array of "reviewer", "approver", "custodian", "verifier", "commissioner", "operator"`; `disclosure: nonempty string` stating actual role combinations, scope and AI assistance. Solo mode lists every combined role and explicitly states no independent human acceptance; independent mode must satisfy section 1 role separation |
| `Appointment` | `actor: Actor`, `roles: nonempty unique array of "reviewer", "custodian", "verifier"`, `scope: "p4s7-recovery"` |

Every stored path is the full repository-relative path, never the abbreviated
directory labels used in prose. Reject absolute paths, traversal and symlink
entries for SourceRef as for GitRef. Source digests cover unmodified receipt bytes.

All JSON uses `json.dumps(value, ensure_ascii=False, sort_keys=True,
separators=(",", ":"), allow_nan=False).encode("utf-8")`, followed by exactly one
ASCII LF. Reject BOM, CRLF, extra LF/whitespace and noncanonical escapes. Transport
digests cover all committed bytes including LF. An attestation's `payload_sha256`
is SHA-256 of the canonical **payload object only, without LF**. Every attestation
in one record must bind that same digest. This is not a hash of the enclosing
record; there is no record self-hash or own publication-commit field. The payload
is frozen before statements are requested. Any change requires new statements.

All record classes have exactly these six top-level fields:

| Field | Constraint |
|---|---|
| `schema_version` | Class-specific literal below |
| `record_id` | UUID; equals filename stem and `payload.record_id` |
| `repository` | Exactly `bader5657/AIOS`; also equals `payload.repository` |
| `payload` | Class-specific closed object below |
| `reviewer_acceptance` | Attestation; accountable human adopts the findings under role_context; in solo mode the actor is the same authenticated Owner as project_owner_approval, with separate later approval |
| `project_owner_approval` | Attestation; Owner explicitly approves the payload's stated disposition/scope, not unlisted operations |

The payload repeats `record_id` and `repository` so their identities are covered
by the attested digest. Each payload includes its own `classification`, preventing
reuse of the same statements as another evidence class. Envelope version must
match that classification. Owner approval time must follow reviewer acceptance;
acceptance follows completion of all payload checks. No future times are accepted.

## 3. Review record schema

`schema_version = "aios-operator-review-evidence-v1"`.
The payload has exactly:

| Field | Type / rule |
|---|---|
| `record_id`, `repository` | As above |
| `role_context` | RoleContext; required, digest-bound scope and combined-role disclosure under section 1 |
| `classification` | `original-review-retention` or `retrospective-revalidation` |
| `record_created_at_utc` | UTC when this new record, including a correction, is actually assembled; never the historical review or merge time |
| `subject` | PRIdentity |
| `review_verdict` | `CLEAN` or `CHANGES_REQUIRED` |
| `reviewed_at_utc` | UTC of the actual review being retained: authenticated original review for original-review-retention, actual re-review for retrospective-revalidation |
| `merge_verified_at_utc` | UTC of current merge verification |
| `merge_occurred_at_utc` | UTC from merge evidence corroborated against authentic human sources and Git facts, independent of the proposed record; no second human required in solo mode; distinct from verification time |
| `review_source` | SourceRef: actual findings, scope, actual author/reviewer relationship, role_context disclosure, reviewer identity and any AI/tool assistance |
| `human_merge_source` | SourceRef: direct authenticated statement of the actual human merger or Owner with firsthand merge evidence; identify the historical actor/action; no API-only inference |
| `identity_sources` | Nonempty array of SourceRef: PR mapping, original two-parent topology, exact second parent and blob-comparison output; factual Git/API evidence only |
| `artifact_checks` | Nonempty array of BlobCheck, unique paths; all governance-required artifacts |
| `findings` | Nonempty string describing findings and limitations; `CLEAN` cannot coexist with unresolved blocking findings |
| `process_authority` | GitRef to the approved, merged GD-008 bytes |
| `bootstrap_authority` | GitRef to the approved, merged bootstrap amendment, or null for original-review-retention |
| `predecessor` | GitRef to preceding review record for this subject, or null for first record |
| `permitted_use` | Exactly `p4s7-recovery-evidence-gate-only` |

For original-review-retention, an authentic original human review satisfying the
governance effective at that event must already exist, bind the exact reviewed head, and
predate the actual merge. Its review timestamp comes from that authenticated original
source. Current collection, acceptance and approval dates remain current. Missing
original review cannot be filled by an old commit date, a PR description, or a fresh
review called original. Solo mode never retroactively waives an original independence
requirement or relabels a historical solo or AI review as independent human acceptance.

Historical event fields remain distinct from record-creation and current
verification/attestation times. `merge_occurred_at_utc` always describes the actual
historical merge. `reviewed_at_utc` describes the specific review retained by this
record, not collection or correction time. For the bootstrap's retrospective
class it describes the real re-validation, never an unavailable original review.
All required UTC fields remain non-nullable. If a required historical event time
cannot be authentically established, STOP: do not complete, publish or admit a
review record with a guessed time, null, sentinel, correction time or invented
precision. Retain a current-dated unavailability/STOP source receipt under
sections 1 and 6 instead. An unavailable original pre-merge review timestamp is
not a field to fill in a permitted retrospective record; an unavailable required
actual merge timestamp still blocks that record. Current verification timestamps
remain separately recorded in the source receipt even when completion is blocked.

Retention has two phases for a new PR: before its human merge, preserve authentic human
review under section 1 and Owner merge-authorization receipts bound to its exact final
HEAD under the source-receipt custody rules. After the actual merge, verify the merge
and assemble this completed record with its now-known merge_sha. No completed review
record containing a future merge is required before that merge. Pre-merge receipts alone
cannot satisfy a later completed-record gate. If the reviewed HEAD changes, obtain new
review and authorization receipts.

Retrospective records require the bootstrap amendment and its exact allowlist.
The review occurs now, after that amendment is effective; merge verification is
performed during that re-review, and both dates are after the historical merge.
Each record must expressly say it does not establish original pre-merge acceptance.
No unavailable human-merge evidence may be manufactured; retrospective technical
verification does not waive this separate requirement.

`CHANGES_REQUIRED` records may be retained but never satisfy an acceptance gate.
An Owner may approve retention of a failed review without accepting the subject.
Owner approval of a CLEAN record admits it only for `permitted_use`, subject to
the authoritative register and a fresh action verification.

## 4. Authoritative Owner decision register

The single serial register is `decisions/`, with one immutable, authenticated
Owner decision per sequence number. Its genesis is sequence 1, with null
predecessor. Every successor names the exact prior committed entry and increments
sequence by one. No timestamp, directory scan or moving `main` chooses authority.
Two valid successors to one entry are a conflict: STOP and obtain a separately
reviewed explicit Owner reconciliation; never silently choose one branch.

`schema_version = "aios-operator-authority-decision-v1"`.
The closed payload has exactly:

| Field | Type / rule |
|---|---|
| `record_id`, `repository` | As above |
| `role_context` | RoleContext; required, digest-bound scope and combined-role disclosure under section 1 |
| `classification` | Exactly `owner-authority-decision` |
| `sequence` | Positive integer |
| `predecessor` | GitRef to prior decision, or null for genesis |
| `decision` | One of `commission-process`, `appoint-actors`, `admit-bootstrap`, `authorize-binding`, `authorize-selector`, `supersede`, `revoke`, `close-bootstrap` |
| `decided_at_utc` | UTC; real decision time |
| `process_authority` | GitRef to approved merged GD-008 |
| `governance_basis` | Nonempty array of GitRef: exact already-approved governing documents, including bootstrap amendment when relevant |
| `subjects` | Array of GitRef: exact review records, evidence records or prior authority decisions affected |
| `bootstrap_verification` | Exactly one GitRef to a previously completed and published action-verification record for admit-bootstrap; JSON null for every other decision; never omitted or an array |
| `appointments` | Array of Appointment; nonempty only for commission-process / appoint-actors |
| `selector` | Selector or null; nonnull only for authorize-selector |
| `effect` | Nonempty string stating exact scope, superseded/revoked decisions and restrictions; cannot create authority beyond governance_basis |
| `owner_source` | SourceRef: authenticated Owner instruction, identities, inventory/completeness declaration, reservations and known pending/conflicting decisions |
| `predecessor_inventory` | Array of GitRef identifying all applicable pre-register governance authorities; required for genesis, empty otherwise |

Genesis requires explicit Owner commissioning under the now-approved and merged
three-document package. The Owner and appointed verifier (the same human in disclosed
solo mode) authenticate the package's exact final reviewed head, human merge and blob
equality directly, retaining receipts as genesis sources. This is the sole initial trust
ceremony; it does not rely on a record approving itself or claim that an archive
previously existed. The genesis Owner identity is established independently as in
section 1. Initial reviewer/custodian/verifier appointments are approved explicitly by
that Owner before genesis preparation and retained in its source receipts; later role
changes require already-authenticated register authority. Missing disclosed
role-compliant human review, package approval, human merge evidence or commissioning is
STOP.

At commissioning the Owner must enumerate all earlier applicable recovery
authorities (including R32, R34, PR #301 and PR #303), revocations, supersessions
and outstanding reservations across every channel they control, and personally
declare the inventory complete. Preserve each exact authority as a GitRef; retain
non-repository instructions in owner_source, without pretending they were commits.
Unknown or disputed entries block commissioning. This is an accountable human
completeness determination, not a claim that Git can prove global completeness.

After commissioning, the Owner is the sole issuer of recovery binding/succession
and selector decisions in this register; this issuance power is not delegated.
Review/custody appointments do not confer it. New positive authorizations are
ineffective until authenticated publication in the serial register. The Owner
must disclose every pending reservation and off-register instruction during fresh
verification. Any credible revocation, conflicting authorization or authority
uncertainty received through any channel causes immediate STOP, even before its
register publication. Register absence never overrides an actual stop/revocation.
The Owner records the resolution through the reviewed publication process before
work resumes. There is no unpublished positive-authority exception.

`admit-bootstrap` must reference exactly four approved CLEAN records and the exact
bootstrap amendment, declare its population-remediation effect prospectively,
and close admission for that set. Its required verification is identified only by
`bootstrap_verification`, under the validation rules below; `subjects`, `effect`
and source prose cannot substitute for that field. It neither authorizes PR #304
merge nor creates a second first-record entitlement. `close-bootstrap` records abandonment or final
completion and forbids reopening; record corrections preserve the same admission.
`authorize-binding` names an exact approved binding, baseline and applicable
supersession authority; a second live successor to the same predecessor is STOP.
`authorize-selector` names exact merged evidence bytes and Selector, and requires
separate reviewed publication authority; this process supplies no execution
procedure or permission. `supersede`/`revoke` name all affected prior decisions;
no restoration, authority renewal or silent approval-window extension is implied.

Distinguish an authorized selector decision from a verified installed selector.
The former never proves publication. Until separately authorized publication and
independent byte/custody verification complete, retain the prior installed state
(including absence) and treat the proposed selector as pending. Fresh verification
must reconcile the register decision, actual publication receipt and observed
selector; mismatch or an unfinished transition blocks operational use.

### Bootstrap admission verification reference

For `admit-bootstrap`, `bootstrap_verification` must be a non-null closed GitRef. Its
`commit` is the action-verification publication PR's verified actual merge commit, its
`path` is exactly
`docs/governance/operator-review-evidence/verifications/<record_id>.json`, and
`transport_sha256` hashes that record's complete canonical committed bytes, including
the one LF. The filename UUID must equal both record_id fields. Resolve one exact
regular `100644` blob; no branch name, directory search, source receipt, unpublished
draft, alternative schema or free-form reference is acceptable.

Before Owner admission and again immediately before its publication, the appointed
verifier must verify all of the following; any missing, mismatched, stale, unavailable
or ambiguous input is STOP, not permission to omit the field or reinterpret it:

1. The referenced record satisfies `aios-operator-action-verification-v1`, its
   closed schema, canonical bytes, authenticated attestations and post-merge
   publication checks. Its `classification` is `fresh-action-verification`,
   `verdict` is `PASS`, `action` is `bootstrap-admission`, and all four no-conflict
   booleans are true. Its selector fields are null.
2. Its `target` is exactly the held PR #304 candidate tuple in the bootstrap
   amendment: commit `e1a4459dc55ad9a15fe6dfc28dc11758a799c8c0`, path
   `docs/intelligence/stage-0.33c-p4s7-recovery-review-merge-evidence/records/1b8e3152-e315-43f4-9396-28776bd87947.json`,
   transport SHA-256 `11a609eaf580d3283b84d4994fb7f79a2995da6bab529ca722032f69c98523b2`.
   Authenticate its PR mapping separately; no future PR #304 merge is invented.
3. Its `bootstrap_review_records` contains exactly four distinct GitRefs in PR
   number order 299, 300, 302, 303. Each resolves at its actual verified publication
   merge to `reviews/<record_id>.json` under this archive, with exact transport
   digest and matching filename/record UUIDs. Each is an approved, published,
   unrevoked CLEAN `retrospective-revalidation` record for the amendment's exact
   corresponding HEAD/merge pair. The admission's `subjects` must equal this
   ordered array followed by the verification's `target` (exactly five GitRefs).
   The verification reference itself never appears in `subjects`.
4. Its `register_tip` equals the admission's `predecessor` as a complete GitRef,
   its `register_sequence` matches that entry, and the admission sequence is
   exactly one greater. Its `authority` identifies that tip, GD-008 and the exact
   approved bootstrap amendment; the admission's `governance_basis` identifies
   those same governance documents. Walk the pinned register to genesis and its
   exact predecessor_inventory and owner_source receipts. Fresh authenticated
   Owner confirmation must cover that same inventory, all subsequent decisions
   and off-register instructions, the target and the four review-record tuples.
   No repository-only completeness inference or unspecified inventory is allowed.
5. The verification's checks, reviewer acceptance, Owner approval, actual
   publication and role-disclosed post-merge verification are all complete before
   the admission's `decided_at_utc`. Retained current-dated publication receipts
   establish that ordering; no future publication timestamp is embedded in the
   verification itself. Require `checked_at_utc <= decided_at_utc < expires_at_utc`
   and that the admission's Owner approval and publication both occur before
   expires_at_utc and within all applicable authority windows. Perform section 5's
   final direct confirmation immediately before publication. An intervening
   register decision, revocation, superseded review, changed inventory, expiry or
   freshness failure invalidates admission and requires a new verification.
6. Neither the referenced verification record nor its action_id may have been
   used or reserved for another admission. Check the complete authoritative
   register and pending/off-register instructions with the Owner, reserve it for
   this admission's exact record_id, and serialize publication. A retry after an
   aborted admission requires a new verification record and action_id. Successful
   admission consumes this verification for that one admission only. Its own
   authorized append is the sole expected register-tip advancement; no unrelated
   intervening entry is allowed. It consumes no recovery installation authority.

For every decision other than `admit-bootstrap`, `bootstrap_verification` must be
present and null. These conditional rules are part of the closed schema; reject
unknown fields, missing fields, wrong types and any free-text replacement.

## 5. Fresh action / no-conflict verification schema

`schema_version = "aios-operator-action-verification-v1"`.
The closed payload has exactly:

| Field | Type / rule |
|---|---|
| `record_id`, `repository` | As above |
| `role_context` | RoleContext; required, digest-bound scope and combined-role disclosure under section 1 |
| `classification` | Exactly `fresh-action-verification` |
| `action_id` | UUID, unique to one proposed action; never a reusable PASS |
| `action` | `bootstrap-admission`, `evidence-review`, `evidence-merge`, `selector-publication`, `activation-creation`, or `installation-attempt` |
| `target` | GitRef to exact reviewed/merged artifact relevant to that action |
| `bootstrap_review_records` | Exactly four distinct GitRefs ordered by PR 299, 300, 302, 303 for bootstrap-admission, as validated in section 4; empty array for every other action, never null or omitted |
| `authority` | Nonempty array of GitRef to exact register decisions and separately approved action-specific governance |
| `register_tip` | GitRef to authenticated latest effective decision |
| `register_sequence` | Positive integer matching that tip |
| `checked_at_utc` | UTC of fresh verification |
| `expires_at_utc` | UTC, strictly later than checked_at; within every applicable approval window and separately approved action window |
| `selector` | Selector or null; required for selector-publication and later operational attempts; no invented future evidence merge |
| `selector_transport_sha256` | Digest of exact canonical Selector plus LF, or null iff selector is null |
| `owner_currentness_source` | SourceRef: fresh directly authenticated Owner statement naming register tip, action, subject, complete succession, and all known pending/off-register instructions |
| `verification_sources` | Nonempty array of SourceRef: checked review/publication evidence with actual verifier and role_context disclosure and complete register/predecessor walk |
| `complete_succession` | Boolean |
| `no_conflicting_successor` | Boolean |
| `no_competing_supersession_authority` | Boolean |
| `no_revocation` | Boolean |
| `verdict` | `PASS` or `STOP` |
| `limitations` | Nonempty string, including sources and scope of external verification |

PASS requires all four booleans true, authenticated Owner confirmation and appointed
human verifier acceptance for this exact action under section 1, including its
production boundary. A solo-mode PASS never supplies independent human acceptance or
production execution authority. A boolean is never proof by itself. Walk every register
predecessor to commissioned genesis, verify exact bytes/approvals and historical
authority inventory, and reconcile all recovery binding and supersession decisions,
revocations and the current selector decision. No skipped entries, forks, unexplained
gaps, stale pins or unsupported source claims. Compare the exact actual selector where
applicable; commissioning and bootstrap actions must use null rather than fabricate a
selector.

The Owner must serialize decisions and confirmations: disclose in-flight requests,
hold off issuing a competing positive decision while an action is pending, and
notify the operator of any stop/revocation immediately. Immediately before the
action, the operator recontacts the Owner over the authenticated channel and
rechecks the same tip, exact action, unexpired record and absence of new notices.
The action must be explicitly one-shot within its approved window. Any delay,
changed source, disconnected confirmation, intervening decision or revocation
invalidates PASS; retain STOP and obtain a new verification. An expiry time alone
never proves freshness. Retain the final confirmation receipt before the action.
If that cannot be done without making the verification stale, STOP. The fresh
confirmation and action linkage remain external operator gates; this process
does not claim atomic global revocation detection or introduce a runtime service.

The final confirmation receipt is a new immutable source file, bound to the published
verification's commit/path/transport digest and action_id. It is kept by the appointed
operator in the same protected working archive pending its next governance-only
publication; the operator and appointed verifier retain exact copies under section 6 (in
solo mode, the same Owner maintains the separate copies). This narrowly defined delayed
publication applies only to that final receipt, never a positive Owner authority
decision or an unapproved review record. Its custody, authentication and indefinite
retention follow section 6. Missing receipt, unavailable verifier or inability to
preserve it prevents the action.

## 6. Custody, publication, retention and corrections

The appointed human custodian prepares records and source receipts in a dedicated
local checkout of this repository. Owner-controlled access: no shared credentials;
working archive directories mode `0700`, files `0600`, no symlinks, exact exclusive
creation and no overwrites. The actual local checkout path is named in the Owner's
commissioning receipt; it is not a production/runtime path. Git publication uses
regular `100644` blobs at the fixed repository paths above. Git access controls
are supplementary custody controls, not acceptance evidence. No provisioning or
permission changes are authorized by this proposal.

Publication is a separate governance-only PR: add records/receipts only, validate
schemas/canonical bytes and source digests, authenticate each reviewer/Owner statement,
and obtain role-disclosed human review of the exact final PR head. A human merges only
after explicit Owner publication authorization naming that head and custodian. After
merge, the appointed verifier checks actual PR mapping, two-parent topology,
reviewed-head second parent and exact reviewed/merged bytes. Retain that factual
verification and authenticated publication approval as source receipts for the next
linked action or register entry, referring to the now-known publication commit. No
record embeds its own future merge. The initial record's use always requires these
post-merge checks; a later receipt is not a substitute for actually performing them.
Repository identity evidence and human acceptance must remain separately labeled
throughout.

Retain every published record, authentic receipt, failed review, STOP, revocation and
superseded version indefinitely in accepted history and an Owner-controlled archive
copy. Retain approved final confirmation receipts locally until publication and
thereafter under the same rule. No deletion, rewrite, force-push, garbage collection of
sole copies, or silent edit may erase an authoritative chain. Custodian and appointed
verifier retain separate exact copies of unpublished receipts. In solo mode the Owner
maintains both the protected working copy and a separate Owner-controlled archive copy,
records their actual locations in the commissioning receipt, and discloses common
custody; copies do not imply two humans or independent custody. Archive loss or
unavailable required records is STOP. There is no time-based expiry of historical
evidence; applicability/approval windows still expire and historical evidence never
renews them.

Review corrections create a new UUID and record their actual current creation time in
the review payload's `record_created_at_utc`. A review correction names
the exact prior review via predecessor and undergoes fresh acceptance/approval;
its use requires an Owner register decision superseding the old admitted record.
Original subject identities never change under a correction. New subjects need
new authority. Register entries are corrected only by a later explicit supersede
or revoke decision in the same serial chain; no sequence reuse. Action verifications
are never amended or reused: any new attempt gets a new action_id and record.
Sources are never edited; corrected statements use new source IDs and disclose
the earlier statement and reason. Preserve all conflicting records for audit.

For a review correction, preserve authentically established `reviewed_at_utc`
and `merge_occurred_at_utc` when retaining the same historical events; never
replace them with record-creation time. A historical value may change only when
a stronger independently authenticated source establishes the actual event time.
Retain that new source and explain the prior value, corrected value and evidence
in `findings`; keep the prior record immutable. If the necessary event time is
unavailable, use section 3's unavailability/STOP rule, not a fabricated date. A
newly performed permitted retrospective re-review uses its actual current
reviewed_at_utc and explicitly identifies the new review in review_source; it
does not backdate or relabel an original review.

New correction events use their actual current times: record_created_at_utc for
assembly, merge_verified_at_utc for fresh merge verification, and each new
reviewer_acceptance.at_utc and project_owner_approval.at_utc for those attestations.
The later Owner admission/supersession decision records its real decided_at_utc
and approval time. Record each new publication's actual time in its authenticated
post-merge source receipt under section 6, not in an invented future timestamp or
the subject's historical merge_occurred_at_utc. Creation and current verification
must be complete before new reviewer acceptance; Owner approval follows acceptance,
and publication follows its separate authorization. These rules change no
historical event, original authority window or retrospective allowlist.

Schema/version changes require separately reviewed, explicitly Owner-approved governance
and a defined compatibility boundary. Unknown versions are STOP; custodians cannot add
fields or reinterpret historical records in place. The required role_context is a
revision to these still-proposed v1 schemas, not a migration or certification of any
existing evidence. It adds one payload field to each class (19 review, 17 decision, 23
action-verification fields); the six-field envelope and canonical encoding remain
unchanged. No older record is implicitly upgraded, and historical source statements must
never be rewritten.

## 7. Boundaries and proposed validation gates

No populated record, appointment, approval, original review, commissioning,
no-conflict finding or operational permission is asserted by this specification.
Do not rely on it until GD-008 activation and commissioning. It does not change
PR #301's fifteen-field evidence schema, four-field selector schema, R34's
activation schema, executor/policy, fixed runtime or external freshness gate.

Before any later publication, the appointed verifier must reject extra/missing/duplicate
keys, wrong types, malformed IDs/times, noncanonical bytes, bad source hashes, false
identity claims, unappointed actors, undisclosed role combination, false independence
claims, out-of-scope solo authority, missing role_context, altered payloads, unavailable
human merge evidence, backdating, forked register chains, off-allowlist bootstrap
subjects, inappropriate nullable fields, stale action windows, changed selector bytes
and unsupported approval scope. Positive checks must authenticate real actors and
sources; synthetic tests or Git-only PASS are insufficient.

This proposal adds documentation only. Implementing validators, provisioning
custody, creating records, performing re-reviews, or publishing operational
artifacts are separate tasks requiring their applicable authorizations.
