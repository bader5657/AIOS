# Stage 0.33C-P1S Runtime Source Drift and Target Identity

## Scope and source gate

This package publishes synchronization governance only. It does not modify the
runtime checkout, restart services, begin Step 2, provision filesystem paths,
create an authorization artifact, build a harness, select input, create
authority, or contact PostgreSQL.

At publication, the review repository satisfied `HEAD == main == origin/main ==
964193f2e567b5109de50c427bbbf632b2198958`, with a clean worktree. Stage 0.33C
implementation remains CLOSED / VERIFIED; PR #265 remains MERGED / VERIFIED;
Step 1 remains open and Step 2 is not authorized.

## Read-only runtime checkout inventory

| Property | Observed value |
|---|---|
| Path | `/opt/aios-src` |
| Type / symlink | Directory; non-symlink |
| Owner/group/mode | `aiosadmin:aiosadmin`, `0755` |
| Commit | `2c44dc84cb38dc51778f8a65f12a6e59683c74c9` |
| Branch | Detached `HEAD` |
| Remote | `origin git@github.com:bader5657/AIOS.git` |
| Worktree | Clean; no local modifications or untracked files |
| Relative state | 0 commits ahead and 4 commits behind the available `origin/main` reference |

The checkout lacks `controlled_candidate_create.py`,
`candidate_create_authorization.py`, and `candidate_create_evidence.py`. The
reviewed authoritative source is the repository `main` commit
`964193f2e567b5109de50c427bbbf632b2198958`.

## Frozen target and drift gate

Future synchronization must target exactly
`964193f2e567b5109de50c427bbbf632b2198958`. A moving `main`, “latest” ref, or
equivalent-content substitution is not acceptable. Before mutation, the
operator must confirm the expected remote identity, detached/known checkout,
clean status, no unknown commits, no untracked runtime artifacts, and target
object availability. Any local drift or ambiguous remote state is a hard STOP;
there is no force-reset over unknown changes.

The required whole-checkout result must contain the target commit and all
already-merged dependencies, not a partial copy or cherry-pick of the three new
modules.
