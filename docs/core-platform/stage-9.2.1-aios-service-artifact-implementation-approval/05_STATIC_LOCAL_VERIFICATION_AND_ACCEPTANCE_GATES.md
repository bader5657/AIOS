# Static/Local Verification and Acceptance Gates

The authorized static test must parse the actual tracked unit and verify:

- exact path, sections, directives, and single occurrence of each section;
- exactly one `ExecStart` and the approved `ExecStartPre`;
- required non-optional EnvironmentFile;
- non-root identity, entrypoint, restart/rate-limit/shutdown/hardening values;
- `WantedBy=multi-user.target`;
- absence of secrets, test DSN, migrations, Docker/Compose execution, shell retry/wait loops, logging files, application containers, and later-phase behavior.

Local verification requires the focused static test, relevant regression suite, compile/static checks, dependency/prohibited-source audit, and `git diff --check`. `systemd-analyze verify` on local systemd 255 is an approved supplementary diagnostic; it is not the sole portable gate because production-only user and absolute paths may be absent locally.

Acceptance requires exactly two implementation paths, exact directives, valid static parse, no production activation, no runtime/Docker/database change, one ExecStart, preserved single polling, source/runtime separation, and no Stage 8 regression.
