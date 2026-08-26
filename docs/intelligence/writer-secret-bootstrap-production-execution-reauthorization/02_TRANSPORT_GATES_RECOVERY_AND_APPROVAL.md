# Frozen Transports, Execution Gates, Recovery, and Approval

## Administrative control plane

All administrative PostgreSQL operations are frozen to:

host root helper -> `/usr/bin/docker exec -i` -> fixed container
`aios-postgres` -> `/usr/local/bin/psql` -> container-local Unix socket -> role
`aios` -> database `aios`.

This plane alone performs identity and capability checks, logging preflight,
HBA and password-encryption inspection, collision and PUBLIC ACL validation,
provisioning, privilege validation, database-state reconciliation, and NOLOGIN
compensation. There is no nested sudo, host Linux `postgres` dependency,
fallback admin role, caller-selected container/database/role/SQL, generic shell,
or mutable Docker operation.

The helper must freshly prove that role `aios` exists, can LOGIN, is superuser,
and has CREATEDB and CREATEROLE before sensitive mutation. It must not broaden
that role or substitute another identity.

## Application runtime probe plane

Runtime authentication probes are frozen independently to numeric host
`127.0.0.1`, port `5432`, database `aios`, `sslmode=disable`, and the exact
candidate or posting runtime identity. They may execute only the fixed read-only
probe. They must not use Docker exec, the admin role, `localhost`, a Unix socket,
an external host, environment target override, or fallback.

The sealed memfd pgpass record must bind to `127.0.0.1:5432:aios` and the exact
runtime identity. The password is prohibited from argv, URI, output, logs,
tracebacks, governance evidence, or persistent files.

## Mandatory transport and security gates

Before secret generation, and again under the exclusive lock before mutation,
the helper must prove read-only that:

1. the fixed container identity and PostgreSQL 17 topology are valid and the
   container is running;
2. authoritative `NetworkSettings.Ports["5432/tcp"]` contains exactly one
   effective `127.0.0.1:5432` mapping;
3. secondary `HostConfig.PortBindings` exactly agrees, with no absent, wildcard,
   IPv6, external, alternate-port, multiple, or ambiguous publication;
4. exactly one dynamically derived Docker network gateway is IPv4 and within
   RFC1918 `10.0.0.0/8`, `172.16.0.0/12`, or `192.168.0.0/16`;
5. the first effective ordered HBA rule for each runtime identity, database
   `aios`, that gateway source, and the explicit non-TLS path is exactly
   `scram-sha-256`; `local` and `hostssl` are inapplicable, while `host` and
   `hostnossl` follow PostgreSQL first-match semantics;
6. `password_encryption` is exactly `scram-sha-256`;
7. logging posture, four-role collision absence, governed-table existence,
   PUBLIC ACL rejection, and all filesystem gates pass.

Malformed, undecodable, missing, multiple, unsupported, or ambiguous evidence
is a sanitized fail-closed result. The helper changes no Docker, network, HBA,
logging, or PostgreSQL server configuration.

## One-shot lifecycle

Immediately before an activated invocation, the operator must prove the
repository commit and helper SHA frozen in this package mechanically, a clean
`HEAD == main == origin/main`, all filesystem invariants, the original
`runtime.env` SHA without displaying contents, PostgreSQL/service health, the
four governed tables, receipt/item/movement counts `0/0/0`, an unchanged
non-secret `material_stock` fingerprint, all four identities absent, PUBLIC ACL
absence, unchanged stock-reader security state, and lock availability.

Only after all preflight and under-lock revalidation gates pass may the helper
generate two unequal secrets from independent 32-byte CSPRNG inputs, atomically
replace the environment, and provision roles. Role creation, attributes,
memberships, grants, and exact precommit validation remain one
`ON_ERROR_STOP` administrative transaction.

After commit and before either runtime authentication child starts, the helper
must revalidate the effective mapping, gateway, HBA first match, SCRAM and
password-encryption posture, and exact runtime endpoint. Drift or parser failure
must skip authentication and enter committed-state compensation.

## Failure, reconciliation, and compensation

Any ambiguous administrative client outcome remains UNKNOWN until authoritative
catalog reconciliation over the admin plane proves all four identities absent,
a complete valid committed state, or partial/unexpected state. Client failure
must never be treated as proof of rollback.

For post-commit transport drift or either runtime authentication failure, the
admin plane must transactionally set both runtime identities NOLOGIN, verify
exactly two expected identities with `rolcanlogin=false`, and COMMIT before the
original environment is restored. Compensation failure is a high-severity stop:
retain the current environment and do not claim safe recovery. Roles are never
automatically dropped.

No automatic retry is permitted. SIGKILL, power loss, or root-level concurrent
mutation requires state preservation and new reconciliation governance.

## Project Owner activation record

I approve separation between the PostgreSQL administrative control plane and
the application runtime data plane and, only after this package's PR is reviewed
and merged, approve exactly one manually authenticated production invocation of
the frozen helper artifact.

The invocation may persist exactly two governed writer secrets and create only
the four frozen identities and privilege matrices. It may not activate services,
populate data, post stock, alter networking/HBA/Docker, or change Telegram.

The sudo password must be entered normally by the human operator and must never
be requested, captured, automated, or bypassed by Codex, ChatGPT, `sudo -n`,
NOPASSWD, or sudoers changes.

This text is a proposed activation record, not a recorded approval. Until the
documentation PR is merged and the Project Owner separately and explicitly
activates one invocation, production execution authority remains NONE.
