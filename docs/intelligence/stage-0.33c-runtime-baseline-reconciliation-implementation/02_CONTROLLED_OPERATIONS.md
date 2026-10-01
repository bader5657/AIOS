# Exact controlled operations (normative implementation)

These operations are a specification to be reviewed, not commands executed now.
Every variable is bound by 01; no path is discovered or accepted from CLI/environment.
The only dynamic identities are newly created inodes and separately approved prepared
metadata. Record actual identities; never fill them with predictions. Null release
inputs prohibit ALL future mutation, including external control-root initialization.

## Common preconditions and identity algebra

Before the first syscall with side effects: verify authenticated execution authority
and applicable production-risk gate, complete review/test release, fresh currentness,
exact input hashes, effective sequence5, PR318 and PR304, old detached HEAD/index,
exact two-entry status, all missing paths, 62 missing objects in 5426-object graph,
92 application files, service/PID/config and complete authentication custody. Exclude
other Git writers/recovery actors using actual operator custody; directory flock only
serializes this procedure. No service stop/restart is a means of obtaining exclusivity.
Recheck custody and STOP/revocation before every primitive and state seal. A bounded
quiet custody window must be established without modifying service/DB; if unavailable,
STOP. Ordinary process activity cannot be guessed away as a migration-owned change.

Identity has existence, absolute path, dev, ino, file type, UID, GID, mode, size,
SHA-256 for regular files; also record nlink/mtime_ns/ctime_ns. Directory identity
excludes size/timestamps for equality after child operations, but records their real
values. Original HEAD/index nlink/ctime changes are allowed ONLY for listed links;
bytes/inode/ownership/mode stay bound. All other protected custody matches published
identities. Do not use byte equality to replace dev/inode ownership proof.

Path opening: start with open('/', O_RDONLY|O_DIRECTORY|O_CLOEXEC), traverse each
literal component using openat(parentfd, name, O_RDONLY|O_DIRECTORY|O_NOFOLLOW|
O_CLOEXEC). Reject empty/dot/dotdot components. For each ancestor fstat, compare the
approved baseline or a durable same-attempt D record; before and after mutation,
re-traverse the full path and require it still resolves to those held descriptors.
Open regular inputs with O_RDONLY|O_NOFOLLOW|O_CLOEXEC, require S_ISREG, fstat before
and after reading/hash. Reject hardlink surprises on original inputs against baseline
nlink; stage links intentionally change nlink and must be accounted for. Reject
nonregular entries, symlinks at any level and paths crossing st_dev. No resolve()-then-
open safety assumption. An unapproved ancestor identity is STOP, not auto-pinning
permission; the separately approved preflight binds all ancestors not enumerated in
01. This strengthens checks without adding any creation path.

The file rule, its parent rule and permitted_child_names MUST all agree. Every
creation destination must match one exact rule or finite control/ledger name below.
No mkdir -p, glob-based writes, copy/unlink fallback, rename replacement, chmod of an
existing entry, cleanup, gc, git fetch/reset/checkout/clean or runtime Git writer.
No shell expansion or subprocess that imports runtime Python is allowed.

## Primitive contracts

EXCLUSIVE_FILE(parentfd,name,bytes,mode): parent verified; name allowlisted and absent.
openat O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC, creation mode 0600; require current
EUID/EGID=1000, no privilege escalation. Write all bytes (handle EINTR/short writes),
fchmod the NEW fd to target mode, verify fstat owner/group/type, fsync file, fsync
parent; reopen no-follow, hash and compare. No chown/adoption of an existing file.
A failed write/fsync leaves content in place under STOP; never truncate/rewrite retry.

EXCLUSIVE_DIR(parentfd,name,mode): absence + parent verified. mkdirat single basename
with umask 077; open new directory O_DIRECTORY|O_NOFOLLOW; require uid/gid1000,
fchmod NEW fd only to approved 0700 or0755; fsync new directory and parent. Crash
before its identity has been durably recorded leaves an unprovable orphan => STOP.

