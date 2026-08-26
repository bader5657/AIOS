# Writer Bootstrap Container Transport Decision

Date: 2026-08-26 (Asia/Jakarta)

## Administrative control plane

The bootstrap helper freezes `/usr/bin/docker`, container `aios-postgres`, image
contract `postgres:17-alpine`, container client `/usr/local/bin/psql`, database
`aios`, role `aios`, port `5432`, and the container-local Unix socket directory
`/var/run/postgresql`. SQL is supplied only on stdin. The helper neither invokes
a shell nor exposes caller-selectable Docker, container, role, database, or SQL
targets.

Before secret generation, the helper verifies the exact container name, running
state and image contract, then verifies PostgreSQL 17, the active database and
session identities, required `LOGIN`, `SUPERUSER`, and `CREATEROLE` attributes,
the socket directory, and the effective local `trust` HBA rule without reading
container environment values. Logging, collision, and ACL preflights use this
same control-plane transport.

## Runtime data plane

The production `aios.service` is a host systemd service, while PostgreSQL is a
container with a loopback-only `127.0.0.1:5432` host publication. Therefore the
legacy runtime-login probe contract using host `/usr/bin/psql` and the
container-only `/var/run/postgresql` socket is not compatible with the deployed
runtime topology. This remediation deliberately leaves that frozen probe
unchanged and gives its socket a separate `RUNTIME_PG_SOCKET` name.

Changing runtime login authentication to loopback TCP, a container network, or
another client implementation requires a separate governance decision. No new
production execution authority is created by this repository change.
