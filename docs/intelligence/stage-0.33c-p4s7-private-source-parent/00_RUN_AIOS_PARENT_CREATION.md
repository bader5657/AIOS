# Stage 0.33C P4S7 `/run/aios` Parent Creation Governance

## Scope and prerequisite

This artifact governs one future creation of exactly `/run/aios`. It resolves
the missing-parent blocker recorded by P4S7-R11. It does not execute that
creation and grants no authority over any other path below `/run`.

Before consuming this authority, the executor must resolve `/run` without
following symlinks and require it to be an existing real directory owned
`root:root`, mode `0755`. That is the verified governance-time host state and
is acceptable for the root-managed volatile runtime namespace; this authority
does not permit changing it. `/run/aios` must be absent under both ordinary
existence and no-follow directory-entry checks. A file, directory, symlink,
dangling symlink, or other conflicting entry at that name is a terminal stop. Local changes must
not be removed, replaced, renamed, or repaired.

## Frozen target and metadata

The only governed target is:

`/run/aios`

Its required post-creation metadata is exactly:

| Property | Required value |
|---|---|
| object type | real directory, not a symlink |
| owner | `root` |
| group | `root` |
| mode | `0700` |

The `root:root/0700` contract is the least-privilege parent compatible with the
merged private-source contract, which requires the child source directory to
be a no-follow `root:root/0700` directory. No merged governance requires group
or world traversal of this private namespace.

## Future exclusive creation procedure

A later, separately authorized execution must:

1. open `/` and then `run` through retained directory descriptors using
   directory-only, close-on-exec, no-follow resolution;
2. record the retained `/run` descriptor's device, inode, owner, group, and
   mode; verify the resolved `/run` entry and opened descriptor have identical
   device/inode identity and meet the prerequisite above, and keep that
   descriptor open across creation and all verification;
3. establish again that the `aios` entry is absent without following links;
4. create only `aios` relative to the retained `/run` descriptor, exclusively,
   with initial mode `0700` and no overwrite or replacement behavior;
5. apply and verify exact `root:root/0700` metadata without recursive changes;
6. immediately record the created child's device, inode, owner, group, and mode
   as creation evidence, requiring a directory at exact `root:root/0700`;
7. `fsync` the created directory and the retained `/run` parent descriptor
   where the host filesystem supports those durability operations;
8. independently re-resolve absolute `/run` with directory-only, close-on-exec,
   no-follow semantics; require it to remain a real non-symlink directory at
   `root:root/0755`, and require its device/inode to match the still-open
   retained pre-creation `/run` descriptor exactly;
9. close the child's creation descriptor and reopen the name `aios` read-only
   relative to the retained `/run` directory descriptor, using directory-only,
   close-on-exec, no-follow flags rather than an absolute pathname;
10. require the reopened child descriptor's device/inode to match the recorded
    created-child identity exactly, and independently recheck that it is a real
    non-symlink directory at exact `root:root/0700`; and
11. retain the recorded parent and child identities in the bounded creation
    evidence and close every descriptor after verification.

Successful completion therefore proves that the retained `/run` parent
identity remained stable, absolute `/run` did not change identity, and `aios`
reopened relative to that retained parent resolves to the exact created inode.
Together these comparisons explicitly rule out pathname substitution between
creation and verification.

Any uncertainty, collision, path substitution, metadata mismatch, durability
failure, or identity change is a stop. The execution must not chmod or chown
`/run`, recurse into another path, modify another `/run` entry, or leave a
writable descriptor open.

## Explicit exclusions

This governance does not authorize:

- creating `/run/aios/stage-0.33c-p4s5-source` or any other child;
- reading, copying, reconstructing, or materializing private package bytes;
- modifying `/opt/aios-src`, `runtime.env`, or the runtime evidence directory;
- executing `one_shot_install.py` or creating an installation claim;
- creating final runtime approved-input targets;
- restarting, reloading, or signaling `aios.service` or another process;
- contacting PostgreSQL, invoking the harness, creating a candidate, creating
  `authorization.json`, or authorizing Step 5.

## Required sequence and classification

The required sequence remains:

parent creation governance -> independent review -> human merge -> parent
creation execution and verification -> repeat P4S7-R11 private-source
materialization.

No stage may be collapsed. Until this artifact is independently reviewed and
merged, `/run/aios` creation remains unauthorized.

`P4S7_RUN_AIOS_PARENT_CREATION_READY_FOR_REVIEW`
