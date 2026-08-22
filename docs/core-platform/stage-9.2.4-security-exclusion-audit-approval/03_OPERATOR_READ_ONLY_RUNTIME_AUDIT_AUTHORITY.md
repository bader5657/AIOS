# Operator-Assisted Read-Only Runtime Audit Authority

## Operator and target

- Approved channel: `Bagus-PC → aiosadmin@aios-prod-01`
- Interactive `sudo`: allowed only when metadata access requires it
- Codex direct SSH: not required and not authorized as a substitute channel
- Mutation authority: `NONE`

Allowed tools are `stat`, filename/path/type-only `find`, `du`, `mount`,
`findmnt`, mount/path-limited Docker inspection, Git status/check-ignore,
ownership/mode inspection, counts, filename/extensions, and category-only
journal review.

The operator must not print environment values, complete DSNs, passwords,
tokens, private-key contents, business-document contents, Manifest contents,
database pages/rows/dumps, or copied secret content.

## Approved evidence categories and output limits

| Audit | Approved target and report |
|---|---|
| SSH keys | `/home/aiosadmin/.ssh` and necessary host SSH directories; filename, type, owner/group, mode, private/public classification, and inside/outside-source result only |
| PostgreSQL mount | `aios-postgres`; active source and `/var/lib/postgresql/data` target only; no environment/config dump |
| DB dumps/backups | Likely runtime roots; matching path, filename, type, owner/group, mode, count, and size only |
| Business originals | `/opt/aios/data/documents/{images,voice,pdf,docs,links}`; path/type/count/ownership/access metadata only |
| Manifests | `/opt/aios/data/documents/manifests`; path/type/count/ownership metadata only |
| Rollback | `/opt/aios/runtime/rollback`; top-level stages plus filename/type/count/size metadata only |
| Temporary residue | approved temporary/runtime locations; path/count/size/type only |
| Secret metadata | `/opt/aios/runtime/config/runtime.env`; existence, owner/group, mode, and outside-source proof only; expected `root:aiosadmin 0640` |
| Source/Git | `/opt/aios-src`; tracked/staged/untracked classification, clean status, protected filename/type audit, and ignored-state proof without content |

Success requires no private SSH key, secret file, database data/dump, log,
backup/rollback artifact, original business file, Manifest, temporary download,
or runtime cache inside `/opt/aios-src`; active PostgreSQL data must be outside
source; and runtime protected categories must remain outside Git.

No restart, stop, reload, reboot, file move/delete, chmod/chown, migration,
database query/mutation, Docker/Compose change, Storage change, credential
change, or Git mutation is authorized.
