# Stage 0.33C-P2 Provisioning, Atomic Install, and Password Boundary

## Exact consumed-directory provisioning command

After independent review and merge, a human operator may execute exactly:

```sh
/usr/bin/sudo /usr/bin/install -d \
  -o aiosadmin \
  -g aiosadmin \
  -m 0700 \
  /opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/consumed
```

This publication does not execute it. Before execution, non-following checks
must reconfirm the candidate root exact and classify `consumed` as `ABSENT`; if
it is present, the command is not run and the existing-path policy applies.
There is no repair authority.

The terminal operator alone may satisfy sudo authentication. Codex, scripts,
logs, and evidence must never request, receive, store, echo, or pipe a sudo
password. Project Owner approval here covers governance publication only.
Privileged execution requires independent review, merge, and a human operator.

## Frozen future authorization-install model

Step 2 must not run this model. A later, separately approved first-write stage
must bind an already-approved source file and its lowercase SHA-256, then use a
privileged operator procedure with all of these exact semantics:

1. Recheck every parent with `lstat`; STOP on a symlink or metadata drift.
2. Require the final path absent using non-following lookup; any existing object
   is a STOP.
3. Require the approved source to be an absolute-path, regular, non-symlink file.
4. Read at most 16385 bytes; require 1–16384 bytes, strict UTF-8 strict JSON with
   no trailing bytes, and exact match to the separately approved SHA-256. The
   approved schema must exclude credentials, passwords, `DATABASE_URL`, tokens,
   private keys, and other secret fields.
5. As root, create a randomly named hidden temporary regular file in the same
   candidate root with exclusive creation and no symlink following. Use mode
   `0600` during population; collision is a STOP, never an overwrite.
6. Write the exact approved bytes completely, flush, `fsync` the file, set
   `root:aiosadmin` and `0440`, then re-`lstat` and re-hash it.
7. Atomically publish without replacement by creating the final name as a hard
   link to that same-filesystem staged inode. Plain `linkat` semantics are
   required: final-name existence, including a symlink, fails with `EEXIST` and
   is a STOP. No unlink or retry at the final name is permitted.
8. `fsync` the candidate-root directory, unlink only the exact hidden staging
   name, `fsync` the directory again, and verify final type, owner, group, mode,
   size, and SHA-256. On any failure before publication, remove only the exact
   staging inode after identity verification. On any failure after publication,
   STOP and preserve the artifact for separately governed review.

The hard-link publication is the atomic same-directory equivalent of a
no-replace rename: the fully written, synced, correctly owned inode appears at
`authorization.json` in one namespace operation, so partial JSON is never
visible. It also preserves the mandatory no-overwrite policy. Generic `mv`,
`cp`, redirection to the final path, `install` directly to the final path, and
rename-with-replacement are prohibited.

The later authority must publish the reviewed implementation or exact operator
helper that realizes these syscall-level semantics and must bind its source
path, approved byte hash, and helper hash. This package freezes the method but
does not publish authorization bytes, create a helper, or authorize invocation.

## Production and secret boundary

No database connection, runtime environment read, credential validation,
candidate creation, first-write authorization, or traffic activation belongs to
this procedure. Evidence may contain only paths, inode metadata, hashes, and
bounded probe facts—not a DB password, `runtime.env` contents, `DATABASE_URL`,
tokens, private keys, future authorization payload, or real business data.
