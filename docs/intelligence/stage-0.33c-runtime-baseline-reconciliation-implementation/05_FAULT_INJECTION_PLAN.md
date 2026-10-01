# Isolated crash/fault validation plan — NOT RUN

No production crash test, restart, object import or probe mutation is authorized.
This is a test specification. A separately authorized disposable fixture must have
NO mounts, symlinks, credentials, sockets, systemd/DB access or network route to AIOS
production. Fixture paths must be rebased injectively from exact approved paths;
reject overlaps and any production prefix. Rebase identities from fixture lstat,
never substitute production inode numbers. Preserve path topology, modes, hardlink
semantics, file content requirements and directory creation order. Use synthetic
nonsecret auth-custody sentinels. Do not copy real authentication evidence/env/DB.
A later filesystem adapter must enforce this containment independently of test code.

Before testing, freeze adapter binary/source hash, OS/kernel/filesystem/mount options,
Git/Python/zlib versions, fixture manifest, generated standalone target index bytes,
canonical compressed-object streams and target graph. Source Git object reads and
fixture population require separate authorized scratch preparation. No git writer
runs in /opt/aios-src; no test runner uses production operation root.

In a separately authorized run, exercise every originating fault site in06 in a
fresh retained fixture (no ambiguous reuse). Deduplicated cases share a surviving-
state/recovery oracle; merging cases does not waive any fault-injection origin. Fault hook
labels in02 have BEFORE and AFTER variants around each syscall, fsync, event append,
completion marker and state seal. Also inject partial writes, EINTR, ENOSPC, EIO,
EEXIST, EXDEV, unsupported rename flags, clock regression, directory rename races,
unknown inode with matching hash, symlink at every ancestor, and concurrent Git lock.
SIGKILL demonstrates process-interruption behavior only. Power-loss durability needs
an isolated VM/filesystem with deterministic disk fault or power-cut simulation;
process exit alone is not proof that fsync ordering survives power loss.

For each case record: exact program/adapter/release hashes, seed, operation ID,
microstep, injection position, before map, durable ledger prefix, observed namespace
and anchors, restart choice, actual syscall trace, after map, git status bytes,
protected sentinel hashes/inodes, and terminal classification. Retain full raw
fixture evidence in a separately approved test archive; do not invent runtime ledger
paths for tests. Tests fail on any unlisted write syscall or command.

Oracles:
- Proven-before: perform the one missing operation; no duplicate link/exchange.
- Proven-after without DONE: fsync/reverify and record completion, no mutation replay.
- Already DONE/sealed: verify postcondition and advance/no-op, no duplicate mutation.
- Unprovable/torn/orphan: STOP, preserve every byte; no guessed repair/deletion.
- Approved rollback: reverse exact proven subset using04, restore old detached
  HEAD/index bytes/inodes and the intentional two-entry dirty state; keep objects.
- Terminal VERIFIED/ROLLED_BACK: inspection only. A changed terminal invariant is
  STOP/new incident, never silently rerun forward or rollback.

Mandatory scenarios beyond individual microsteps:
1. Kill during each of62 object operations, including valid subset, torn compressed
   stage and valid stage with absent destination. Retain imported objects on rollback.
2. Each fanout created without object; D010 created without child; unexpected existing
   empty directory. Only proven D010 may quarantine, fanouts retained.
3. Each F subset of size0..3. Reverse only actually published inode-proven subset.
4. Index swap complete, HEAD old, plus every index.lock/quarantine interruption.
5. HEAD advanced with incomplete/corrupt index or missing ancillary file: fail CLEAN;
   restore only if original/candidate ownership is provable, otherwise STOP.
6. Every forward state boundary, before/after state-seal fsync; every rollback step.
7. VERIFY failure before seal and invariant loss after VERIFIED. Never claim success
   on the former or auto-reverse the latter.
8. Same-hash foreign inode at each creation/lock/quarantine path, symlink traversal,
   mount/device mismatch, auth sentinel change, process identity change and loss of
   custody. Preserve foreign content and STOP.
9. Prepared index deliberately wrong tree/flags/extensions, object correct raw hash
   but wrong Git OID/type/length, trailing compressed bytes, changed package/window.
10. Ledger duplicate keys, bad canonical LF, broken predecessor hash, gaps, duplicate
    ordinal, wrong attempt, forged DONE and stale clock. No tail truncation.

