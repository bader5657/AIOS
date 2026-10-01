# Compatibility, release prerequisites and acceptance

## Compatibility/regression matrix

| Surface | Preserved binding | Proposed isolated test / production observation | Acceptance |
|---|---|---|---|
| Telegram ingestion | Both PR306 module bytes/inodes, current process | Synthetic fixture update parsing through mocked transports; no real Telegram message | Same outputs/errors as PR306; no production ingestion test |
| Authentication | Exact module and full custody inventory | Synthetic authorized/unauthorized/replay/failure inputs against copied code, synthetic archive only | Same behavior; no real cert/journal/guard/marker/consumption writes |
| Service startup | Unit/env/interpreter/PID/start time/WorkingDirectory | Inspect live properties read-only; startup smoke only in isolated mock environment | No production restart; unchanged live PID/config; test failures remain blockers |
| PostgreSQL | No DB action in program | Mock DB adapter and syscall/network trace; no SQL against production | Zero production DB connections/queries/migrations; no DB-state equivalence claim without separate evidence |
| Executor/policy/reader/R34 | Snapshot hashes and exact GitRefs | Byte identity plus isolated existing reader contract tests | All hashes unchanged; old PR304/runtime mismatch remains STOP after future transition until successor/selector gates |
| Application/dependencies | 92 files equal PR306 and current main | Compare exact bytes/modes; offline mock regression | No code/dependency/interpreter installation |
| Evidence | PR304 immutable record/hash and historical source receipts | Exact committed blob/source hash comparison | PR304 stays PUBLISHED / VERIFIED, required immediate predecessor |
| Bootstrap | Sequence4 immutable closure | Compare decision and adoption source bindings | CLOSED / EFFECTIVE, no reopening |
| Operational authority | R34 remains baseline; selector/activation absent | Read-only presence/hash check | No selector/activation creation or consumption |
| Rollback | Old HEAD/index and intentional deployment overlay | Every fault case plus exact after-rollback map | Original metadata bytes/inodes and two dirty entries restored; functionality preserved |

## Exact STOP conditions

STOP before mutation if any release input in01 is null, stale or unauthenticated;
register fork/revocation/STOP/reservation/conflicting instruction; main/subject bytes
not equal reviewed references; wrong current or target HEAD; unexpected status or
index flags; missing/corrupt original/candidate anchor; source hash/OID mismatch;
wrong object count or missing set; unexpected path/owner/mode/type/link count;
symlink or ancestor replacement; different device; unsupported rename/fsync semantics;
unknown existing control root/lock/stage/quarantine; lost exclusive custody;
authentication/service/process/DB boundary change; concurrent archive writes;
expired approval or incomplete action/currentness/package/interpreter/unused-authority
checks; incomplete/failed crash tests; conflicting successor/selector/activation.

STOP during/restart on every unprovable identity, torn event, hash-chain gap, failed
write/fsync/rename/link, foreign inode even with equal hash, wrong before/after state,
clock regression or loss of approved custody. Do not reclassify STOP as PASS after a
retry without durable proof and applicable authority. Only the exact preapproved
rollback branch may mutate proven-owned state; otherwise preserve and seek review.

## CLEAN runtime success criteria (all required)

1. HEAD is a regular detached file with exact targetSHA+LF, new approved inode/mode;
   original HEAD remains in durable backup/forward-old anchor. No ref/reflog change.
2. Index is exact separately approved target artifact, stage0 entries/modes/OIDs
   exactly equal full target tree; no sparse/skip/assume/intent/split concealment.
   Original index anchor/bytes intact. Full filesystem content matches target tree;
   independent byte comparison does not rely solely on index stat-cache fast paths.
3. All62 objects correctly imported, complete5426-object target graph readable;
   all original objects unchanged. Only nine allowed fanouts and D010 created.
   Exactly three ancillary target files materialized. Existing PR306 modules retain
   original bytes, inodes, mode, ownership and metadata; no copy/overwrite/relink.
4. Full staged/tracked/untracked Git status is empty; ignored artifacts are inspected
   and cannot conceal unexpected worktree content. HEAD/index.lock both absent after
   exact quarantine moves. No runtime test report, temporary file or extra parent.