LINK_EXCLUSIVE(srcfdparent,srcname,dstfdparent,dstname): both parents revalidated;
source is exact recorded regular inode and no symlink; destination absent. linkat
with flags0 (never follow symlink); EEXIST is not success. fsync source inode to
persist nlink metadata, then both parents; reopen source and destination, require
same dev/ino, owner/mode/hash. Preserve source anchor. Ledger expected nlink delta.

MOVE_EXCLUSIVE: use renameat2(oldparent,oldname,newparent,newname,RENAME_NOREPLACE).
Both parents same device; source exact recorded inode; destination absent. No fallback.
Fsync source inode when applicable and both directories, revalidate namespace and
identity, then completion event. EEXIST/EXDEV/ENOSYS/EINVAL => STOP. Directory moves
also fsync the moved directory. No unlink is used anywhere in this program.

EXCHANGE: renameat2(liveparent,livename,lockparent,lockname,RENAME_EXCHANGE), with
both inodes pinned and exact. Fsync BOTH exchanged regular inodes and their parent
(.git); re-open and require exact swap. No metadata content write. The lock file
is not deleted: MOVE_EXCLUSIVE to its exact quarantine slot. Swapping wrong content
is prevented by custody plus immediate identity checks; syscall itself is not an
inode compare-and-swap against a hostile concurrent writer. Lost custody => STOP.

No mutation may occur without a durable INTENT/BEFORE record, except initial creation
of the attempt-root/ledger needed to establish the ledger itself. Initialization
exception applies only to those exact external paths; unprovable restart is STOP.

## Ledger and completion

Hold flock(LOCK_EX|LOCK_NB) on the pinned attempt-root directory fd throughout.
Event fields are EXACTLY rollback_protocol.ledger_event_fields in 01. Use null only
where semantic_evidence_contract permits it; never omit fields. Identity subrecords are the closed full path-keyed observation maps defined below;
parent subrecords are their exact directory projections. Each event records real
UTC, state, operation_id and observed before/after identity, never asserted success.
Allowed operation IDs: those 79 IDs plus ROLLBACK and FINAL. Event enum INTENT, STAGED,
BEFORE, AFTER, DONE, STOP. ROLLBACK_INTENT/ROLLED_BACK are state values, not extra
filename event types. Encode UTF-8 sorted keys, compact separators, finite JSON only,
exactly one LF. Hash covers full bytes. ordinal starts1, previous_event_sha256=null
only for1; otherwise SHA-256 of preceding complete event. Reject duplicate keys,
missing fields, ordinal gaps/duplicates, incorrect filename/value correspondence,
noncanonical bytes, stale times, unknown paths/operations or broken hash chains.
No later action may trust a DONE record without checking actual side-effect identities.

File name = six-digit ordinal + '-' + operation_id + '-' + event + '.json'.
Use EXCLUSIVE_FILE(ledgerfd,name,canonical_bytes,0600); fsync the file AND ledger dir.
No mutable checkpoint file. Derive state by replaying immutable events in order.
Each operation has exactly INTENT with microstep_id BEGIN, then for EVERY named
01 microstep BEFORE -> AFTER -> STAGED if and only if stage_checkpoint=true, then
one DONE with microstep_id COMPLETE after all microsteps. Microstep paths exactly
match01. INTENT/COMPLETE and state seals have null source/destination; identity
subrecords retain the relevant observations. An AFTER is appended only after the
entire primitive's ordered syscalls and postconditions are durably verified. A STAGED
record binds the exclusively created inode before it can become a reusable anchor.
There is no per-syscall DONE and no mutable completion-marker file: operation DONE
and FINAL/DONE are the exclusive immutable completion markers.

durability_checks is a closed object with microstep_id, program_sha256 (SHA-256 of
canonical01 bytes), verified=true, durable=true and the closed evidence object. Those
booleans alone cannot satisfy replay; evidence must satisfy semantic_evidence_contract.
They attest checked
adapter evidence; they do not authenticate themselves. Full identity observations,
object hashes and parent/link changes must be validated against the approved release
and descriptor observations before those flags can be supplied. A syntactically
well-formed forged chain is not trusted without custody and authenticated proofs.