All seven user-required failure classes must have both retry and rollback outcomes,
where identity-proof permits them, plus ambiguity STOP outcomes. Test report must
separate passed, failed, not-run and inapplicable cases; zero unexplained cases and
zero writes outside finite allowlists are required. Failing/torn infrastructure does
not entitle the harness or operator to reset a production attempt.

Prepared pure-model tests in07 require a separately authorized test run. They exercise
control decisions only and do not establish filesystem/power-loss safety. A possible
later invocation is Python -B with pytest cache/bytecode disabled in the disposable
fixture, using a separately reviewed harness; no such invocation was run here.

## Rebuilt occurrence inventory (revision M4)

06 is regenerated from 01's ordered syscall_occurrences and the ledger EXCLUSIVE_FILE
contract. It includes initialization, forward/rollback effects, phase predicates,
every ordinary ledger append, permitted STOP replacements and post-terminal checks.
Each case names a canonical semantic-state fingerprint, recovery outcome and all
originating fault-site IDs. Each origin resolves to its fixture, normative site ID,
exact call ordinal/action/path/role and failure mode. Fixtures bind a validated
durable prefix and exact ordered calls. Names/ordinals resolve from that prefix.
Rollback fixtures name an exact forward cut and selected plan; retain-forward uses
the actual interrupted exchange row. No-op barriers remain required.

The applicable count is **149,873**. This is a plan inventory, not tests run or passed.
All action-inapplicable fault combinations are explicitly excluded in06. The normal
operation sequence does not authorize unlink/chown, unflagged rename or chmod of
existing entries. Symbolic fault actors may use physically realizable mutations
outside that sequence to model corruption; this does not authorize runtime writes.
Hash checks on directories and STOP appended after terminal/STOP or through a malformed
tail are excluded. Reopen/read/hash/fstat after fsync
is included for each created regular file and every ledger record. Separate ancestor
checks, flock, parent fsync, and phase validation have named occurrence sites.

STOP fault fixtures replace an intended ordinary append at a valid nonterminal
prefix. They do not append through a failed/torn event. A complete durable STOP halts;
absent/torn STOP still means preserve and STOP, never forward resume or recursive
STOP. Successful short-write/EINTR handling finishes the same buffer then halts.

TERMINAL_INVARIANT_LOSS now starts after SEAL:VERIFIED or SEAL:ROLLED_BACK and injects
drift immediately before read-only terminal verification. Its expected result is
STOP/new incident authority, with no ledger append or filesystem repair.

Read/hash/index/tree/graph checks are explicit semantic action sites. Their internal
read syscalls and per-object validation must be expanded and bound during future
adapter review; this source-level occurrence count makes no claim to be the count of
kernel syscalls. No unlisted write is permitted. The approved fixture must materialize
the exact maps from replay and retain the program/adapter/context/seed binding.

## Prepared behavioral tests (revision M5)

The general behavioral suite remains 36 functions / 2,269 parameter-expanded cases.
The complete current suite has 89 functions / 2,378 cases, counted statically from AST
decorators and exact program cardinalities. No test import, collection or execution.

- `test_full_real_program`: 1
- `test_exact_retry_action_at_every_completion`: 459
- `test_pending_effect_classification`: 295
- `test_barrier_and_state_retry`: 8
- `test_baseline_alias_membership_and_linkcount`: 6
- `test_alias_corruption_stops`: 48
- `test_unapproved_inode_sharing_stops`: 1
- `test_each_barrier_metadata_drift`: 64
- `test_missing_seal_blocks_next_operation`: 7
- `test_duplicate_seal`: 8
- `test_missing_operation_completion`: 79
- `test_duplicate_completion`: 79
- `test_semantically_invalid_evidence`: 12
- `test_structural_chain_rejection`: 6
- `test_all_metadata_rows`: 24
- `test_invalid_metadata_combinations`: 500
- `test_pre_and_post_rollback_barriers`: 9
- `test_partial_objects_with_real_history_and_rollback`: 63
- `test_reachable_ancillary_subsets_with_barriers`: 4
- `test_unreachable_ancillary_subsets_stop`: 4
- `test_contradictory_terminal_evidence`: 2
- `test_terminal_observation_loss`: 2
- `test_durable_stop_is_terminal`: 1
- `test_execution_release_is_not_created`: 1
- `test_semantic_event_order_and_seal_regressions`: 6
- `test_missing_rollback_barrier_cannot_be_supplied_by_caller`: 8
- `test_metadata_rollback_target_and_order`: 3
- `test_exact_phase_git_predicates`: 32
- `test_each_rollback_barrier_rejects_inconsistent_evidence`: 45
- `test_head_only_incomplete_cannot_be_accepted`: 1
- `test_preseal_has_no_terminal_and_postseal_requires_terminal`: 1
- `test_partial_directory_history_and_rollback`: 4
- `test_object_evidence_must_match_exact_rule`: 3

