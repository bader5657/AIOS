# Zero-Poller Source Switch and Integrity Gates

## Exact cutover boundary

The `/opt/aios-src` worktree may change only after:

1. the existing Stage 9.2.3 executor stops `aios.service`; and
2. process inspection proves `POLLING COUNT = 0` with no alternate launcher.

During that zero-poller window, the authorized source sequence is:

1. quarantine only preflight-classified generated `__pycache__/` and `.pyc`
   residue under the existing bytecode-disposition authority;
2. switch `/opt/aios-src` to detached exact commit
   `2c44dc84cb38dc51778f8a65f12a6e59683c74c9` (or an existing deployment
   branch resolving exactly to it);
3. prove `HEAD` equals that full SHA;
4. prove tracked and staged diffs are empty;
5. prove the service artifact has the exact approved blob and SHA-256; and
6. only then continue corrected-unit installation under the already-active
   Stage 9.2.3 VPS separation approval.

No service start is permitted unless every source verification passes.

## Residue and Git restrictions

Only independently verified generated Python bytecode may be quarantined. No
other untracked or ignored class may be removed or moved. Discovery of any
other class requires an immediate stop with:

`STAGE 9.2.3 SOURCE INTEGRITY BLOCKED`

The following remain prohibited: `git clean`, destructive removal of unknown
files, unresolved deletion globs, historical-branch merge, local source edit,
local commit, force operation, and remote history rewrite. A detached exact
deployment SHA is acceptable.
