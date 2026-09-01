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
6. verify the exact approved source byte objects are regular non-symlink files,
   bounded to their exact transport sizes and hashes, without logging their
   contents.

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

The helper creates the staged object relative to the retained directory
descriptor with semantics equivalent to `O_WRONLY | O_CREAT | O_EXCL |
O_NOFOLLOW` and initial mode `0600`. It requires a regular non-symlink object on
the candidate root's filesystem, writes only the already-approved transport
bytes to completion, flushes and file-`fsync`s, and rejects short writes or
trailing bytes. Before publication it sets only the exact final metadata
`root:aiosadmin` and `0440`, then reopens without following symlinks and verifies
type, device, owner, group, mode, byte count, and SHA-256:

| Final basename | Transport bytes | Required SHA-256 |
|---|---:|---|
| `approved-input.json` | `1328` | `e3c66fddf815c57f17baad49926c44588279d60cb4e78df867e0ae2189237a6d` |
| `approved-input-approval.json` | `3550` | `266c39426fae0b04dacf009436334dd34d6791368dcad5066a9b2a37b9bd8a57` |

Publication uses the established Stage 0.33C same-filesystem hard-link model:
plain `linkat`-equivalent semantics from the complete staged inode to the fixed
final basename. It is atomic and no-replace; any existing final object produces
`EEXIST` and a STOP. The executor must never unlink, truncate, chmod, chown,
overwrite, or replace an existing final object and must not retry publication.
The final name can therefore expose only the already complete inode.

After each publication, the helper `fsync`s the parent directory, opens the
final path without following symlinks, and independently verifies regular-file
type, device, `root:aiosadmin`, `0440`, exact transport byte count, exact
SHA-256, and byte-for-byte equality with the approved source object. Only then
may it unlink that artifact's exact staging pathname, `fsync` the parent again,
verify staging absence, and reverify the final object. Wildcards, directory
sweeps, recursive cleanup, and arbitrary hidden-file removal are prohibited.

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

Any metadata, size, hash, byte, approval-window, path, staging, durability, or
pair-verification mismatch fails closed. Publication success never invokes the
harness or controlled callable and never authorizes candidate or database
activity.

## Bounded evidence contract

Future execution evidence may record only:

- reviewed governance commit and installer/helper hash;
- fixed parent and final paths;
- source, staged, and final byte counts and SHA-256 values;
- non-following type, device, ownership, group, and mode checks;
- approval validity result and exclusive-expiry comparison result, without raw
  approval JSON;
- internally generated staging basenames, `caller-selected = NO`, exclusive
  creation results, file and parent `fsync` results;
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
