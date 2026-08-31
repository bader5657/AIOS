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
5. The governed helper internally generates exactly one canonical lowercase
   UUIDv4 and the filename
   `.authorization.json.stage-<canonical-lowercase-UUIDv4>`. The exact accepted
   regex is
   `^\.authorization\.json\.stage-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$`;
   for shape only, a conforming name resembles
   `.authorization.json.stage-123e4567-e89b-42d3-a456-426614174000`. No real UUID
   is frozen.
6. Derive `staging_path` only as the exact candidate-root directory plus `/`
   plus that helper-generated canonical filename. A caller, CLI argument,
   environment variable, or authorization payload cannot select a staging name
   or path. No alternate directory, `/tmp`, arbitrary path join, absolute
   injected filename, `../`, slash, backslash, or Unicode path trick is
   accepted.
7. As root, create that exact path with semantics equivalent to `O_WRONLY |
   O_CREAT | O_EXCL | O_NOFOLLOW` and initial mode `0600`. A collision is a
   STOP: do not overwrite, truncate, delete, retry, run a fallback loop, or
   generate a second name during the same governed installation attempt.
8. Require the staged object to be a regular non-symlink file in the governed
   same-directory/filesystem context, never a FIFO, socket, device, or
   directory. Write only the exact approved strict-authorization-JSON bytes,
   completely, with size 1–16384 bytes; flush and `fsync` the file.
9. Before publication, strictly parse JSON, perform closed-schema and
   authorization-semantic validation, compare the exact approved SHA-256, and
   verify size, regular non-symlink type, and staging owner/group/mode. Any
   failure prohibits publication. Only the exact governed privileged procedure
   may transition metadata to `root:aiosadmin` and `0440`; broad `chmod` or
   `chown` is prohibited. Re-`lstat`, re-hash, and verify exact bytes.
10. Atomically publish without replacement by creating the final name as a hard
   link to that same-filesystem staged inode. Plain `linkat` semantics are
   required: final-name existence, including a symlink, fails with `EEXIST` and
   is a STOP. No unlink or retry at the final name is permitted.
11. After publication, `fsync` the candidate-root directory, then verify the
   final path is a regular non-symlink with exact owner, group, mode, size,
   approved SHA-256, and bytes. Publication alone never makes the artifact
   activation-ready and never starts candidate execution.
12. Only after successful final verification, unlink only the exact generated
   staging pathname, `fsync` the parent directory again, verify that staging
   path absent, and verify final `authorization.json` still exact. Wildcards
   such as `rm .authorization*`, directory sweeps, arbitrary hidden-file
   cleanup, and recursive cleanup are prohibited.
13. If exact staging-path removal fails after verified publication, classify
   exactly `AUTHORIZATION_STAGING_CLEANUP_INCOMPLETE`. Leave final
   `authorization.json` present; do not overwrite or delete it automatically,
   retry publication, activate candidate traffic, or execute first write. STOP
   for governance/operator disposition. The residual staging path is never a
   second authorization artifact, and the runtime authorization reader still
   reads only exact `authorization.json`; activation remains blocked until the
   cleanup disposition is resolved.
14. On a failure before final publication, final `authorization.json` remains
   absent. The attempt may remove only its exact generated staging path and only
   when that same governed attempt explicitly permits cleanup. If safe cleanup
   fails, classify exactly
   `AUTHORIZATION_STAGING_PREPUBLICATION_CLEANUP_INCOMPLETE`, STOP, and prohibit
   activation.

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

Future bounded evidence records only: final authorization path; staging
filename and path; `generated internally = YES`; `caller-selected = NO`;
canonical UUID validation; exclusive-create result; payload byte count;
approved, staged, and final SHA-256; publication result; final metadata;
staging-cleanup result; parent-fsync result; and activation eligibility. It must
not record authorization payload contents.

## Production and secret boundary

No database connection, runtime environment read, credential validation,
candidate creation, first-write authorization, or traffic activation belongs to
this procedure. Evidence may contain only paths, inode metadata, hashes, and
bounded probe facts—not a DB password, `runtime.env` contents, `DATABASE_URL`,
tokens, private keys, future authorization payload, or real business data.
