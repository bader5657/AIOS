# Stage 0.33C-P2 Paths, Ownership, Modes, and Current State

## Package authority and source gate

This documentation-only package records Project Owner approval for publication
of Step 2 governance and nothing else. Its inspected source gate was clean at
`HEAD == main == origin/main == 7b1ac3e546b4133da28f888b17e42cd5a88a5f8f`.
Step 1 is `CLOSED / VERIFIED`; Step 2 is current governance; Step 3 is not
authorized. Publication does not provision a path or grant first-write authority.

The preserved sequence is: (1) closed runtime prerequisites, (2) filesystem
prerequisites, (3) future ephemeral one-shot harness, (4) real evidence/facts,
(5) first-write authority, (6) review/merge authority, and (7) one bounded write.
No steps may be combined or started automatically.

## Frozen paths and read-only prestate

| Object | Exact path | Required state | Inspected prestate |
|---|---|---|---|
| candidate root | `/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c` | real directory, `root:aiosadmin`, `0750` | exact; non-symlink |
| authorization artifact | `/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/authorization.json` | future regular non-symlink file, `root:aiosadmin`, `0440`, at most 16384 bytes | `ABSENT` |
| consumed directory | `/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/consumed` | real non-symlink directory, `aiosadmin:aiosadmin`, `0700` | `ABSENT` |

These paths admit no environment override, alternate, or caller-selected final
path. The existing
`/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/runtime-sync-evidence`
is unchanged historical Step-1 infrastructure and must not be reused for Step 2.

The candidate root's group bits are `r-x`, not `rwx`; therefore runtime identity
`aiosadmin:aiosadmin` cannot create `consumed` directly. Privileged human
provisioning is required after this package is independently reviewed and merged.

## Existing-object and symlink policy

Every component is checked without following an unsafe symlink. The candidate
root, `consumed`, and `authorization.json` must themselves be non-symlinks. Any
unsafe symlink component is a STOP.

For `consumed`: `ABSENT` permits later exact provisioning; `EXACT_PRESENT`
permits reuse only after verification; `DRIFTED_PRESENT` is a STOP. There is no
chmod/chown repair, rename, delete/recreate, or recursive mutation.

`authorization.json` is expected absent. If it exists in any form, inspect only
bounded metadata, classify
`UNEXPECTED_PREEXISTING_AUTHORIZATION_ARTIFACT`, and STOP pending separate
review. Do not read its business or secret contents. No overwrite, truncate,
silent replacement, or removal is allowed unless later deactivation/replacement
governance explicitly authorizes it.

Any future authorization installation stages only in the governed candidate
root, using the helper-generated name
`.authorization.json.stage-<canonical-lowercase-UUIDv4>`. The exact accepted
regex is
`^\.authorization\.json\.stage-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$`.
The helper derives the staging path from that fixed directory and its internally
generated canonical name; callers, CLI arguments, environment variables, and
authorization payloads cannot select either component. No alternate directory,
`/tmp`, separator, traversal, absolute injected name, backslash, or Unicode path
trick is accepted.

Creation is exclusive and no-follow (`O_WRONLY | O_CREAT | O_EXCL |
O_NOFOLLOW`) at initial mode `0600`. A collision is a STOP: no overwrite,
deletion, fallback loop, or second generated identity occurs in the same
governed attempt. Publication remains same-directory and no-replace. Cleanup is
limited to that exact generated path; wildcards, directory sweeps, recursive
cleanup, and arbitrary hidden-file cleanup are prohibited. A cleanup defect
before publication is
`AUTHORIZATION_STAGING_PREPUBLICATION_CLEANUP_INCOMPLETE`; a cleanup defect
after verified publication is `AUTHORIZATION_STAGING_CLEANUP_INCOMPLETE`.
Either disposition blocks activation and first write pending governed operator
resolution. A residual staging name is never a second authorization artifact;
the runtime reader recognizes only exact `authorization.json`.

## Authorization artifact contract

Future approved bytes must be strict JSON, contain no secret fields, be no more
than 16384 bytes, and be installed as a regular non-symlink file owned
`root:aiosadmin` with mode `0440`. Filesystem capability provisioning is distinct
from artifact creation: Step 2 may prepare and prove directory capability, but
must leave `authorization.json` absent. Actual bytes belong only to a later
first-write authority stage.