Tests use the real 79-operation program and baseline-derived identity/alias fixtures.
They assert exact choices, reconstructed histories/maps, barrier results, STOP reasons,
rollback targets, metadata rows and invalid combinations. Closed evidence mutations,
terminal contradictions, alias splits/counts/metadata, missing/duplicate/reordered
events/seals/barriers and partial-object/directory/ancillary histories are covered.
Only four ancillary subsets are reachable in the ordered program (none, F001,
F001+F002, all three); the four non-prefix subsets are STOP cases, not legal fixtures.
Prepared tests remain unexecuted. Their existence does not establish passing behavior,
filesystem compatibility, power-loss durability or authorization.


## Preserved mandatory durable rollback prefixes

10 is a static data compiler. It reads the unchanged normative program in01; it does
not import03 or07, execute tests, open runtime paths, or provide syscall execution.
The compiler symbolically replays the full forward schedule, then these three cuts:

- `FINAL:DONE:SEAL:HEAD_RECONCILED`: normal full rollback.
- `M_HEAD:AFTER:M_HEAD.002.exchange`: retain the interrupted HEAD forward-old inode,
  then execute the selected remainder of rollback.
- `M_INDEX:AFTER:M_INDEX.002.exchange`: retain the interrupted index forward-old
  inode, restore index and ancillary entries, with the required no-op HEAD barrier.

Each branch includes INTENT, ENTER, every selected BEFORE/AFTER/DONE, all subject
barriers including no-op subjects, PRE_ROLLBACK_SEAL, SEAL:ROLLED_BACK and terminal
inspection. Later primitives are also inventoried under each applicable branch.
The12 formerly defective primitive families are: HEAD and index retain_forward,
link_original, reverse, retain_candidate; F003/F002/F001 quarantine; D010 quarantine.

The old pending-BEFORE recipe is removed. Ledger-writing fixtures start at the exact
prior durable prefix; primitive syscall fixtures start only after the matching
BEFORE is durable. The syscall trace then folds each actual namespace/inode effect.
AFTER-writing fixtures retain the completed effect with BEFORE still last durable;
DONE and subsequent barrier/seal fixtures follow their actual predecessors. Separate
origin IDs cover writing BEFORE, after durable BEFORE before syscall, every syscall
failure/crash, and all completion boundaries. Equivalent surviving states may share
a case, but never lose an origin. Every fixture is semantically prefix-validated
before admission, with an independent static replay audit of the generated data.
Source presence, destination absence, exchange identity presence and D010 emptiness
are checked during the symbolic fold. Rejected generated outcomes are retained in candidate_exclusions using the explicit taxonomy below; malformed normative fixture prefixes fail compilation.

## M4-1: durable proof comes from surviving files

The v7 inventory has one canonical `ledger_files` content root. Each retained file
binds its path, inode identity, dev/ino, uid/gid, mode, type, nlink and exact content
hash or symlink target. File leaves are stored in sorted blocks of32 for compactness;
block structure is canonical and does not depend on insertion or fault order.
The compiler and independent scanner separately memoize only fully validated blocks,
keyed by incoming proof root, proved snapshot and immutable block hash. Any file
change invalidates that block; cached rejection or bookkeeping does not supply proof.

`durable_proof_state` records source NONE, EXTERNAL_BASELINE or LEDGER, the
evidence-derived base snapshot, accepted record count and any rejection reason.
With no accepted durable record and no separately governed surviving external witness,
the base and last-proved snapshot are null. Planned baselines, writer observations,
fixture defaults, intended targets and initialization completion do not supply proof.
The first accepted surviving canonical record binds its actual before snapshot; later
records must satisfy exact continuity. A partial, missing or untrusted first record
cannot establish that baseline. Restart without initialization proof is STOP_RECOVERY_REQUIRED. The scanner derives it from the actual surviving
files, their exact bytes/metadata, filename/ordinal/predecessor chain and evidence
continuity. Complete, trusted canonical records contribute proof even when the crash
preceded the parent-fsync return, IF those exact complete bytes and metadata survive.
Partial/malformed bytes do not contribute proof. Wrong metadata, replaced ledger
inodes, chain/path divergence and files after a terminal record require halt.

