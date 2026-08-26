# Writer Runtime PostgreSQL Transport Governance Decision

Date: 2026-08-26 (Asia/Jakarta)

## Decision proposed for Project Owner approval

The administrative control plane and application data plane are separate
contracts.

Administrative bootstrap operations remain frozen to host root invoking
`/usr/bin/docker exec -i aios-postgres /usr/local/bin/psql` against the
container-local `/var/run/postgresql` socket, database `aios`, and administrative
role `aios`.

Future host application runtime connections are frozen to:

- numeric host `127.0.0.1` with no hostname resolution or fallback;
- port `5432`;
- database `aios`;
- candidate login `aios_material_receipt_candidate_runtime`; and
- posting login `aios_material_inventory_posting_runtime`.

The application data plane must not use Docker exec, the administrative role,
an external interface, `localhost`, or the container-local Unix socket. This
decision explicitly supersedes the prior application-runtime socket assumption.

This package changes no helper, service, runtime configuration, credentials,
roles, PostgreSQL state, Docker state, firewall, or business data. It grants no
bootstrap retry or runtime activation authority.