5. Config/reflog/unit/env/interpreter/venv/process unchanged; PID/start time unchanged;
   all auth custody and rollback identities unchanged; selector/activation/consumption
   state unchanged. No SQL/service action executed. Read observations only.
6. All operation DONE proofs and state seals valid, no gaps/unresolved STOP, every
   before/after mapping and durability result retained. VERIFY and FINAL/DONE VERIFIED
   recorded at actual UTC. No future timestamp or proposed result is a completion.
7. Appointed human verifier later adopts actual results. Technical CLEAN is solely
   source-state reconciliation, NOT Stage0.33C closure or recovery readiness.

Rollback success: exact old detached HEAD and original index bytes/inodes/owner/mode,
original index flags, status exactly modified core/adapters/telegram/main.py and
untracked core/adapters/telegram/auth_evidence.py; modules/custody/service preserved.
Imported objects/fanouts and all external anchors/history retained. Log unavoidable
metadata nlink/ctime differences; never backdate or claim bitwise whole-filesystem
restoration. ROLLED_BACK is not CLEAN runtime and never permits recovery.

## Separate authority and remaining blockers

This package is local and uncommitted. Sequence5 permits this governance preparation;
it supplies no production PASS. Before any mutation (including creating external
ledger or original metadata anchors), require:
- Owner review/adoption of this package and explicit publication-candidate instruction;
  exact-HEAD review, publication authorization and verified publication when adopted
  as the execution procedure. No permission is inferred to commit/open a PR now.
- Concrete syscall adapter reviewed against02/04 and a separately authorized isolated
  fixture/test run. Freeze adapter/environment/program hashes; accept all required
  model, filesystem, power-loss and rollback test evidence. None has run here.
- Separately authorized scratch preparation of the exact standalone index and compressed
  objects. Freeze generated bytes and approve their hashes in a separate execution
  release; no runtime source staging/import occurs during governance preparation.
- Action-specific independent-human production acceptance plus Owner approval, OR an
  effective separately reviewed scoped solo-owner production-risk amendment, where
  the process boundary applies. Neither PR318 nor sequence5 supplies that amendment.
- Explicit exact execution AND rollback authorization naming attempt root, program,
  adapter, artifacts, allowed paths/modes, failure branches, operator/custodian/verifier,
  no-concurrent-writer method and bounded action window. Unbounded manual repair banned.
- Fresh cross-channel/register/approval-window/package/interpreter/custody/unused-authority
  checks, current old-head/overlay identities and capabilities. Earlier evidence is
  not a perpetual currentness certification or renewed approval window.

After actual migration: authenticated clean-state verification, separately authorized
successor population with PR304 immediate predecessor, its review/approval/publication,
then separately governed selector, activation, installation and operational closure.
Do not create successor record/selector/activation/installation evidence now. Step5
remains outside this entire implementation package.

The H1/M2–M5 revision adds baseline-derived alias groups, closed semantic evidence,
ordered rollback barrier records, separate pre-seal/post-terminal checks, regenerated
fault occurrences and behavioral prepared tests. It is not an execution release. The
reviewed adapter must validate evidence authenticity and phase predicates before
it supplies verified/durable flags. All pure-model tests, all applicable occurrence
fault cases, actual filesystem rollback tests and power-loss validation remain
unexecuted and mandatory before execution approval. Static AST/schema/hash success
is only a package-integrity result. Exact local re-review is next; Owner adoption
and separately authorized publication-candidate preparation follow a CLEAN review.


Revision acceptance additionally requires all approved baseline hardlink groups to
retain exact membership/inodes/content/metadata/counts; no new sharing is permitted.
The full semantic evidence context must be separately authenticated and release-bound.
ROLLED_BACK acceptance requires PRE_ROLLBACK_SEAL evidence, the terminal seal, then
successful read-only POST_ROLLBACK_TERMINAL verification. Source/static checks alone
do not certify that prepared tests pass. Project Owner authorization for this revision
does not authorize tests, adapter creation, runtime mutation, execution, commit or PR.


M2/M4/M5 follow-up acceptance requires stable schema/semantic STOPs for malformed
inputs, uniqueness of semantic fault boundaries, required alias/exchange reopen
occurrences, and behavioral recovery histories for every metadata row. Static AST,
schema, inventory uniqueness and hash checks do not claim tests passed. This package
is offered for re-review only; publication/adoption and execution gates are unchanged.