`pending_ledger_file` is internal writer bookkeeping only; it never enters a survivor
fingerprint. A parent fsync adds no record bytes or persistent marker in this protocol.
Identical fully persisted before/after-parent-fsync witnesses therefore have identical
ledger roots, last proved snapshots, STOP/seal state, recovery classes and case IDs.
This does not claim that every pre-fsync write survives a power failure. Cases bind
one exact persistence outcome; loss/partial outcomes remain distinct and must be
explicitly represented. No extra durability marker or execution authority is created.

In an established ledger, STOP continues to serialize only the last proved snapshot, with null after/after-parent/
link-change fields and UNKNOWN_RETAIN. Actual state remains separate. Recovery is
recomputed from scanned proof: malformed retained bytes => STOP_TORN_RECORD; untrusted
ledger metadata/chain => STOP_RECOVERY_REQUIRED; unproved effects => STOP_AMBIGUOUS_EFFECT;
durable STOP/revocation/known failure => STOP_PRESERVE when no ambiguous effect exists.
All STOP classes halt. Terminal records permit inspection only. Successful short-I/O
handling in a healthy live invocation may continue the same call; a clean proved
prefix may follow only its prescribed continuation under separate valid governance.
Neither direction nor a fixture label supplies recovery authority.

## M4-2/3: realizable fault witnesses before acceptance

The blanket ledger-path exclusion is removed. Ledger files use the same existence,
traversal, identity and transition checks as other modeled files. Wrong mode, owner,
group, content, hardlink count and foreign replacement are generated where realizable,
including newly created and already durable ordinary/STOP records. Fault injection is
allowed to violate normal-operation preconditions; its own physical transition must
still be possible. Unavailable approved object/Git byte witnesses remain separately
reported UNBOUND_COVERAGE_OBLIGATION entries, not accepted coverage.

Every filesystem disturbance has an origin-linked `fault_operations` sequence outside
the semantic key. These are symbolic isolated-fixture actor operations, not permitted
runtime commands. The contracts represent fchmod/fchown, exclusive create plus bound
full-content write, ftruncate plus bound full-content write, mkdirat, symlinkat, linkat,
unlinkat/rmdir and flagged rename operations. Existing content can be copied with its
exact full hash; unavailable partial prefixes are never guessed from that hash.

A separate filesystem replay validates the sequence before accepting its outcome:
- `/` remains the directory traversal root; it cannot be removed or replaced.
  Noncanonical aliases such as `/.` are rejected before applying any operation.
  Declared mount anchors (including same-device bind mounts) and device-boundary
  anchors cannot be renamed, removed or replaced. This fixture declares no nested
  mounts; a mounted deployment requires a separately bound topology.
- Every present entry has a present traversable directory parent. Noncanonical paths
  and invented children below missing/non-directory parents are rejected.
- Creation requires absence; mutation/removal requires an existing compatible target.
  A held inode cannot change file type merely because its pathname was replaced.
- Link requires a regular source, absent destination and compatible device. Directory
  hardlinks are rejected. A directory link-count fault creates an actual child directory.
- Rename requires valid endpoints and same-device parents, cannot move root or a
  directory into itself, and observes NOREPLACE/replacement rules. Moving a directory
  retains every modeled descendant; crossing a mounted subtree is rejected. The
  bound fixture is one filesystem with no nested mount points.
- A directory replacement first retains the old tree at an explicit sibling name,
  then creates the replacement. rmdir requires an empty directory. File/directory
  replacement mismatches are rejected. Normative exchanges use existing regular
  metadata endpoints; no unbound directory-tree exchange is accepted.
- Symlinks are created by symlinkat at reachable non-root paths; regular-file races
  use an explicit temporary symlink plus rename. Linux symlink mode is0777.
- Inode identities, hardlink membership and directory-child link counts remain
  consistent. No fault label alone changes namespace or inode state.

Violations are excluded as INVALID_FILESYSTEM_REALIZABILITY with an explicit reason
and origin ID. They never enter accepted coverage. UNBOUND_COVERAGE_OBLIGATION
entries retain missing path/object/prefix bindings and are neither accepted coverage
nor physical impossibilities. INVALID_COMPILER_CASE is reserved for compiler contract
failures; action-inapplicable exclusions are counted separately. Neither exclusion category is a passed or executed test.

