# Runtime Cache, Installed-Unit Preservation, and Bytecode Disposition

## Exact runtime cache authority

Create only:

`/opt/aios/runtime/cache/pycache`

Required final metadata:

- owner/group: `aiosadmin:aiosadmin`;
- directory mode: `0750`;
- writable by `aiosadmin`;
- not world-writable; and
- outside `/opt/aios-src`.

The cache is disposable, non-canonical operational state. It is not backed up
and has no business-data, Registry, Manifest, database, original-file, or
rollback meaning. It must not be created in `/tmp` or any alternate path.

Before cutover, verify the exact path, owner/group, mode, service-user
writability, non-world-writability, and source separation.

## Preserve the installed Stage 9.2.2 unit

Before replacement, preserve:

`/etc/systemd/system/aios.service`

as:

`/opt/aios/runtime/rollback/stage-9.2.3/aios.service.stage-9.2.2`

Record source and backup SHA-256, owner/group, mode, size, and timestamp. The
backup must be byte-identical to the installed predecessor, protected from
world write, and must not overwrite any existing path. Existing Stage 9.2.2
rollback evidence remains untouched.

## Generated-bytecode disposition

Only after the service is stopped and the polling count is exactly zero may
the executor act on source bytecode. The allowed class is limited to already
classified generated `__pycache__/` directories and `.pyc` files beneath
`/opt/aios-src`.

Required sequence:

1. enumerate exact paths without wildcard deletion;
2. verify every entry is a generated cache directory or `.pyc` regular file;
3. record a metadata and hash manifest for regular files without content
   disclosure;
4. reversibly quarantine entries beneath
   `/opt/aios/runtime/rollback/stage-9.2.3/source-bytecode/`, preserving each
   source-relative path; and
5. prove no source `.py`, tracked file, unknown file, or unrelated ignored
   entry moved or changed.

`git clean`, recursive source deletion, unresolved globs, deletion of `.py`,
and treatment of unknown content as bytecode are prohibited. If an entry
cannot be independently proven generated, stop without moving it.
