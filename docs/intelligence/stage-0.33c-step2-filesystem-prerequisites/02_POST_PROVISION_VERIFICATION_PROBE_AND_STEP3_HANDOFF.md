# Stage 0.33C-P2 Post-Provision Verification, Probe, and Step-3 Handoff

## Exact non-sudo metadata verification

After future human provisioning, run as `aiosadmin` (not through sudo):

```sh
/usr/bin/namei -l /opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c
/usr/bin/stat -c 'type=%F owner=%U group=%G mode=%a inode=%i' /opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c
/usr/bin/namei -l /opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/consumed
/usr/bin/stat -c 'type=%F owner=%U group=%G mode=%a inode=%i' /opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/consumed
/usr/bin/test ! -e /opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/authorization.json
/usr/bin/test ! -L /opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/authorization.json
```

Require the candidate root to be a real non-symlink directory,
`root:aiosadmin`, `0750`; require `consumed` to be a real non-symlink directory,
`aiosadmin:aiosadmin`, `0700`; and require `authorization.json` absent. Any
unexpected output or status is a STOP.

## Exactly one consumed-directory write probe

Run the following once, non-sudo, as `aiosadmin:aiosadmin`, only after metadata
verification. It creates one `probe-<canonical-lowercase-UUIDv4>` name with no
`.json` suffix, never a bare authorization marker name. The content is fixed,
bounded, and non-secret. `O_EXCL|O_NOFOLLOW` makes collision a STOP with no
overwrite; mode is `0600`.

```sh
/usr/bin/python3 - <<'PY'
import os
import stat
import uuid

directory = "/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/consumed"
content = b"AIOS_STAGE_0_33C_STEP2_WRITE_PROBE\n"
name = "probe-" + str(uuid.uuid4())
path = os.path.join(directory, name)
flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
fd = None
created = False
try:
    fd = os.open(path, flags, 0o600)
    created = True
    with os.fdopen(fd, "wb", closefd=True) as stream:
        fd = None
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
    st = os.lstat(path)
    if not stat.S_ISREG(st.st_mode):
        raise RuntimeError("probe is not regular")
    if stat.S_IMODE(st.st_mode) != 0o600:
        raise RuntimeError("probe mode mismatch")
    if st.st_uid != os.getuid() or st.st_gid != os.getgid():
        raise RuntimeError("probe identity mismatch")
    with open(path, "rb", buffering=0) as check:
        if check.read(len(content) + 1) != content:
            raise RuntimeError("probe content mismatch")
    dirfd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(dirfd)
    finally:
        os.close(dirfd)
    os.unlink(path)
    created = False
    dirfd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(dirfd)
    finally:
        os.close(dirfd)
    if os.path.lexists(path):
        raise RuntimeError("probe cleanup failed")
    print("STEP2_CONSUMED_WRITE_PROBE=PASS")
except Exception:
    if fd is not None:
        os.close(fd)
    if created:
        print("STEP2_CONSUMED_WRITE_PROBE=STOP; exact probe preserved for review")
    raise
PY
```

On a failure after exclusive creation, the probe is deliberately preserved for
review rather than silently deleted; this is fail-closed cleanup behavior. A
successful run flushes and fsyncs the file, fsyncs the parent, deletes the exact
probe, fsyncs the parent again, and verifies absence. The name cannot activate
or consume authority, and the probe does not contact a database.

## Evidence and closure

Step 2 requires its own post-provision evidence session. It must not reuse or
write into Step-1 `runtime-sync-evidence`. No additional on-host evidence root is
needed or authorized: the human-reviewed command transcript, limited to the
metadata outputs and bounded PASS fact above, must be published in a later
documentation-only Step-2 closure record. Thus this package introduces no
silent evidence-directory provisioning requirement.

Step 2 may close only when that later review proves: exact candidate-root and
consumed metadata; the write/flush/file-fsync/parent-fsync probe PASS and clean
removal; `authorization.json` still absent; no secret exposure; no PostgreSQL
contact; and no candidate creation. Filesystem provisioning remains `NO` in this
publication, so Step 2 is not closed here.

Even after a later Step-2 PASS, Step 3 does not start automatically. It requires
separate governance for an ephemeral one-shot harness. No production input,
authorization artifact, first-write authority, candidate traffic, or production
write is approved by this package. The next official action after this PR is
fresh independent review; after merge, a human operator may perform only the
exact governed consumed-directory provisioning and verification sequence.
