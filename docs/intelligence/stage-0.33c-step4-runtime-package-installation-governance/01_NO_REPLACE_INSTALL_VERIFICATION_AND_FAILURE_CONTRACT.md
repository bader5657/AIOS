# Stage 0.33C-P4S3-R1 No-Replace Install and Failure Contract

## Preflight and safe path resolution

The future separately authorized executor must use fixed constants for the
candidate root and both final basenames. Before creating anything, it must:

1. inspect every existing component from `/opt` through the candidate root
   without following symlinks and require real directories with the reviewed
   identity and access properties;
2. open the candidate root using directory and no-follow semantics and retain
   that directory descriptor for relative operations;
3. require the root itself to be `root:aiosadmin`, mode `0750`, and on one
   stable device for the attempt;
4. use non-following lookups to require both final basenames absent; any object,
   including a symlink, is `UNEXPECTED_PREEXISTING_APPROVED_INPUT_TARGET` and a
   STOP;
5. reject governed staging-name collisions and unexpected staging debris; and
6. verify the exact approved source byte objects are regular non-symlink files
   and satisfy their exact transport-length, terminal-LF, and semantic-prefix
   hash contracts without logging their contents.

No absolute caller-selected staging path, `..`, separator, backslash, Unicode
path trick, `/tmp`, alternate filesystem, environment-selected component, or
payload-selected pathname is accepted. No direct shell redirection, `cp`,
generic `mv`, or `install` into a final path is permitted.

## Exact staging and publication model

The installation authority must publish the two artifacts sequentially in this
fixed order: `approved-input.json`, then `approved-input-approval.json`. For
each artifact, the reviewed helper internally generates exactly one canonical
lowercase UUIDv4 and derives the same-directory staging basename:

- `.approved-input.json.stage-<canonical-lowercase-UUIDv4>`; or
- `.approved-input-approval.json.stage-<canonical-lowercase-UUIDv4>`.

Each accepted basename must match its fixed prefix followed by
`[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}`.
The caller cannot supply the UUID or name. One collision stops the attempt;
there is no deletion, fallback loop, second UUID, or reuse.

For each artifact, the helper must complete this lifecycle in order:

1. create the unique staged object relative to the retained directory
   descriptor with semantics equivalent to `O_WRONLY | O_CREAT | O_EXCL |
   O_NOFOLLOW` and initial mode `0600`;
2. require a regular non-symlink object on the candidate root's filesystem and
   write only the already-approved transport bytes to completion, rejecting
   short writes and trailing bytes;
3. flush userspace state if applicable and file-`fsync` the staging object;
4. set exactly `root:aiosadmin` ownership and mode `0440`, and `fsync` metadata
   as required by the governed installation design;
5. close every writable descriptor, treating any close, `fsync`, ownership, or
   permission-setting failure as an installation failure that leaves the final
   target absent;
6. prove that no `O_WRONLY` or `O_RDWR` descriptor controlled by the installer
   still references the staged inode, then reopen it read-only with no-follow
   semantics if descriptor-based verification is required; and
7. through read-only access, verify type, device, owner, group, exact mode, and
   the applicable byte-domain contract below.

Setting mode `0440` does not revoke write authority retained by an already-open
`O_WRONLY` or `O_RDWR` descriptor. Publication is prohibited until every such
installer-controlled descriptor has been closed and its absence proved. A
close or read-only reopen failure must fail closed; the helper must not publish,
weaken permissions, or reopen either staging or final path writable.

| Final basename | Semantic bytes | Transport bytes | Required semantic-prefix SHA-256 |
|---|---:|---:|---|
| `approved-input.json` | `1327` | `1328` | `e3c66fddf815c57f17baad49926c44588279d60cb4e78df867e0ae2189237a6d` |
| `approved-input-approval.json` | `3549` | `3550` | `266c39426fae0b04dacf009436334dd34d6791368dcad5066a9b2a37b9bd8a57` |

For `approved-input.json`, verification requires an exact 1,328-byte transport
file, bytes `[0:1327]` as the semantic payload, SHA-256 of exactly that prefix
equal to the table value, byte `[1327]` equal to `0x0A`, and no later byte. For
`approved-input-approval.json`, it requires an exact 3,550-byte transport file,
bytes `[0:3549]` as the semantic payload, SHA-256 of exactly that prefix equal
to the table value, byte `[3549]` equal to `0x0A`, and no later byte. Thus each
file contains exactly one terminal LF. No transport-file SHA is frozen or
required: fixed semantic length and frozen semantic SHA, exact terminal byte,
and exact total length bind the transport bytes without conflating the two byte
domains.

