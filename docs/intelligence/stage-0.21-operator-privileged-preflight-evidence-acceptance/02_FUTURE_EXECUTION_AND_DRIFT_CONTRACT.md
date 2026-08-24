# Future Execution and Network Drift Contract

The next execution harness must not invoke `sudo`, `nft`, `iptables`, or `ufw`.
The privileged inspection has already been completed by the operator and is
not to be repeated by Codex or the harness unless observable drift invalidates
the evidence and governance returns to the operator.

Immediately before session creation, the harness must first verify the frozen
evidence identity and SHA-256, then freshly verify without privilege:

- no host listener on port 11434;
- no published port for the staging container;
- the staging container remains attached only to the approved isolated network;
- the acquisition network is absent;
- the expected container IP is unchanged; and
- the staging Docker socket identity is unchanged.

Every item must pass before a new session ID or journal is created. A material
difference is network drift: stop without creating a session and require a new
operator privileged inspection. Safety must not be inferred from stale
evidence.

After exclusive creation of a new append-only journal, the harness must run a
full fresh preflight covering source identity, AIOS `MainPID`/`NRestarts`,
PostgreSQL, Telegram poller, RAM, swap, load, disk, staging container, and
runtime/config identity. Every gate must pass before request admission.

Before each admitted request, the lightweight network gate must freshly verify
that host listener 11434 and published port remain absent, isolated network
identity is unchanged, and acquisition network remains absent. No repeated
privileged inspection is required in the same bounded session unless drift is
detected.

Any gate failure transitions the attempt to `FAILED_CLOSED`, admits no further
request, and permits no retry, fallback, alternate session, or second session
under this authority. Network drift specifically returns control to operator
privileged inspection governance.