## M4-4: validation, canonicalization and accounting

10 reads01 and writes06 only. It imports neither03 nor07. Generation checks the
normative fixture prefix and mandatory BEFORE; checks full closed evidence and STOP/
terminal semantics; validates actual filesystem realizability; derives canonical
physical-file proof and recovery; then independently checks every origin against its syscall prefix, fault-operation
witness and recovery requirement before inserting the semantic state into one global
map. Partial-write validation also proves that no unrelated namespace or file changed.
A complete independent pass replays both ordinary filesystem calls AND ledger-file
creation/write/chmod boundaries, replays each injected operation sequence, rescans
physical evidence and independently recomputes every accepted origin's recovery.
There is no omitted ledger path in that pass. Mandatory BEFORE is verified at the
fixture start. If an injected ancestor rename later moves the ledger away, the
witnessed loss is retained as a halted case; the validator does not demand that
the destroyed/moved proof remain at its old path. An unchanged ledger must still
end at the required BEFORE throughout the primitive fixture.

The fingerprint is SHA-256 of finite sorted compact UTF-8 JSON with one LF. Persistent
inputs include the exact physical ledger files, derived ledger proof, proved snapshot,
actual namespace/inode/content state, Git HEAD/index/worktree roots, persistent controls,
markers/seals/STOP and recovery-relevant uncertainty and final class. Component preimages
are retained and checked. SHA-256 is the declared content-identity assumption; equal
hashes are additionally checked for equal available preimages during compilation.
Direction, fault names, syscall annotations, ephemeral descriptors and writer bookkeeping
are excluded. Origin IDs and injected syscall witnesses remain auditable outside the key.

| Inventory accounting | Count |
| --- | ---: |
| Raw candidate combinations | 4,250,190 |
| Syscall-inapplicable exclusions | 3,647,236 |
| Invalid compiler exclusions | 0 |
| INVALID_FILESYSTEM_REALIZABILITY exclusions | 48,349 |
| Unbound coverage obligations | 2,549 |
| Accepted candidate origins | 552,056 |
| Semantic equivalents removed | 402,183 |
| Final deduplicated applicable cases | 149,873 |
| Unique persistent semantic states | 149,873 |

Raw minus inapplicable minus invalid compiler minus invalid filesystem realizability
minus unbound coverage obligations minus semantic equivalents equals final cases. Final cases equal unique canonical
persistent/recovery states. Counts are regenerated from the complete candidate set.
All12 rollback families retain valid BEFORE prefixes. STOP evidence, H1 aliases,
M2 typed validation, M3 rollback seals and existing M5 behavior remain unchanged.

## M4-5: prepared regressions — not run

53 M4 functions / 109 parameter-expanded cases; the36 existing general functions /
2,269 cases are preserved byte-for-byte. The total is 89 functions / 2,378 cases.
Coverage includes the existing STOP schema/last-proof/halt checks, all12 rollback
families, partial ledger byte distinctions, process/power equivalence, namespace
separation, canonical fingerprints, complete stored origin mappings, and normative
ledger replay. New focused cases cover parent-fsync equivalence; complete records
independent of writer bookkeeping; valid wrong-mode/owner/group ledger faults;
impossible root replacement and held-descriptor type changes; missing parents,
directory hardlinks, same-inode rename no-op, nonempty rmdir,
cross-device rename, mount-anchor removal, same-device bind-mount movement,
file/directory replacement mismatch and missing exchange endpoints; valid ledger symlink replacement;
absence of the blanket ledger exclusion; and realizable ledger-ancestor loss after
a valid BEFORE prefix. Further regressions move a completed record between internal
pending/committed representations and reject unwitnessed namespace changes at the
acceptance gate. Expected recovery is independently
recomputed by scanning physical files, not trusting the compiler's supplied proof class.

These regressions are prepared only. Static data compilation, the complete generated
outcome audit, AST/cardinality checks, scope-preservation checks and artifact digest
verification do not execute them or establish runtime/power-loss safety. All adapter,
isolated testing, release and governance prerequisites in08 remain unchanged.

Additional prepared tests (counted statically, not run):
- test_malformed_string_fields_stop_before_semantic_dispatch: 450
- test_malformed_nested_evidence_has_exact_stop: 32
- test_cross_direction_microstep_is_rejected_before_lookup: 1

