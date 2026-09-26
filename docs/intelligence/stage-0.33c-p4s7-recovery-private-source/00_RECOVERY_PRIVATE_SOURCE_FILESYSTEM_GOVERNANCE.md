# AIOS P4S7-R31A Recovery Private-Source Filesystem Governance

Classification: `P4S7_RECOVERY_PRIVATE_SOURCE_FILESYSTEM_GOVERNANCE_READY_FOR_REVIEW`

## Purpose and authority

This governance-only amendment resolves the storage specification portion of
the R31 blocker. It freezes one distinct private recovery approval location
under recovery authority `7bc638e2-e1f4-4e87-a54a-4d0df031b130`.
That identity remains inactive: this document does not activate execution
authority or authorize directory creation, approval creation, installation,
or Step 5. Independent review and human merge are required; no automatic merge.

The governing recovery amendment is [R30](../stage-0.33c-p4s7-approval-expiry-recovery/00_APPROVAL_EXPIRY_RECOVERY_AMENDMENT.md),
merged through PR #297 at `f3188f8d61cccf58c2ad7f6c3b6bdbcf5acb1606`.
All R30 approval, validity, diff, binding, review, and recovery-order gates
remain mandatory. This document governs filesystem custody only and does not
renew approval or change its closed schema.

R31 reported that private-path safety could not be verified: `/run/aios`
was root-only and privileged inspection required a sudo password. Recovery
directory existence and metadata remain unverified. This document makes no
claim that a private path is absent, safe, or already prepared.

## Immutable history and logical source pair

Preserve these exact historical sources byte-for-byte and with their existing
metadata, without copy, hardlink, rename, relocation, overwrite, or deletion:

| Historical source | Exact path |
|---|---|
| Approved input | `/run/aios/stage-0.33c-p4s5-source/approved-input.json` |
| Approval | `/run/aios/stage-0.33c-p4s5-source/approved-input-approval.json` |

Preserve the historical activation at
`/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/p4s7-r13-post-merge-activation.json`
and all old authority evidence without modification or deletion.

The recovery source pair is logically composed of the historical
approved-input reference plus the new recovery approval artifact. Future
recovery must read approved-input at its exact historical path above. Do not
duplicate, copy, hardlink, symlink, or rewrite approved-input into the recovery
directory. No filesystem reference object is created by this reference model.
The historical approval is preserved as history, not reused as fresh approval.
Later executor source binding must explicitly support these two distinct paths
under its separately reviewed amendment; this document changes no executor.

## Frozen recovery paths and root custody

| Object | Exact path | Required future metadata |
|---|---|---|
| Recovery directory | `/run/aios/stage-0.33c-p4s5-recovery-source` | Real non-symlink directory; owner root (UID 0), group root (GID 0), mode `0700` |
| Fresh approval | `/run/aios/stage-0.33c-p4s5-recovery-source/approved-input-approval.json` | Regular non-symlink file; root:root, mode `0400`, `st_nlink == 1` |

Custody remains with the privileged root operator. No group/world write,
writable aliases, or relaxed access grants are permitted. Do not invent
alternate paths or repair conflicting pre-existing entries. The approval
target must be absent before future exclusive publication; any existing
target is STOP, even if it appears to contain the intended bytes.

## Privileged read-only verification before creation

After independent governance review and human merge, a privileged operator
must perform and retain read-only verification before any directory or file
creation. Verify `/run`, `/run/aios`, and recovery-child absence or exact
governed metadata. Obtain separately explicit authorization for any subsequent
creation; neither merge nor a successful inspection is creation permission.

Walk from a trusted root descriptor using directory-relative, no-follow
operations. Retain descriptors for `/run`, `/run/aios`, and the recovery child
once present. Use `O_DIRECTORY|O_NOFOLLOW` directory opens and descriptor
metadata checks; do not rely on a prior pathname-only check followed by an
unprotected open. Require:

- `/run` exists as a real non-symlink directory.
- `/run/aios` exists as a real non-symlink directory, root:root, mode `0700`.
- The recovery child is absent or is a real non-symlink directory with exactly
  root:root ownership and mode `0700`.

