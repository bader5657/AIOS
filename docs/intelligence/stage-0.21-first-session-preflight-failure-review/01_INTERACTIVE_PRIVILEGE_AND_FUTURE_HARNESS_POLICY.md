# Interactive Privilege and Future Harness Policy

## Approved future authentication boundary

For a separately reauthorized session, interactive operator authentication is
permitted solely for the minimum already-governed read-only inspection set:

- `nft list ruleset`;
- `iptables-save`;
- `iptables -S`;
- `iptables -t nat -S`;
- `ufw status`; and
- minimal read-only listener, Docker container, and network inspection.

`sudo -n` is not required. Password storage, logging, echoing, scripting,
piping through `sudo -S`, embedded credentials, sudoers modification,
persistent privilege escalation, and all state-changing firewall, NAT,
network, routing, sysctl, or Docker commands remain prohibited.

Interactive authentication grants no broader authority. A failed, cancelled,
expired, incomplete, or indeterminate inspection remains fail-closed.

## Selected future harness behavior: A

The future operator-controlled harness must pause before session creation and
require completion of the privileged read-only preflight. It may proceed only
after all network criteria are freshly and determinately `PASS`.

The operator performs the approved commands interactively; the harness must
not capture a password. The bounded, secret-free inspection result is carried
forward into the auditable session record. Only after `PASS` may the harness:

1. generate one new session identifier;
2. exclusive-create one new journal;
3. record the pre-admission privileged evidence and remaining fresh gates;
4. enter the governed session lifecycle; and
5. construct the composition only after the complete session preflight passes.

If privileged inspection does not pass, the harness stops before session and
journal admission. It must not reuse the failed journal or its identifier, and
must not attempt inference. This sequence keeps privilege handling explicitly
operator-controlled while preserving a complete auditable record for any
session that is actually admitted.

Option B, direct interactive sudo after session admission, is not selected for
the next authorization because it unnecessarily consumes a session artifact
before the prerequisite access gate is known to be available.