The 500 invalid metadata combinations also construct a real replayed index prefix,
inject contradictory identity observations and assert the exact identity/absence STOP.
The 24 valid metadata-row cases assert reconstructed state, next action, remaining
rollback primitives, exact original-live and quarantine targets, alias preservation,
pre-seal barrier and terminal verification. Existing partial object/ancillary histories,
terminal evidence contradictions and observation-loss cases remain behavioral.


Root-child races use canonical sibling names under `/`; joining `/` never creates `//` artifacts that discard realizable faults. Unbound graph/object predicate byte witnesses are UNBOUND_COVERAGE_OBLIGATION entries, never claims of filesystem impossibility. Prepared regressions cover both distinctions. The independent transition validator owns its immutable witness cache; every candidate is bound to its normative prefix and exact witnessed result before acceptance. The complete audit rehashes all components before reusing these independent proofs.

Static inventory coverage verification: 3800 parent-fsync survivor pairs share case IDs. Retained ledger-origin counts: CONTENT_HASH_MISMATCH=1900, SYMLINK_REPLACEMENT=1900, WRONG_GROUP=7600, WRONG_MODE=7600, WRONG_OWNER=7600. No tests were imported, collected or executed.


## Current M4 revision: initialization proof, concrete roles and coverage obligations

An external baseline is optional, separately authenticated evidence. The default
binding registry is empty and every generated case has no external witness. Neither
this compiler nor this revision approves one. A future witness must bind the exact
program, attempt root and snapshot, surviving evidence hash/preimage and governing
approval hash/preimage, with scope INITIALIZATION_BASELINE_PROOF_ONLY. Its reference
must also occur in the separately authenticated allowlist. Mere booleans or a supplied
base snapshot are insufficient. The production adapter must authenticate that allowlist
and confirm surviving durability; the symbolic model conveys no execution authority.
Prepared regressions exercise a hypothetical bound witness and reject absent bindings,
missing evidence, mismatched approvals, wrong program/scope and nondurable claims.

Whole-namespace verification records namespace_scope_anchor separately from concrete_fault_target in each fault_target witness.
Concrete witness roles select live approved descendants: regular_content,
regular_hardlink_source, regular_metadata, regular_replacement,
regular_symlink_replacement or directory_replacement. Git/ledger/custody predicates
retain their specific subject semantics. Root paths used only to denote predicate
scope are not mutation targets. Actual directory-target calls retain directory
semantics. Selection cannot invent an approved path or substitute a foreign alias.
The independent checker derives capabilities from the operation witness, requires
approved membership and scope containment, then replays the exact syscalls.
All 33 formerly excluded whole-namespace content cases and 32 alias cases are rebuilt.

The v7 taxonomy is explicit:
- INAPPLICABLE: fault does not apply to the normative syscall/role; counted with reason.
- INVALID_COMPILER_CASE: compiler contract or validation failure; never accepted.
- INVALID_FILESYSTEM_REALIZABILITY: a concrete witness violates filesystem semantics.
- UNBOUND_COVERAGE_OBLIGATION: meaningful fault lacks an approved path, object bytes,
  exact prefix or Git transition. Preserve origin/fixture/call, predicate, variant,
  operation/microstep, normative cursor, program digest and required binding role.
- ACCEPTED: prefix, durable proof, realizability and recovery validated before semantic
  hashing; this means a prepared candidate origin, never an executed/passed test.
All rejected candidate rows are in candidate_exclusions. No obligation is discarded
or included in accepted counts. The former 868 release-stream binding exclusions
and unavailable exact-byte/Git witnesses use the obligation category.

Canonicalization derives proof from surviving evidence, validates the normative
prefix and concrete transition, independently computes recovery, then hashes and
globally deduplicates. Scope/target annotations and missing-binding metadata live
outside the semantic state. The complete audit independently groups actual snapshot,
ledger files, persistent controls and any bound external witness: every such group
must have one durable proof. Adding recovery-relevant uncertainty and recovery class
must yield exactly one fingerprint. Every accepted origin's recovery is also checked
against its actual disposition, so a caller-supplied recovery label cannot justify a
split. Complete candidate accounting covers accepted and all exclusion categories.

Prepared additions reproduce the reported initialization crash, wrong-owner and
link-count pairs; audit every physical proof group; reject fabricated proof/defaults;
exercise role-aware content, alias and metadata faults; retain scope as an anchor;
and distinguish missing bindings from genuine root/held-inode impossibilities.
No tests have been imported, collected or run. H1, M2, M3, M5 and L1 remain unchanged.

