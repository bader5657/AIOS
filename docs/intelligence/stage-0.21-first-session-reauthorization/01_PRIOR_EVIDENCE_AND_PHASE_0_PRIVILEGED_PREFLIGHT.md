# Prior Evidence and Mandatory Phase 0 Privileged Preflight

## Permanently consumed evidence

The previous session identifier is:

`stage-0.21-level-b-session-20260824T101928663982Z-6b257eca00ef463dbde3fe249e8be6b7`

Its journal is exactly:

`/opt/aios/runtime/intelligence/staging/level-b-sessions/stage-0.21-level-b-session-20260824T101928663982Z-6b257eca00ef463dbde3fe249e8be6b7.jsonl`

Verified SHA-256:

`70599c4d285ec559d72a7905a8bdc355bea18fc9002770f60c16723c7d9eaaeb`

The `FAILED_CLOSED` journal records request count zero, live inference count
zero, provider calls zero, and `/api/chat` calls zero. It must never be
modified, reopened, appended, renamed, reused, or deleted.

## Phase 0 ordering

Before any session exists, an operator must complete the approved privileged
read-only network inspection. It must deterministically prove:

- no public Ollama exposure;
- no host publication or listener on port `11434`;
- no acquisition network;
- no DNAT or public-ingress exposure;
- no unexpected firewall/NAT drift; and
- the isolated staging runtime remains private.

Interactive sudo authentication is authorized solely for the minimum required
read-only commands, including `nft list ruleset`, `iptables-save`,
`iptables -S`, `iptables -t nat -S`, `ufw status verbose`, and governed
read-only Docker/listener/network inspection. `sudo -n` is not required.

Passwords must not be stored, logged, echoed, embedded, piped with `sudo -S`,
or otherwise retained. Sudoers modification, persistent elevation, and every
state-changing firewall, NAT, network, routing, sysctl, or Docker command are
prohibited.

Retain only bounded, secret-free operator evidence associated with this
reauthorization task; it must not claim that a live Level B session existed.
If inspection fails, is unavailable, or is indeterminate, stop and return to
governance without generating a session ID, creating a journal or composition,
or performing inference.

Only a deterministic Phase 0 `PASS` permits one fresh UUID-backed session ID
and one exclusive-created new journal. The new ID must differ from every prior
ID. A journal collision stops the attempt; no alternate-ID retry is authorized.

