# Command Scope, Pass Criteria, and Evidence

## Minimum read-only command scope

The operator may use only the smallest necessary subset of:

- `sudo nft list ruleset`;
- `sudo iptables-save`;
- `sudo iptables -S`;
- `sudo iptables -t nat -S`;
- `sudo ufw status`;
- read-only Docker network/container inspection; and
- read-only host listener inspection.

Interactive sudo authentication is allowed solely for these read-only
commands. Never store, log, echo, script, or pipe the password; do not use
embedded credentials or `sudo -S`; and do not alter sudoers or establish
persistent privilege.

Any append, delete, insert, replace, flush, allow, deny, enable, disable,
reload, connect, disconnect, create, remove, restart, sysctl, routing, firewall,
NAT, or Docker-network mutation is prohibited.

## Exact pass criteria

PASS requires bounded evidence that:

1. the staging container is attached only to the approved internal runtime
   network;
2. the acquisition network is absent/disconnected;
3. port 11434 has no host publication or public listener;
4. no stale Stage 0.6.x or Stage 0.20 temporary allow/NAT rule exists;
5. no DNAT exposes the staging endpoint externally; and
6. no unexpected FORWARD rule permits public ingress to staging Ollama.

Normal Docker masquerade for the approved internal bridge is not a failure
unless it enables public inbound exposure. Any unexpected or indeterminate
rule stops inspection without repair or mutation.

## Evidence retention

Retain one bounded, secret-free record at:

`/opt/aios/runtime/intelligence/staging/stage-0.20-evidence/01_PRIVILEGED_NETWORK_PREFLIGHT.json`

It records command names, timestamps, exit codes, only relevant firewall/NAT
lines, listener and Docker-network state, and final classification. It must not
overwrite the existing blocked-preflight record or retain unrelated sensitive
host information.