Realizable endpoint types without a bound replay contract (for example a symlink hardlink or mixed-type exchange) are obligations, not filesystem impossibilities. Unsupported syscall vocabulary is a compiler-contract error. These additions change no normal-operation authorization or baseline alias contract. The independent outcome validator also enforces a closed semantic-state schema, rejecting nonsemantic annotations.

Initialization record construction may contain verified live observations, including in an initial STOP record, but those observations supply no crash-surviving proof until the complete trusted record survives and is accepted. The prepared STOP regression distinguishes that initial no-proof frame from an established ledger whose STOP must retain the prior proved snapshot.

Static inventory coverage verification: 3800 parent-fsync survivor pairs share case IDs. Retained ledger-origin counts: CONTENT_HASH_MISMATCH=1900, SYMLINK_REPLACEMENT=1900, WRONG_GROUP=7600, WRONG_MODE=7600, WRONG_OWNER=7600. No tests were imported, collected or executed.


## Final M4-A/B revision: required targets and physical-first classification

All whole-namespace predicates include verify_full_status_and_custody as well as
phase, index/tree/worktree and terminal verification. Generic namespace mutations
select an approved live child by explicit role. Predicate-specific ledger, Git
metadata and protected-alias faults retain their exact subject bindings, including
subjects outside the representative worktree scope. The namespace_scope_anchor is
never an implicit concrete_fault_target. A missing eligible child is an explicit
UNBOUND_COVERAGE_OBLIGATION; there is no scope-root fallback.

Every accepted injected filesystem mutation and partial-write fault now carries a
closed fault_target with namespace_scope_anchor (null for a direct object call),
concrete_fault_target, predicate and witness_role. Content and Git-object corruption
require regular content-bearing files; hardlink witnesses require regular sources;
metadata witnesses require existing chmod/chown-capable objects; directory link-count
faults require a real directory child; replacement, symlink and exclusive-creation
roles bind compatible paths and parents. Filesystem replay checks the full operation
sequence, devices, inode identities, type constraints and resulting state.

Before semantic hashing, the independent origin validator rejects a missing target,
a role mismatch, an unapproved namespace child or any syscall using a namespace scope
anchor as its target/source. It checks capabilities from the concrete pre-fault state
and binds the target to the actual mutation syscall. Partial writes bind their exact
regular ledger file. Controls, crashes and no-effect errno outcomes do not acquire
invented mutation targets. Target/scope annotations remain outside semantic state.

Classification order is normative applicability, concrete bound-object physical
constraints, filesystem/syscall constraints, approved witness availability, then
acceptance. WRONG_TYPE on fstat_verify_regular/fstat_verify_directory is a held-inode
filesystem type change, never a request for different Git object bytes. Its physical
impossibility is checked before object-role or release-stream missing-binding logic.
The current bound inode type is read when available; an unbound release-stream
fstat still has the held regular-descriptor contract. Byte corruption of that same
regular inode remains realizable and accepted where exact bytes/path are bound.
Logical Git object-type/length/hash faults retain separate byte-binding obligations.

Each unbound row retains a conditional physical_realizability_precheck, its basis,
the held-inode filesystem-type guard and concrete-type/descriptor-contract context, in addition to
origin, fixture, call, normative cursor, program hash and required binding. Independent
stored-data audit recomputes this precheck and rejects impossible held-type faults in
the obligation category. Conditional realizability does not authenticate a binding,
create durable baseline proof or count as accepted coverage. The precheck field
held_descriptor identifies the fstat_* filesystem-type guard; it is not a descriptor-
lifetime trace. Object decoder WRONG_TYPE means Git logical type, not inode type.

Prepared additions cover the reported full-status same-hash case; every accepted
mutation's target and syscall-derived capability; null targets; scope/role forgery;
namespace scope plus child separation; missing eligible children; bound and unbound
held-descriptor type impossibility; same-inode realizable object corruption; and
physical prechecks for every obligation. Tests remain PREPARED / NOT RUN.

Final-revision static inventory coverage verification: 3800 parent-fsync survivor pairs share case IDs. Retained ledger-origin counts: CONTENT_HASH_MISMATCH=1900, SYMLINK_REPLACEMENT=1900, WRONG_GROUP=7600, WRONG_MODE=7600, WRONG_OWNER=7600. No tests were imported, collected or executed.