Only after that read-only pre-publication verification passes, publication uses
the established Stage 0.33C same-filesystem hard-link model: plain
`linkat`-equivalent semantics from the complete staged inode to the fixed final
basename. The destination must still be absent. Link creation is atomic and
no-replace; any existing final object produces `EEXIST` and a STOP. The executor must never unlink, truncate, chmod, chown,
overwrite, or replace an existing final object and must not retry publication.
The final name can therefore expose only the already complete inode, with no
installer-controlled writable staging handle through which published content
could subsequently be modified.

After each publication, the helper `fsync`s the parent directory, opens the
final path read-only without following symlinks, and independently verifies
regular-file type, device, `root:aiosadmin`, exact mode `0440`, exact transport
length, exactly one terminal `0x0A`, the exact semantic-prefix length and frozen
semantic SHA, no extra bytes, and byte-for-byte equality with the approved
source object. It must also prove no installer-controlled writable descriptor
references the published inode. Only then may it unlink that artifact's exact
staging pathname, `fsync` the parent again, verify staging absence, and reverify
the final object. It must not leave the staging pathname as an uncontrolled
writable alias or reopen staging or final paths writable. If absence of a
writable descriptor or alias cannot be proved, fail closed and require separate
incident/recovery governance. Wildcards, directory sweeps, recursive cleanup,
and arbitrary hidden-file removal are prohibited.

After both objects pass independently, the executor must verify the pair again
and record that both are present and exact. The pair is not usable and Step 4
is not closure-eligible unless both final objects and every bound relationship
pass in the same reviewed evidence session.

## Failure and rollback semantics

Before publication of an artifact, failure must leave its final basename
absent. Cleanup may remove only the exact staging object created by that
attempt. If exact cleanup is unsafe or fails, preserve the object and classify
`APPROVED_INPUT_STAGING_PREPUBLICATION_CLEANUP_INCOMPLETE`; do not publish,
retry, or broaden cleanup.

After successful final publication, the final object is immutable under this
authority. It must not be deleted, overwritten, renamed, replaced, or repaired
automatically. Failure to remove its exact staging link is
`APPROVED_INPUT_STAGING_CLEANUP_INCOMPLETE`; leave the verified final object and
residual staging object in place, block package use, and require separate
incident/recovery governance.

If `approved-input.json` publishes but publication or verification of
`approved-input-approval.json` fails, classify
`STEP4_APPROVED_INPUT_PARTIAL_INSTALLATION`. Preserve the first final object,
do not overwrite or delete it, do not retry the second publication, do not
invoke the harness, and require separate incident/recovery governance. The same
partial-install classification applies to any state where exactly one final
artifact is present. This governance grants no rollback-by-replacement.

Any descriptor close or read-only reopen failure, metadata, size, hash, byte,
approval-window, path, staging, durability, or pair-verification mismatch fails
closed. Pre-publication failure leaves the final target absent and is an
installation failure; permissions must never be weakened as a retry.
Publication success never invokes the
harness or controlled callable and never authorizes candidate or database
activity.

## Bounded evidence contract

Future execution evidence may record only:

- reviewed governance commit and installer/helper hash;
- fixed parent and final paths;
- source, staged, and final semantic/transport byte counts, terminal-LF checks,
  and semantic-prefix SHA-256 values;
- non-following type, device, ownership, group, and mode checks;
- approval validity result and exclusive-expiry comparison result, without raw
  approval JSON;
- internally generated staging basenames, `caller-selected = NO`, exclusive
  creation results, file and parent `fsync` results, writable-descriptor close
  and absence proofs, and read-only reopen results;
- atomic no-replace publication results and final pair verification;
- exact-path cleanup results and any closed failure classification; and
- zero harness, candidate, inventory, stock, authorization, and PostgreSQL
  effects.

Evidence must not contain approved-input contents, approval-record contents,
retained content, OCR, business facts, credentials, DSNs, environment contents,
tokens, or private keys.

This package authorizes no runtime mutation. Its successful classification is
`STEP4_RUNTIME_PACKAGE_INSTALLATION_GOVERNANCE_READY`, subject to independent
review and merge. Step 4 remains open and Step 5 remains unauthorized.
