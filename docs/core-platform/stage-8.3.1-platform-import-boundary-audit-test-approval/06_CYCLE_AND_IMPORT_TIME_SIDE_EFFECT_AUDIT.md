# Cycle and Import-Time Side-Effect Audit

The authorized test must build the smallest deterministic module graph from
Python AST imports for the current Stage 8 runtime and prove:

`PYTHON IMPORT CYCLES = ZERO`.

No third-party graph package is authorized. Python import cycles must be
distinguished from conceptual lifecycle ordering.

The audit must also detect module-level startup of database or external-network
connections, Telegram polling, servers, or singleton external clients without
relying solely on an overbroad substring blacklist. Existing Adapter
configuration/environment loading is accepted. Token validation, Telegram
Application construction, and polling must remain callable startup behavior in
`main()`, not import-time execution.
