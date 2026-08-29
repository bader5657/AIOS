# First-Write Input, Authority, Evidence, and Failure Contract

## Approved real input only

Synthetic production input is prohibited. The Project Owner must separately
supply or approve one real retained `IngestionResult` and all trusted facts.
The ingestion object must retain its exact input/recognized types, stored-path
identity if present, canonical manifest path, bounded metadata/text state,
handoff flags, registration/registry identity, event-delivery state, failure
code where applicable, and `brain_result=None`, satisfying the merged validator.
This is identity/state reconstruction from retained evidence, not permission to
select an arbitrary file path or fabricate an ingestion result.

The manifest must be an existing canonical regular non-symlink retained
manifest, named by its UUID identity, valid under the repository manifest
schema, selected by an evidence-governed procedure, and byte-bound by
`source_manifest_sha256`. No suitable real manifest or business facts are
identified by this package; retained-evidence readiness is therefore pending.

Exact `TrustedReceiptFacts` categories are:

- canonical supplier name;
- optional canonical document number and optional document date;
- timezone-aware received timestamp; and
- one to 500 items with unique positive line numbers.

Each item requires optional governed candidate description, canonical display
name, size, specification, and material UUID; nonnegative bounded full-colly
count; conditional positive bounded `qty_per_full_colly`; nonnegative bounded
partial quantity; positive bounded total quantity satisfying the exact packaging
formula; and unit exactly `sheet`, `pcs`, `kg`, `roll`, or `pack`. Sheet
quantities must be integral. Supplier/document identity, received time, item
identity/descriptions, material mapping, packaging quantities, and units must be
derived from retained evidence where support exists and otherwise explicitly
approved by the Project Owner. No values are invented here.

## Future authority model and immutable identity

A separate first-write governance publication must authorize exactly one
attempt and freeze:

- one `authorization_id`, artifact byte SHA-256, enabled window, and no retry;
- one canonical operator identity;
- one retained manifest reference and SHA-256;
- one canonical trusted-facts SHA-256 and the complete approved input identity;
- the exact ephemeral harness bytes/hash, reviewed commit, interpreter, Unix
  identity, and one-call invocation;
- the exact local production DB target, candidate runtime and writer roles, and
  `READ COMMITTED` single-transaction expectation;
- expected `material_receipts +1`, `material_receipt_items +N`, all
  `NEEDS_REVIEW`; and confirmation, posting, inventory and stock effects `0`;
- bounded execution-evidence location, identities, modes and hashes; and
- rollback, verification, deactivation, and forbidden-side-effect rules.

The governance authority, exact `authorization.json` bytes,
`authorization_id`, `consumed/<authorization_id>.json`, harness invocation, and
execution evidence must all name and hash-bind the same immutable authorization
identity. The artifact does not authorize itself. This readiness package creates
none of those authority objects.

## Execution evidence contract

The future evidence set must durably retain bounded semantic facts: governance
authority identity; reviewed commit and harness hash; authorization artifact
SHA-256 and authorization ID; safe operator representation; source-manifest SHA;
trusted-facts/input SHA; claim timestamp; claim and durability outcomes; whether
DB capability was attempted; candidate ID and `NEEDS_REVIEW` status; receipt and
item affected-row counts; confirmation, posting, inventory, and stock effects;
transaction outcome; error/result classification; and a bounded secret scan.

The implemented runtime evidence DTO carries authorization/source digests but
does not independently carry `trusted_facts_sha256`, transaction detail, harness
identity, or post-write assertions. The separately governed ephemeral harness
and evidence package must bind those additional facts without changing the
merged runtime model or storing unrestricted business content. PASS/status-only
evidence is insufficient; secrets and raw payloads are forbidden.

## Bounded post-write verification

The future authority must freeze candidate-ID- and authorization-bound queries,
not broad production SELECTs. Immediately after the attempt, using the least
privileged governed verification identity, verify the exact candidate ID/source,
one receipt, exact N linked items, every status `NEEDS_REVIEW`, creator actor
equal to the authorized operator, null confirmation state, and zero rows/effects
for posting/inventory/stock attributable to that candidate. Record transaction
outcome and bounded before/after counts or fingerprints. Verification does not
permit mutation, confirmation, posting, retry, or unrelated data inspection.

## Failure and deactivation policy

- Before `O_EXCL`, failure leaves the authorization unconsumed where the marker
  was never created; the cause must be corrected only under fresh governance.