State seals use FINAL/DONE, microstep_id SEAL:<state>, in the exact eight-state
order, after every phase operation DONE and the matching phase predicate. A next
phase operation without the preceding seal is STOP. Never insert a seal retroactively
to repair history. A clean interrupted prefix after final operation DONE may append
its next seal only after fresh barrier verification, with no later event present.
VERIFIED requires VERIFY/DONE, every prior seal, all08 invariants and its terminal
seal. Subsequent forward events are rejected.

Both validate_chain and semantic_replay in03 are mandatory adapter entry points.
State is their reconstructed sealed/active/completed history, not a caller-supplied
completed prefix. Reject duplicate/missing/out-of-order operations or seals, forged
DONE, malformed/noncanonical events, event reordering and chain mismatch. A missing
tail completion is pending, never success. Retry replays the same history; it cannot
repeat a proven link or exchange. Pending BEFORE requires exact before/after inode
classification; ambiguity STOP. Proven-after may reverify/fsync and append AFTER
at actual current UTC, not rewrite the earlier record.

Write errors,
torn events, absent durability evidence, ledger divergence or EIO/ENOSPC => STOP.
Do not append a guessed correction after a corrupt tail. If ledger is writable and
valid, a STOP event may be appended; otherwise stop and preserve filesystem evidence
for a separately retained incident receipt. No prior record is erased/repaired.

## INIT and PREPARE (within later execution authority)

1. Require exact control parent baseline, same st_dev as all destinations, operation
   root absent. Exclusively create root0700 and ledger0700; hold root flock. Persist
   PREPARE/INTENT with observed identities and authorized preflight. Create only
   backup, staging, quarantine0700 through logged EXCLUSIVE_DIR operations.
2. Read original HEAD/index/config/logs-HEAD no-follow and bind exact hashes/inodes.
   HEAD equals oldSHA+LF and is detached. Verify complete index stage0 inventory,
   flags/extensions and absence of ignored/sparse/assume-unchanged concealment.
   Exclusively create backup/{HEAD,index,config,logs-HEAD}.bytes0600 and
   backup/before-state.json0600 with required published fields. Byte backups contain
   only Git metadata, not environment credentials or authentication messages. Treat
   confidential Git config as private backup; no backup contents go into PR receipts.
3. Ledger and LINK_EXCLUSIVE original HEAD/index to backup/{HEAD,index}.original.
   Record original link-count/ctime change. Preserve mode0664. Never fchmod anchors.
   Snapshot before-state includes pre-link nlink/ctime; post-link observations are
   in events. A pre-PREPARED interruption after links is execution-side metadata
   activity and must be reported, never called 'runtime untouched'. It changes no
   module content and remains within the explicit original-anchor exception.
4. Separately prepared index bytes must already be approved from an isolated scratch
   repository. No scratch generation runs against production. Independently decode
   index and compare every path/mode/OID/stage with target tree; reject skip-worktree,
   assume-unchanged, intent-to-add, sparse/split indexes and unsafe extensions. Use
   a full standalone index whose stat cache is invalidated rather than copied from
   fixture inodes. Bind exact artifact SHA-256; missing artifact => STOP.
   Publish staging/index.after0664 and HEAD.after0664 exclusively; latter bytes are
   exactly targetSHA+LF. Check deployment target/modules and metadata rule hashes.
5. Verify backups/anchors/stages and full immutable custody. PREPARE/DONE, then
   FINAL/DONE PREPARED. No D/O/F or live metadata exchange before this seal.

A partly initialized attempt root without a valid durable PREPARE identity chain is
not resumable by name alone. STOP and retain it. A new attempt root requires new
reviewed authority; never choose an automatic suffix or clear the directory.

## Ordered forward operations

D001..D009 (OBJECT_DIRECTORIES_CREATED): use exact missing fanout rules.
D010 (DIRECTORIES_CREATED): use exact PR303 documentation directory rule.
For each D: BEGIN; create-directory BEFORE, exact staging/D###.directory0755
creation/fsync/verification, AFTER, STAGED; move BEFORE, MOVE_EXCLUSIVE stage to
exact destination, fsync moved directory/both parents, AFTER; COMPLETE DONE.
On resume, destination-only exact recorded inode is already published; stage-only
recorded inode permits move; both present, both absent after STAGED, or unproved inode
=> STOP. Never infer ownership from emptiness. Seal only after all group D checks.

