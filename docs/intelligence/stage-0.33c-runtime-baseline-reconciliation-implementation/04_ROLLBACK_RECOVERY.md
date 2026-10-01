# Deterministic recovery and rollback implementation

All dispatch uses verified ledger + actual inode/content map, never state label alone.
Original = backup/*.original exact pre-change inode, bytes, uid/gid/mode. Candidate =
staging/*.after exact approved inode/bytes. A third inode, even with equal hash, STOP.
The retained stage anchor is mandatory for regular created-file ownership. Directory
ownership comes from durable STAGED identity and approved parent chain.

## Metadata classification table (apply separately to index and HEAD)

| Mode / live | lock | forward-old | rollback-new | Next exact operation |
|---|---|---|---|---|
| Forward / original | absent | absent | absent | Link candidate to lock; exchange; move original to forward-old |
| Forward / original | candidate | absent | absent | Link already done: fsync/verify, exchange once, move original |
| Forward / candidate | original | absent | absent | Exchange already done: fsync/verify, move lock to forward-old |
| Forward / candidate | absent | original | absent | Forward complete: verify and append missing markers only |
| Rollback / candidate | original | absent | absent | Finish retaining original at forward-old first, then reverse |
| Rollback / candidate | absent | original | absent | Link original backup anchor to lock, reverse exchange, move candidate to rollback-new |
| Rollback / candidate | original | original | absent | Reverse link already done: reverse exchange, move candidate |
| Rollback / original | candidate | original | absent | Reverse exchange already done: move candidate lock to rollback-new |
| Rollback / original | absent | original | candidate | Rollback complete; no mutation |
| Rollback / original | candidate | absent | absent | Forward never exchanged: quarantine candidate lock at rollback-new; live unchanged |
| Rollback / original | absent | absent | absent | Untouched: no mutation |
| Rollback / original | absent | absent | candidate | Cancellation before exchange complete: no mutation |

Each non-absent slot must have exact expected inode/content/owner/mode and ledgered
provenance. Any combination not listed is STOP. Alias entries such as lock and
forward-old may intentionally share original inode ONLY after ledgered reverse-link
intent; never accept that combination in forward mode. Mode is fixed by a durable
ROLLBACK/INTENT state ROLLBACK_INTENT; no direction change after it. EXCHANGE is never
replayed merely because a completion marker is absent. When a side effect is proved
but completion event absent, fsync affected objects/parents, verify and append actual
AFTER/DONE; don't invent the missed historic event time.

Rollback action is separately authorized as part of the exact execution release.
Do not switch from forward to rollback automatically on an unclassified exception.
If custody/ledger/anchors are ambiguous, preserve everything and STOP for human review.
If full state is proved and the preapproved failure policy permits rollback, record
ROLLBACK/INTENT durably, then run this exact order:

1. Freeze forward dispatch. Verify all original/prepared anchors, lock/quarantine
   states and unchanged protected content. Restore HEAD first if advanced, then index.
   Use the metadata table and primitives in02. Every link/exchange/move has BEFORE,
   durable side-effect verification, AFTER. Final per-item rollback completion uses
   ROLLBACK/DONE with state ROLLBACK_INTENT and source/destination identifying item;
   original forward DONE entries remain immutable and do not permit forward restart.
2. For F003,F002,F001: (destination exact stage inode, quarantine absent) => durable
   BEFORE then MOVE_EXCLUSIVE to exact quarantine/F###.file, fsync/verify/AFTER/DONE.
   (destination absent, quarantine exact stage inode) => already undone, verify only.
   (both absent, no published F provenance) => never created, preserve absence.
   Unknown inode, both present, absent stage anchor for a published file, or absent
   paths despite proven publication with no rollback evidence => STOP. Preserve all
   external stages; no deletion. Missing DONE after a proven move is repaired only
   by a new actual-time completion event backed by the earlier durable intent.
3. D010: if published, all child F paths must be absent and directory empty, same
   recorded dev/ino and approved mode/owner. MOVE_EXCLUSIVE to quarantine/D010.directory.
   Exact quarantine inode + absent live destination is already undone. Unpublished
   staged D010 is retained externally. Unknown child/identity is STOP; never recurse.
4. All imported Git objects, fanout directories and object-stage anchors are retained.
   Partial graph population need not be removed to restore the original HEAD/index;
   it must not change source status. No prune, repack, deletion or ref change.
5. Verify original HEAD bytes/inode, original index bytes/inode/flags, owner/mode;
   exact original two-entry dirty state; unchanged deployed modules/authentication/
   service/interpreter/config and original reflog/config bytes. Record actual metadata
   nlink/ctime differences, never claim those timestamps were restored. Seal
   FINAL/DONE ROLLED_BACK. Retain backup/ledger/staging/quarantine indefinitely.

## Partial-state branches

- Partial control-area initialization / unrecorded staged creation: STOP, retain
  orphan. Runtime D/O/F operations cannot have begun before PREPARED; original-anchor
  link-count changes may have occurred and must be reported. New custody authority
  may classify them; no automatic reuse, guessed repair or deletion.
- Partial object import: prove each imported target equals retained stage inode;
  resume missing O operations or retain the imported subset on approved rollback.
- Parent-only: D010 may resume its child or be quarantined empty; retain fanout D.
- Partial ancillary files: reverse only proven F subset; absent ones stay absent.
- Index changed/HEAD old: reverse index; HEAD no-op. Then reverse F/D010.
- HEAD changed/index or worktree incomplete: never declare CLEAN. Reverse HEAD then
  index when all identities are proved; otherwise STOP without guessed repair.
- Interruption at any transition: recompute state from valid ledger plus identities.
  A DONE event whose postconditions do not hold is STOP, not authority to replay.
- Verification failure: no VERIFIED marker. Approved rollback only if identity-proof
  and custody conditions hold; otherwise STOP. A later failure after terminal VERIFIED
  requires new incident/rollback authority. No silent reversal after successor,
  selector or activation; preserve the later binding chain.

Both VERIFIED and ROLLED_BACK are terminal. Retrying verifies terminal invariants;
it never reapplies forward actions. Source functionality is preserved in rollback,
but recovery remains STOP because the intentional dirty Git state is restored.

## Semantic rollback ledger and phase predicates

Freeze the proven forward prefix; append ROLLBACK/INTENT with microstep_id
ENTER_ROLLBACK and state ROLLBACK_INTENT. No subsequent forward resume is allowed.
The release-bound rollback_plan is an ordered subset of01.rollback_occurrences.
Choose it using the exact metadata recovery rows and created_recovery classifications;
omitted steps require authenticated no-op proofs. Each selected primitive records
ROLLBACK/BEFORE -> AFTER -> DONE with its exact microstep ID and source/destination.
semantic_rollback_replay validates that same hash chain and forward prefix before
accepting rollback events. It never infers completion from an arbitrary prefix list.

The phases are ENTER -> RESTORE_HEAD -> RESTORE_INDEX -> UNDO_F003 -> UNDO_F002 ->
UNDO_F001 -> UNDO_D010 -> PRE_ROLLBACK_SEAL -> POST_ROLLBACK_TERMINAL. Their predicates are in01.rollback_predicates.
Before every primitive, check the current full map; after it, fold only its proved
link/move/exchange and check the resulting map. Prior barrier proofs are closed ROLLBACK/DONE barrier events in that exact order, with
microstep_id BARRIER:<phase>, state ROLLBACK_INTENT, null source/destination and
complete unchanged snapshots/Git evidence. They use the existing ledger filename
allowlist with existing event DONE; no mutable checkpoint or additional control path. No-op barriers still require exact absence/original-identity
proofs and their ordered prior-barrier evidence. The adapter authenticates the
observations; replay reconstructs barriers from events. A supplied list of phase
names cannot replace missing history. validate_rollback_barrier checks the next
exact barrier against that reconstructed history and current map.

At ENTER retain the exact forward-entry map (including a fully classified pending
microstep), original history and current Git roles. RESTORE_HEAD requires original
HEAD live and lock absent; RESTORE_INDEX additionally requires original index live
and lock absent. Each UNDO_F requires its live path absent, retained staging anchor
and, if previously published, the same inode in exact quarantine. UNDO_D010 requires
empty directory before movement and absent live directory afterward. Never remove
an unknown child. Imported objects/fanouts and private evidence remain present as
actually proved; rollback does not impose their original absences. All phases check
unchanged protected tokens and exact link-count algebra. PRE_ROLLBACK_SEAL requires
original HEAD/index bytes/inodes, zero unresolved metadata locks, all ancillary live
paths absent and exact original two-entry dirty status while ledger_terminal is null.
After validating this predicate, append ROLLBACK/DONE barrier BARRIER:PRE_ROLLBACK_SEAL.
Only then append FINAL/DONE SEAL:ROLLED_BACK, carrying the same complete evidence.
POST_ROLLBACK_TERMINAL requires that terminal seal and all eight prior barrier records,
then rechecks the complete terminal invariants read-only. It appends no new event.
A missing seal is never accepted by post-terminal verification; the pre-seal predicate
never requires its future seal. Terminal invariant loss STOPs for new incident authority.

Retry uses semantic replay plus the exact current recovery-table row, not exchange
repetition. Partial object/fanout operations retain imported artifacts; parent-only
D010 and partial F subsets use only their same-attempt recorded identities. Index-only
reverses index after HEAD no-op; HEAD-incomplete restores HEAD before index. An
interruption within an event may leave a torn tail: STOP, preserve it, no history
repair. Within a syscall, classify exact before/after or STOP. Post-completion
verification failure has no VERIFIED seal; terminal VERIFIED invariant loss requires
new incident/rollback authority and cannot reuse the original forward stream.


Rollback entry uses the last fully evidenced forward map. If a pending BEFORE's
syscall actually completed, validate and append its real AFTER first under the
interrupted-step rule; never switch streams while concealing an unrecorded effect.
An ambiguous/torn result remains STOP. The selected plan is separately release-bound.
Each rollback BEFORE and AFTER validates its recovery-table identity precondition:
retain_forward requires candidate-live/original-lock; reverse requires candidate-live,
original-lock and original forward-old; retain_candidate requires original-live and
candidate-lock. A cancellation before forward exchange uses retain_candidate only.
No-op phases still emit their BARRIER proof. Unselected object/fanout/stage artifacts
remain at the precise entry-map locations. A selected primitive may not be skipped
because its destination happens to contain equal bytes.


### Behavioral metadata recovery binding (M5 follow-up)

metadata_rollback_decision is a pure model: it checks replayed namespace observations,
derives recovery-table labels from exact ORIGINAL/CANDIDATE tokens, then returns the
remaining ordered primitive IDs and original-live/absent-lock target. It neither
executes them nor creates a rollback release. The prepared fixtures cover all 12
rows for index and HEAD separately (24 cases). Forward rows start at INTENT or the
actual link/exchange/move AFTER; reverse rows start at rollback entry/phase boundary
or the actual link-original/reverse/retain-candidate DONE. No fabricated row labels
stand in for ledger history. Both retain-forward and already-retained paths, untouched
metadata, unexchanged-lock cancellation and completed cancellation reach exact targets.
Every row proceeds through PRE_ROLLBACK_SEAL and read-only post-terminal verification.
The previously approved pre-seal/terminal-seal/post-terminal ordering is unchanged.
