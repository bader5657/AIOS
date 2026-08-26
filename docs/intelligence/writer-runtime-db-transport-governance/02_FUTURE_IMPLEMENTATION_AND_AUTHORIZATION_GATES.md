# Future Runtime Probe Implementation and Authorization Gates

## Required helper remediation

A later repository implementation must change only the post-provision runtime
login probes to use numeric `127.0.0.1:5432/aios`. The administrative transport
must remain Docker exec over the container-local socket.

Before secret generation, the helper must fail closed unless read-only evidence
proves:

- Docker still publishes PostgreSQL exactly on `127.0.0.1:5432`;
- no wildcard or external PostgreSQL publication is accepted;
- PostgreSQL HBA has no error and the host-to-container source is governed by
  strong password authentication, specifically `scram-sha-256`;
- password encryption remains `scram-sha-256`; and
- all existing logging, collision, governed-table, and PUBLIC ACL checks pass.

The candidate and posting probes must use their own newly generated credentials,
the exact numeric host, port, database, and fixed login. If libpq/psql is used,
the sealed memfd pgpass record host is exactly `127.0.0.1`, never `localhost` or
`/var/run/postgresql`. The host currently has no `/usr/bin/psql`, so the later
implementation must select and security-review a fixed host-capable client; it
must not substitute container Docker exec because that would test a different
transport.

Passwords must be supplied as driver parameters or a sealed private descriptor,
never interpolated into logged connection URIs, argv, exceptions, or status
output. No caller may override host, port, database, login, client, or SQL.

## Separate runtime-service authority

Credential creation does not authorize credential consumption. Candidate and
posting services require later governance for separate connection pools,
transaction and statement timeouts, retry policy, URI/error redaction, and
strict credential separation.

## Mandatory sequence

1. Project Owner approves this runtime transport governance package.
2. A new repository PR remediates and tests the helper runtime probes.
3. A fresh security review verifies the exact endpoint, SCRAM posture, and
   unchanged administrative/security contracts.
4. A new one-shot production execution package is published and separately
   authorized.
5. Only that new authority may permit one production bootstrap attempt.

No step in this package authorizes a production retry.