O001..O062 (OBJECTS_IMPORTED): read raw content from exact approved target graph
outside runtime. Verify type, length, raw SHA-256 and SHA-1 of type + space + decimal
length + NUL + raw payload against rule. Compress canonical envelope with approved
zlib/tool version; the separately approved execution release binds compressed-byte
SHA-256 per object. Do not regenerate a different stream on retry. Create exact
staging/O###.object0444 exclusively; fsync, re-open, strictly decompress exactly one
zlib stream (reject trailing/unconsumed/incomplete data) and revalidate header and
content. STAGED seals its dev/ino/raw/compressed identities. BEFORE;
LINK_EXCLUSIVE stage to listed loose-object destination; AFTER; DONE.
After62 verify the entire target reachable graph (5426 unique objects), not just
commit existence; use no replacement/graft/alternate object interpretation. No refs,
repack, maintenance or network fetch in runtime. Then FINAL/DONE OBJECTS_IMPORTED.

F001..F003 (ANCILLARY_FILES_CREATED): source bytes are exact Git blobs at fixed
PR306 target, with published SHA-256. Same stage/STAGED/link/AFTER/DONE protocol as O,
mode0644, exact staging/F###.file and destination. Source module files are NEVER
staged, overwritten, linked or chmodded. Verify all three files plus D010 and
unchanged modules/custody, then seal ANCILLARY_FILES_CREATED.

M_INDEX then M_HEAD (INDEX_RECONCILED / HEAD_RECONCILED):
- Require all previous states sealed, original live inode/hash, prepared-after stage
  exact, original backup anchor exact, lock absent, forward-old quarantine absent.
