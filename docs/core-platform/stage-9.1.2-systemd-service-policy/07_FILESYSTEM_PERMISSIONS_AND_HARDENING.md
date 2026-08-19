# Filesystem Permissions and Hardening

The service identity receives:

- read/execute access to `/opt/aios-src`, with no runtime-generated source changes;
- read/execute access to `/opt/aios/runtime/venv`;
- read-only access to `/opt/aios/runtime/config/runtime.env`;
- read/write access only to approved `/opt/aios/data/documents/...` directories and required temporary runtime locations;
- no broad `/opt`, source-repository, secret, database, log, or backup write permission.

Expected runtime data directories are owned `aiosadmin:aiosadmin` with directory mode `0750`. The unit policy includes `UMask=0027` for newly created runtime files.

The approved minimal hardening is:

- `NoNewPrivileges=true`
- `PrivateTmp=true`

`ProtectSystem`, `ProtectHome`, and more complex path exceptions are deferred to a later security review because they could conflict with approved `/opt/aios` writes. Non-root identity and bounded permissions remain mandatory.
