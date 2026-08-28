# Stage 0.33B-FP Exact Provisioning Commands and Path Contract

## Preconditions and binary identity

After this governance package receives independent PASS and is merged unchanged,
the human operator must first verify without following symlinks that
`/opt/aios/runtime/intelligence` is a real directory, not a symlink, owned by
`root:root`, mode `0755`. The exact `/usr/bin/sudo` and `/usr/bin/install` binaries
must exist and be used. An alias, shell function, alternate binary, Python
script, Docker container, or manually reconstructed operation is prohibited.

Any mismatch requires STOP. Do not repair it automatically.

## Exact approved privileged commands

Command A is authorized if and only if
`/opt/aios/runtime/intelligence/production-execution-evidence` is ABSENT:

```text
/usr/bin/sudo /usr/bin/install \
  -d \
  -o root \
  -g root \
  -m 0755 \
  /opt/aios/runtime/intelligence/production-execution-evidence
```

Command B is authorized if and only if
`/opt/aios/runtime/intelligence/production-execution-evidence/stage-0.33b-d` is
ABSENT:

```text
/usr/bin/sudo /usr/bin/install \
  -d \
  -o aiosadmin \
  -g aiosadmin \
  -m 0750 \
  /opt/aios/runtime/intelligence/production-execution-evidence/stage-0.33b-d
```

No other privileged command is approved. Codex must not execute either command.
The authenticated operator manually enters a sudo password in the local VPS
terminal if prompted; the password must never enter AIOS, Codex, ChatGPT, Git,
logs, or evidence.

## Existing-path policy

Inspect every governed path without following symlinks before execution:

- Required existing parent: real non-symlink directory, `root:root`, `0755`.
- Intermediate parent: if absent, Command A may create it. If present and a real
  non-symlink `root:root` directory with mode `0755`, do nothing. Otherwise STOP.
- Stage root: if absent, Command B may create it. If present and a real
  non-symlink `aiosadmin:aiosadmin` directory with mode `0750`, do nothing.
  Otherwise STOP.

Do not recreate an exact existing path. Do not automatically `chmod`, `chown`,
delete, move, overwrite, replace, or traverse a symlink. A partially successful
provisioning operation does not authorize repair or additional privileged work;
return to governance.

## Frozen resulting tree

```text
/opt/aios/runtime/intelligence
  real directory; root:root; 0755
└── production-execution-evidence
    real directory; root:root; 0755
    └── stage-0.33b-d
        real directory; aiosadmin:aiosadmin; 0750
```

If the root is successfully established but any later pre-launch gate fails, do
not delete it, revert ownership, or retry production. It remains governed AIOS
infrastructure. Migration authority remains UNCONSUMED because no production
control-plane launch occurred. A later separately authorized execution may reuse
the validated root but must create a new unique evidence session.