- INTENT; BEFORE for link; LINK_EXCLUSIVE prepared-after anchor -> exact .git/*.lock;
  AFTER records linked candidate. BEFORE exchange names both inodes; EXCHANGE;
  AFTER records live=candidate, lock=original. BEFORE move; MOVE_EXCLUSIVE lock ->
  quarantine/*.forward-old; AFTER; DONE. Seal respective state after checks.
- No git update-index/read-tree/update-ref/checkout/reset operation in runtime;
  no hooks/reflog/config write. During index-before-HEAD interval, Git may report
  intentionally transitional differences: this is not CLEAN and must block actions.
- Full identity matrix and reversal are normative in04; do not replay EXCHANGE
  just because DONE is missing. Determine syscall result from exact inode mapping.

VERIFY: perform all08 checks, including full tree/index/worktree independently,
empty full Git status and metadata flags. On failure never seal VERIFIED. Before
FINAL/DONE VERIFIED, recheck service/custody/currentness once more. Persist actual
verification evidence in the immutable VERIFY events; no extra unlisted runtime
report file. Technical VERIFIED requires later authenticated human adoption and
never starts successor population, selector, activation or installation.

## Read-only verification command equivalents

Run only under a reviewed sanitized environment: unset GIT_DIR/GIT_WORK_TREE/
GIT_INDEX_FILE/GIT_OBJECT_DIRECTORY/GIT_ALTERNATE_OBJECT_DIRECTORIES and replacement
influences; GIT_NO_REPLACE_OBJECTS=1, GIT_GRAFT_FILE=/dev/null, GIT_OPTIONAL_LOCKS=0,
GIT_CONFIG_NOSYSTEM=1, GIT_CONFIG_GLOBAL=/dev/null. Pin local config digest and reject
unapproved include/filter/fsmonitor/alternate/sparse/replace mechanisms. Use
`git --no-optional-locks -c safe.directory=/opt/aios-src -c core.fsmonitor=false
-c core.untrackedCache=false -c core.hooksPath=/dev/null -C /opt/aios-src ...` with
literal argv, no shell. Read commands only: rev-parse HEAD; symbolic-ref -q HEAD
(must report detached); ls-files --stage -z; ls-files -v -z; diff --no-ext-diff
--no-textconv --exit-code; diff --cached --no-ext-diff --no-textconv --exit-code;
status --porcelain=v1 -z --untracked-files=all --ignored=matching.
No ignored/untracked source artifacts or index shortcuts may make a false CLEAN.
Read-only commands are corroboration, not a replacement for raw index/tree/content
comparison. Never invoke auth verify/consume helpers, application imports, DB SQL,
network ingestion or service restart on production during this procedure.

## Phase-specific barriers and adapter interface

01.phase_barriers is the machine-readable predicate source. Each forward state has
an exact complete namespace token map, historical operation/seal lists and Git
predicate. Every path is either ABSENT (null) or one exact identity token. For an
active microstep, derive the next map only from its proven effect: create introduces
its recorded token, link adds the same token, move transfers it, exchange swaps it.
Historical completion remains immutable while PRESENT path predicates evolve. A
moved D directory must not still exist at its old staging name. Original HEAD/index
remain original-inode tokens at anchors after live paths acquire candidate tokens.

Every barrier checks three distinct categories:
A. Hash/semantic-valid historical events, ordered completion and seal evidence.
B. Unchanged module/custody/service/config/evidence/BASE identities, and exact original
   and candidate object content/type/UID/GID/mode with authenticated provenance.
C. The current phase map, including legitimate absences, aliases and moves. Inodes
   are exact release/preflight or durable exclusive-creation dev/ino, never ranges.
   Approved baseline alias groups share one BASELINE_ALIAS token; all other distinct
   tokens require distinct dev/inode. Alias membership is exact and fixed across phases.
   All regular hashes are exact; directories have null content hash. Link counts
   equal pinned outside_links plus current controlled aliases (regular files), or
   pinned outside_links plus present direct child directories (directories). The
   latter requires reviewed filesystem semantics; unsupported nlink semantics STOP.
   New regular outside_links=0; new directory outside_links=2. Existing outside_links
   is pinned from INITIAL inventory, never recomputed to excuse drift. UID/GID1000,
   modes0444 objects,0644 ancillary,0755 created runtime dirs,0700 private dirs,
   0600 private records,0664 approved metadata; existing owners/modes exactly pinned.

Forward Git predicates distinguish old HEAD/index with two dirty entries, ancillary
additions with three extra untracked files, target index with old HEAD and staged
transition changes, and target HEAD/index with empty status. All states preserve
both deployed modules. A phase predicate is valid at its own barrier; later phases
prove prior completion historically rather than reimposing obsolete path conditions.
Rollback predicates, namespace folds and phase gates are in01 and03, detailed in04.

The future adapter must authenticate entry maps, obtain held-descriptor proofs,
validate prepared index/full Git-object bytes, implement custody and syscall contracts,
validate every before/after identity and durability result, enforce finite creation
and ledger names, invoke structural+semantic replay and phase barriers, and implement
isolated fault hooks. It must not expose arbitrary shell/path callbacks. No adapter
is created here. A symbolic token or verified boolean is never execution authority.


## Closed semantic evidence (revision M2)

01.semantic_evidence_contract is normative. validate_chain rejects unknown/missing
fields and malformed nested payloads before semantic replay. semantic_replay and
semantic_rollback_replay additionally require a separately authenticated context with
exact initial_bindings, content_hashes and rollback_plan. None is execution authority.
Initial bindings contain approved baseline tokens plus the two proved initialization
directories only. Program-known metadata, owners, hashes and canonical alias groups
must match; missing baseline details need a fresh approved preflight, never guesses.
Future regular content hashes are bound by a separate release before mutation.
Future inodes are never predicted: only an exact create AFTER may introduce one.

Every non-STOP event carries full before_identity/after_identity path maps. Each
present identity has exactly dev,ino,file_type,uid,gid,mode,sha256,nlink. Parent maps
are the complete directory projections. content_sha256 is the exact present regular
token/hash map. Object events additionally bind oid,type,length,raw SHA-256 to their
exact O rule; compressed hashes bind to the separate release. link_count_changes is
the exact token delta map, including directory-child changes and newly created inodes.

Replay independently derives namespace effects, pins created identities, and checks
all snapshots against approved bindings and prior observations. BEFORE and all
non-effect records preserve the map; AFTER may perform only its exact declared
create/link/move/exchange. STAGED cannot introduce a second identity. Operation DONE
requires all ordered microsteps and their evidence. FINAL/DONE additionally requires
the phase namespace and exact Git predicate; contradictory terminal evidence STOPs.
Closed evidence fields are kind,git_facts,checks,stop_reason,outcome. Checks associate
the exact event kind/microstep/state; they are not signatures or proof authentication.
Actual hashes and filesystem observations still require the reviewed descriptor adapter.

STOP has the last proved before snapshot, null after/after-parent/link-change evidence,
a closed reason and UNKNOWN_RETAIN outcome. It makes no claim about an ambiguous
side effect. A valid durable STOP halts replay permanently; a torn STOP is preserved,
never repaired and never followed by recursive STOP attempts. Unknown filesystem
outcomes require a separate incident receipt when no valid ledger append is possible.
STOP names the current dispatch target (active operation, next operation or FINAL),
or an explicitly selected rollback entry. Within rollback it names ROLLBACK or the
pending FINAL seal. An unrelated operation cannot label the failure. Copied backup
content hashes must equal the before-snapshot source hash as well as the release hash.

## Approved hardlink membership (revision H1)

baseline_alias_groups is derived solely from the approved baseline's regular-file
device/inode groups. Each canonical token hashes the sorted approved member paths.
All six groups have two listed aliases and outside_links=0. Fresh preflight MUST prove
that the observed link count equals the complete approved membership; if an extra
outside alias exists, STOP rather than increasing outside_links. Every member must
have the same pinned device/inode/hash/owner/group/mode. A missing member, split inode,
extra member, unexpected sharing between distinct tokens or count mismatch is STOP.
The group is counted once across all its paths, never independently per pathname.

## Normative occurrence inventory

Each primitive's syscall_occurrences enumerates ordered action/path/role sites,
including ancestor open/fstat before and after, absence checks, and mandatory
post-fsync reopen/fstat/read/hash/fstat. The same EXCLUSIVE_FILE contract applies to
every immutable ledger event. Initial attempt-root flock has its own occurrence.
Link/move/exchange fsync affected inodes and all distinct affected parents; directory
moves fsync the moved directory. Source absence after a move is checked as absence,
not as an existing-inode metadata check. Barrier and terminal semantic checks have
separate sites. Read/hash/graph semantic actions are not represented as single kernel
syscalls: the separately reviewed adapter must expand their internal reads, errors
and per-object validation before isolated acceptance. No syscall adapter exists here.


### Evidence validation order and failure contract (M2 follow-up)

All external event fields first pass closed shape and primitive/container checks:
strings for operation/event/state/microstep associations; canonical hash strings;
typed full identity/parent maps; typed object records and link-count deltas; closed
Git records with string fields and a list of strings only for ancillary_present.
STOP stop_reason is a string (including rejection of null); non-STOP requires null.
Unknown or missing nested fields STOP before any semantic dispatch. Forward and
rollback microsteps must belong to their operation/direction before step lookup.

validate_chain, semantic replay and public validation APIs preserve explicit stable
Stop reason strings. A residual malformed-input exception normalizes to the single
code MALFORMED_INPUT at the validation boundary. It never yields a Replay/Choice,
VERIFIED or ROLLED_BACK result. This is a semantic STOP, not permission to append a
STOP through corrupt history. No exception path repairs, truncates or reseals history.

### Link/exchange post-fsync sites (M4 follow-up)

For BOTH link aliases and BOTH exchanged paths, after all affected inode/parent
fsyncs: reopenat_NOFOLLOW, fstat_verify_regular, read_and_hash_verify,
fstat_verify_regular, then fstatat_verify_NOFOLLOW against the reopened descriptor.
The expected token is the same shared token after link and the opposite original
token after exchange. Both descriptor and pathname identity must agree; content,
owner/group/mode and group-wide link counts must satisfy the replayed namespace.
Ancestor revalidation follows. Every listed action has an occurrence/fault binding.
PREPARE control-directory verification is a namespace/stat check, not a file hash
of directory bytes. Ancestor opens/fstats supply its directory checks.