Record device/inode identities for retained ancestors and for the child when
present. Reopen entries relative to their retained parents and compare
device/inode and metadata. Confirm the live pathname chain still identifies
the retained directories at verification and publication boundaries. Any
substitution, identity drift, symlink, inaccessible component, missing required
ancestor, or conflicting metadata is STOP. Do not create or take over `/run`
or `/run/aios` under this amendment. No recursive takeover or replacement.

## Future exclusive directory creation and durability

If the recovery child is absent and creation is separately authorized, create
only `stage-0.33c-p4s5-recovery-source` relative to the retained `/run/aios`
descriptor, exclusively with mode `0700`. A collision, including an entry
appearing after the absence check, is STOP; do not accept it as the newly
created child or retry by replacing it.

Open the created child no-follow relative to the retained parent. Record
parent and child device/inode identities. Set root:root ownership and mode
`0700` using the child descriptor, and verify both. Fsync the child where
supported, then fsync the retained parent. Record any explicitly unsupported
child-directory fsync result; do not silently ignore other errors or claim
durability that was not established. A parent fsync failure is STOP.

Reopen the child read-only/no-follow as a directory relative to the retained
parent and require exact device/inode stability and all governed metadata.
Recheck ancestor identities. No fresh approval bytes may be written until
directory verification is PASS.

An already existing child may be used only after privileged read-only checks
establish its exact governed metadata and stable identity. Do not chmod,
chown, replace, or repair a pre-existing conflicting entry. Record whether
the child pre-existed or was exclusively created. Retain descriptors through
future file publication and verification.

## Future exclusive approval publication

Only a separately authorized fresh approval creation may publish the target.
All R30 semantic, historical-preservation, canonicalization, owner-approval,
and validity gates must also pass. No UUID, timestamp, approval bytes, or
fresh binding values are generated by this governance task.

Future publication must use the verified, retained recovery directory
descriptor and this order:

1. Open `approved-input-approval.json` relative to that descriptor with
   `O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW` and restrictive initial mode `0600`.
   Any collision is STOP, with no overwrite or fallback.
2. Verify the new file is regular with `st_nlink == 1`; record device/inode.
   Write the complete canonical transport bytes, handling short writes.
   Transport is R30 canonical UTF-8 JSON plus exactly one ASCII LF.
3. Fchown the file to root:root and fchmod it to `0400`; verify metadata.
4. Fsync the file, close every writable descriptor, then fsync the retained
   recovery directory descriptor.
5. Reopen the target read-only with `O_NOFOLLOW`, relative to that retained
   directory. Require the same file device/inode, regular non-symlink type,
   root:root, mode `0400`, and `st_nlink == 1`; no writable aliases.
6. Verify exact bytes, counts, semantic and transport hashes, canonical
   serialization, duplicate-key rejection, closed schema, derived payload
   checksum, and the R30 allowlisted type-sensitive diff. Recheck directory
   identities and historical preservation. Retain sanitized verification
   evidence; never print raw business facts or full approval JSON.

A failed or partial publication is STOP. No overwrite, automatic retry,
cleanup, replacement, or permission repair is implied. Preserve the observed
state for separately governed disposition. Independent approval verification
remains a separate later gate, even after publication checks pass.

## Current boundaries and next action

| Action in R31A | Result |
|---|---|
| Recovery directory created | NO |
| Fresh approval created | NO |
| Historical input, approval, activation, or old authority evidence modified | NO |
| Approved-input duplicated, copied, hardlinked, symlinked, or rewritten | NO |
| Runtime modified | NO |
| Executor modified | NO |
| Installer executed or authorized | NO |
| Claim or targets created | NO |
| PostgreSQL contacted | NO |
| Harness invoked, candidate or authorization.json created | NO |
| Step 5 authorized | NO |

Next official action: independent review of this single governance document,
then human merge if accepted. After merge, privileged read-only verification
must establish path safety; future directory and fresh approval creation
require separate explicit authorization and all applicable R30 gates.
Installer execution and Step 5 remain unauthorized. STOP.
