# Isolation, Production, and Rollback Verification

## Container and network controls

| Control | Evidence | Result |
|---|---|---|
| Runtime network | internal bridge `aios-ollama-runtime`, subnet `172.31.63.0/29` | `PASS` |
| Runtime IP | `172.31.63.2/29` | `PASS` |
| Container network attachments | runtime network only | `PASS` |
| Public/host port | `PortBindings={}`; `11434/tcp` unpublished; no host listener | `PASS` |
| Privileged | `false` | `PASS` |
| Capabilities | `CapDrop=[ALL]` | `PASS` |
| Privilege escalation | `no-new-privileges=true` | `PASS` |
| Restart policy | `no` | `PASS` |
| Acquisition network attachment | disconnected from container | `PASS` |
| Acquisition network removal | object `aios-ollama-acquisition` still listed | `FAIL` |

The acquisition network has no attachment to the staging container, and the
active runtime network is Docker-internal. However, final closure explicitly
requires that no acquisition network remain. The lingering network object is a
closure blocker even though it does not provide the container an acquisition
path.

## Firewall cleanup

The supplied current operational evidence records temporary acquisition
firewall rules as `REMOVED`. The isolated daemon command line independently
shows `--iptables=false --ip6tables=false`, and the host has no TCP listener on
port `11434`. Direct enumeration of the host nftables ruleset was unavailable
to the unprivileged read-only verifier. No firewall rule was added, removed, or
changed by this task.

## Production isolation

Read-only production checks returned:

| Protected component | Evidence | Result |
|---|---|---|
| `aios.service` | `active/running`; `MainPID=15845`; `NRestarts=0` | `PASS` |
| PostgreSQL | `aios-postgres` healthy; loopback-only `127.0.0.1:5432` | `PASS` |
| Telegram | exactly one process: PID `15845`, `python -m core.adapters.telegram.main` | `PASS` |
| Core/Brain integration | no runtime/container/model reference outside governance records | `NONE` |
| Provider adapter | no Ollama/Qwen provider wiring | `NONE` |
| Production inference authority | not granted | `NONE` |

The production daemon and isolated staging daemon are distinct. No production
container, service, source, secret, network, volume, or configuration was
changed.

## Rollback

Rollback remains staging-only: remove only the named staging container,
staging-only Docker networks, isolated daemon state, and bounded staging
filesystem/config/model assets. Rollback must not prune, delete, restart,
reconfigure, or otherwise touch production containers, images, volumes,
networks, data, services, source, or secrets.
