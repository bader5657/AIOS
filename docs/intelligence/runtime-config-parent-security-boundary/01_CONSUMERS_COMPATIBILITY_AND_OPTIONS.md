# Consumers, Compatibility, and Options

## Actual consumers

The only production config object is `runtime.env`. The active
`aios.service` runs as Linux user/group `aiosadmin`, uses
`EnvironmentFile=/opt/aios/runtime/config/runtime.env`, and the Python Telegram
entrypoint also loads that same file. The systemd manager reads the EnvironmentFile
as root; the application needs traverse access to the path and group-read access
to the file. The service is active/running with no dynamic user.

Repository, systemd, cron/timer, process, and open-file inspection found no
legitimate non-root writer, rotation job, secret refresher, temporary-file
writer, or runtime-state writer targeting `runtime/config`. Runtime writes use
separate existing children such as `runtime/cache`; existing `venv`, `cache`,
`rollback`, and `verification` directories remain owned by `aiosadmin` and can
remain writable internally.

PostgreSQL LOGIN identities are database principals, not Linux users, and need
no filesystem access.

## Option decision

- `root:aiosadmin 0750` for `config` is the correct leaf policy but is unsafe
  unless writable ancestors are hardened too.
- `0755` for `config` unnecessarily exposes names/traversal to other users.
- a separate secret child under the current writable ancestor chain does not
  solve path replacement.
- ACLs add no needed expressiveness; owner/group/mode is sufficient.
- a sticky bit is rejected. It is intended for shared writable directories,
  retains unnecessary write capability, and does not establish this dedicated
  root-only writer boundary across the ancestor chain.

No new secret-directory architecture is required. Minimal correction is to
secure the three existing directory entries while leaving their established
children and data locations unchanged.
