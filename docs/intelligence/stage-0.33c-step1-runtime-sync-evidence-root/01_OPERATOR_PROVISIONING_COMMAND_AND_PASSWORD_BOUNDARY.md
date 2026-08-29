# Operator Provisioning Command and Password Boundary

## Exact future commands

No command is executed by this publication. Because the production-candidate
parent and stage directories are absent, a privileged human operator must first
create the parent chain with explicit metadata, then the evidence root:

```sh
/usr/bin/sudo /usr/bin/install -d -o root -g aiosadmin -m 0750 /opt/aios/runtime/intelligence/production-candidate-create
/usr/bin/sudo /usr/bin/install -d -o root -g aiosadmin -m 0750 /opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c
/usr/bin/sudo /usr/bin/install -d -o aiosadmin -g aiosadmin -m 0750 /opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/runtime-sync-evidence
```

The operator must inspect each path with non-following metadata checks before
and after these commands. The commands are exact-path only; no shell root
session, wildcard, recursive ownership, arbitrary `mkdir`, chmod/chown repair,
or deletion/recreation is permitted. If any existing component has unexpected
type, symlink state, owner, group, or mode, STOP rather than repair it.

The first two commands preserve the existing `root:root` intelligence parent
boundary while granting the explicitly governed `aiosadmin` group traversal.
The third establishes the runtime-sync evidence child. This is Step 1 support
infrastructure and is not authorization.json or consumed-directory provisioning.

## Password boundary

The terminal operator alone may satisfy sudo authentication. Codex must never
request, receive, store, log, pipe, or place a sudo password in a command,
document, environment, or evidence record. No production secret value is
needed for these commands.

Project Owner approval for this publication covers only publication of this
contract. Future provisioning still requires fresh independent review and
human operator execution of these exact commands. It does not approve runtime
source synchronization, service restart, Step 2, candidate creation, or
first-write authority.