- Successful `O_EXCL` permanently consumes the authorization, even if marker
  writing, fsync, process execution, repository construction, DB connection,
  transaction, or evidence finalization later fails.
- Marker write/file-fsync/parent-fsync failure prohibits DB capability.
- A DB transaction failure rolls back the receipt and all items.
- There is no retry, second authorization, marker deletion, repair, takeover, or
  automatic reauthorization.

After a successful first write, the authorized human/operator must remove or
replace `authorization.json` with a separately governed disabled state as the
future authority specifies. The consumed marker and historical execution
evidence remain immutable and retained. Runtime access is not widened, the
ephemeral harness is not installed, and candidate activation remains disabled.

Project Owner approval remains separately required for real business input,
first-write authorization, and privileged filesystem provisioning. Publication
of this readiness package is none of those approvals.

## Exact seven-step post-merge sequence

Progression is frozen as seven distinct governed steps in exactly this order:

1. **Resolve runtime secret / caller prerequisites.** Establish, without
   exposing secret values, the runtime Unix identity, runtime DB role, writer DB
   role, credential-mechanism availability, candidate DB secret metadata
   readiness, and caller execution-context requirements. This step performs no
   filesystem provisioning, harness creation, or production DB write.
2. **Govern and provision filesystem prerequisites.** Under a separate
   provisioning authority, establish the required safe, real, non-symlink path
   components beneath
   `/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/`,
   including the eventual authorization-file parent and consumed directory,
   with frozen owner, group, mode, and exact-runtime write capability. Do not
   create an active `authorization.json`; this step grants no write authority.
3. **Govern and build the ephemeral one-shot harness.** Use a separate
   governance, implementation, and review boundary. The harness must be
   ephemeral, one-shot, and non-permanent; must invoke only the merged
   `controlled_create_review_candidate`; and must not be HTTP, Telegram,
   Universal Ingestion automatic wiring, a scheduler, or agent-autonomous. This
   step selects no real input and executes no production write.
4. **Select and approve real retained evidence and trusted business facts.** Bind
   a real retained ingestion manifest/reference and SHA-256, and obtain Project
   Owner approval for supplier, document, timestamp, item-line, quantity, and
   governed-unit facts. Synthetic production data remains prohibited. This step
   creates no write authority.
5. **Publish a separate first-production-write authority.** Only after Steps 1–4
   independently complete, publish an authority for exactly one attempt binding
   the exact authorization ID, operator, retained-evidence SHA, trusted-facts
   SHA, harness identity/hash, source/main commit, runtime Unix identity, DB
   runtime/writer roles, transaction contract, expected receipt `+1`, items
   `+N`, `NEEDS_REVIEW`, zero confirmation/posting/inventory/stock effects,
   evidence requirements, and no retry. Publication does not execute a write.
6. **Independently review and merge that first-write authority.** Require fresh
   independent PASS, unchanged authority HEAD, merge, source synchronization,
   and every immediate activation gate. Publication alone is inactive, and no
   production write occurs during review.
7. **Execute exactly one bounded production write.** Only after Steps 1–6 PASS,
   execute one governed candidate-create attempt. There is no retry, second
   authorization reuse, broad production activation, confirmation, posting,
   inventory mutation, or stock mutation.

Combining Step 1+2, Step 2+3, Step 3+4, Step 4+5, Step 5+6, or Step 6+7 is
explicitly prohibited. No other collapse, skip, reorder, or implicit combination
is permitted. Every step has its own completion evidence and governance
boundary. If any step is incomplete or blocked: **STOP**. Do not advance, and do
not infer conditional authority or use “continue if practical” discretion.

Classification `D. RUNTIME_SECRET_OR_CALLER_PREREQUISITE_REQUIRED` is preserved:
Step 1 is the current unresolved step. Steps 2–7 remain mandatory and separate.

## Safety statement and next step

During this closure: production PostgreSQL contact `NO`; production DML `NO`;
production authorization creation `NO`; consumed-root provisioning `NO`;
candidate creation `NO`; `runtime.env` modification `NO`; service restart `NO`;
Telegram change `NO`; Universal Ingestion change `NO`; activation `NO`.

The immediate action is fresh independent review of this remediated documentation
PR. If and only if PR #264 is approved and merged unchanged, the next official
action is exactly Step 1—resolve runtime secret / caller prerequisites. Do not
jump to Steps 2–7. No first-write authority is created and production candidate
activation remains unauthorized.
