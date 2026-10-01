# Stage 0.33C reconciliation implementation and validation package

Status: PREPARED, UNCOMMITTED, NOT EXECUTION-AUTHORIZED. No mutation test has run.

This package implements the reviewed plan as an exact controlled-operation program
and syscall-level procedures, with a pure semantic ledger replay and phase predicates. It is not a
production command-line runner. The normative implementation is 01 + 02 + 04;
03 is a side-effect-free dispatcher, not a substitute for the operation contracts.
No operator may translate this into ad hoc shell commands or weaker filesystem
primitives. A concrete syscall adapter must be reviewed and bound to the same program
before isolated fault testing and execution approval. That adapter is not supplied or
approved as a production executable by this preparation-only package.

The current detached HEAD is b5fa2acaa66db799ebd8ec03d2a06a04e34753a2.
The only proposed target is PR306 merge efe859b2ae74b339c93fb3d6986ac6f2407a154c.
No moving branch is an execution input. Sequence5 is effective for governance
preparation only. PR304 remains the exact future evidence predecessor; R34 remains
operational baseline. Bootstrap stays closed. No schema/reader/policy amendment,
production-risk waiver, authority renewal, activation or installation is supplied.

Artifacts:
- 01_OPERATION_PROGRAM.json: exact authority bindings, copied closed allowlist,
  finite operation schedule, immutable custody baselines, and release gates.
- 02_CONTROLLED_OPERATIONS.md: exact ordered operations, pre/postconditions,
  syscall contracts, ledger serialization/durability and interrupted-step rules.
- 03_state_machine.py: pure semantic forward/rollback replay, immutable-event validator and phase predicates.
- 04_ROLLBACK_RECOVERY.md: complete identity-based forward/reverse state tables.
- 05_FAULT_INJECTION_PLAN.md and 06_FAULT_CASES.json: isolated validation procedure,
  mutation boundary cases, expected retry/rollback/STOP results and pass criteria.
- 07_test_state_machine.py: prepared pure dispatcher regression tests; not run.
- 08_COMPATIBILITY_AND_ACCEPTANCE.md: compatibility matrix, stop gates, clean-state
  criteria, production authorization and exact next review sequence.
- 09_PACKAGE_MANIFEST.json: exact artifact hashes and static preparation results.
- 10_fault_inventory.py: reproducible static symbolic inventory compiler; reads01 and
  writes06 only. It cannot issue runtime syscalls, import the dispatcher/tests, or
  create an adapter, release, or execution authority.

Private local preparation files are 0600, directory 0700. No runtime/control-area
path is created. All source snapshots and historical receipts remain unchanged.
The future external operation root is reserved by the published proposal; it is not
this package directory. The package does not populate index.after, stage Git objects,
copy deployment content or allocate a future successor binding ID.

Next: review these exact local artifacts. A committed exact-HEAD publication review
requires separate candidate-preparation authorization because commit/PR creation is
not authorized in this turn. Execution requires the additional gates in 08.

Revision H1/M2–M5 retains the exact 79 operations and published creation/rollback
allowlists. Baseline alias groups are derived from approved identities. Semantic replay
validates closed evidence snapshots and immutable barrier history. Final rollback uses
PRE_ROLLBACK_SEAL, SEAL:ROLLED_BACK, then read-only POST_ROLLBACK_TERMINAL.
01 enumerates normative occurrences;06 contains 149,873 applicable fault cases.
07 contains 89 prepared behavioral test functions / 2,378 expanded cases.
Tests remain PREPARED / NOT RUN. Static syntax/schema/hash checks do not establish
execution safety or passing crash recovery. See05 for the exact inventory.

Manifest convention:09 lists every OTHER package artifact exactly once, sorted by
repository-relative path, and never lists/hashes itself. Canonical JSON is UTF-8,
ensure_ascii=false, sorted keys, compact separators, no NaN/Infinity, one trailing LF.
Reject missing, extra, duplicate or reordered entries; reject symlink/nonregular
package inputs. A detached review digest is SHA-256 of the canonical object:
{"format":"aios-detached-package-review-v1","manifest_path":<09 repository path>,
"manifest_sha256":<SHA-256 of exact09 bytes>,"artifacts":<exact09.files array>}.
Artifact ordering is part of that digest. It binds exact manifest bytes AND every
listed path/hash. The detached value is delivered in the revision report, outside
the package, avoiding a recursive self-hash. Recompute it after any package edit;
a change invalidates the prior review binding. The detached digest is not a package artifact;10 is the inventory compiler.


Revision M2/M4/M5: malformed evidence has typed validation before semantic use and
stable STOP failures; fault cases use unique persistent-effect crash boundaries;
all 12 metadata recovery rows have real ledger/rollback fixtures for both metadata
subjects. This revision preserves H1 aliases, M3 seal order and the L1 digest format.
No test import/collection/execution, adapter, runtime change or execution authority.

M4-only follow-up rebuilds rollback fixtures from three exact forward cuts and the
normative rollback schedule. Every primitive starts after its durable BEFORE. Global
semantic-state fingerprints replace label-local deduplication and retain every
originating fault-site ID. Counts are recomputed, not carried forward. H1, M2, M3,
M5 behavioral coverage and L1 self-exclusion/detached binding remain intact.01–04
and08 are unchanged by this follow-up. See05 for definitions and static results.

M4 semantic revision: durable proof is derived from surviving ledger files, independent
of writer bookkeeping and fsync return position. Realizable ledger metadata/content/
replacement faults are retained. Every injected filesystem transition is replayed;
impossible outcomes are INVALID_FILESYSTEM_REALIZABILITY exclusions. Full independent
validation includes ledger-file effects and recovery recomputation. All 53 M4 regression
functions remain prepared, not run.01–04 and08 remain unchanged. See05 for fresh counts,
exact physical-state fingerprints, exclusions and retained coverage obligations.


Current M4 revision removes initialization proof inferred from writer state. Trust is
NONE until a surviving accepted record or explicitly bound governed external witness
proves a baseline; no external witness is supplied by this package. Namespace faults
select approved concrete descendants by capability while retaining predicate scope.
Unavailable bindings remain UNBOUND_COVERAGE_OBLIGATION entries with origin and binding
requirements. Full static accounting and independent physical-proof/recovery grouping
precede global semantic deduplication. See05 for current counts and prepared regressions.
Revision only: no tests, adapter, runtime changes, commit, PR or execution authority.


Final M4-A/B correction requires explicit role-compatible targets for every injected
filesystem mutation and partial write. Full-status verification now selects a regular
child for same-hash replacement. Held-descriptor type impossibility precedes missing
object/path/byte bindings; unbound obligations retain independently checked conditional
physical realizability. Durable proof, global deduplication and H1/M2/M3/M5/L1 remain
unchanged. This is revision-only preparation for re-review, without tests or execution.
