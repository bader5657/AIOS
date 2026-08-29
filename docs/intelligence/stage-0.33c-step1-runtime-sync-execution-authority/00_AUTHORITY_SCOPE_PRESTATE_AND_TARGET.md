# Stage 0.33C-P1SA Authority Scope, Prestate, and Target

## Authority scope

This documentation publishes exactly one future runtime-source synchronization
execution authority. It does not execute synchronization, restart the service,
begin Step 2, provision filesystem paths, create a harness, select input, create
first-write authority, or contact PostgreSQL.

The authority is consumed only once, immediately before the first operation that
changes `/opt/aios-src` checkout state (`HEAD`/worktree). Read-only preflight and
an explicitly permitted network fetch do not consume it. After consumption there
is no second forward synchronization attempt and no retry.

## Preconditions and identities

Before any runtime mutation, independently reverify:

- governance source `HEAD == main == origin/main ==
  2ceea1a2589a3542a8f3cc00b73ab5fb50f9fa39` and clean worktree;
- `/opt/aios-src` is a real non-symlink `aiosadmin:aiosadmin` directory, mode
  `0755`, detached and clean;
- current runtime SHA is exactly
  `2c44dc84cb38dc51778f8a65f12a6e59683c74c9`;
- remote is exactly `git@github.com:bader5657/AIOS.git`;
- no local modifications, untracked files, unreviewed commits, or path drift;
  and
- pre-sync rollback identity is freshly recorded as
  `2c44dc84cb38dc51778f8a65f12a6e59683c74c9`.

Any difference is `RUNTIME_SYNC_ACTIVATION_BLOCKED`: stop, leave authority
unconsumed, and do not reset, stash, clean, or mutate the checkout.

## Frozen target

The only accepted target is the exact commit
`964193f2e567b5109de50c427bbbf632b2198958`. A moving `main`, `origin/main`,
`latest`, or content-equivalent commit cannot substitute for this identity. The
target must include the complete merged repository and the three Stage 0.33C
modules, not a partial copy or cherry-pick.

## Fetch and consumption boundary

An exact-remote, no-merge `git fetch` may occur during read-only/preflight phase
solely to obtain and verify the target object; it must not alter the worktree.
If fetch or target verification fails, stop before consumption. Immediately
before the first checkout mutation, record the authority-consumption timestamp
and consume the one authority. The subsequent forward mutation is exactly:

`git -C /opt/aios-src checkout --detach 964193f2e567b5109de50c427bbbf632b2198958`

`git pull`, moving-branch merge, manual copy, `rsync`, unreviewed cherry-pick,
and force-reset are prohibited.
