# Runtime Transport Security Evidence and Alternatives

## Verified production evidence

- `/etc/systemd/system/aios.service` runs directly on the host as
  `aiosadmin:aiosadmin` and reads the governed runtime environment file.
- `aios-postgres` is running from `postgres:17-alpine` on `aios-net`.
- Docker publishes `5432/tcp` exactly as `127.0.0.1:5432`; `ss` reports no
  wildcard or external PostgreSQL listener.
- The existing application DSN resolves to numeric `127.0.0.1`, port `5432`,
  database `aios`, with username and password present; no values were disclosed.
- PostgreSQL sees an actual host-loopback application connection as Docker
  gateway source `172.16.2.1/32`. It therefore matches the general host rule
  using `scram-sha-256`, not the container-internal `127.0.0.1 trust` rule.
- `password_encryption` is `scram-sha-256`; server TLS is currently off.

The loopback-only bind itself prevents external routing to PostgreSQL regardless
of host firewall policy. A privileged firewall ruleset dump was unavailable to
the reviewing account, but both Docker binding metadata and the kernel listener
table independently show no non-loopback PostgreSQL exposure.

TLS is not required for this same-host, numeric-loopback contract. SCRAM avoids
transmitting a plaintext password. Any future non-loopback bind, remote client,
or cross-host transport invalidates this decision and requires a new TLS and
network governance review.

## Alternatives

A. Host loopback is approved as the preferred architecture: it is already
reachable by the host service, externally unexposed, independent of Docker
control privileges, and compatible with dedicated LOGIN roles.

B. Moving `aios.service` into Docker is rejected for this bootstrap scope; it is
an unnecessary service-topology migration.

C. Exporting or mounting the PostgreSQL socket into the host is rejected; it
adds filesystem coupling and exists only to preserve an obsolete assumption.

D. Docker exec for application queries is rejected. It would give the data plane
Docker control capability and would not exercise the service's real transport.

`aios_material_stock_reader` is currently a non-superuser LOGIN role. Whether it
later adopts this same endpoint is a separate decision; this package makes no
change to that identity or its consumer.
