# Production Preflight, Transaction, Recovery, and Credentials

## Mandatory preflight

Before any role creation, require clean approved main, the established healthy
production identity, recorded restart count, exact contracts for
`material_stock`, `material_receipts`, `material_receipt_items`, and
`inventory_movements`, receipt/item/movement counts `0 / 0 / 0`, ownership and
ACL baselines, and an unchanged `aios_material_stock_reader`.

All four planned identifiers must be absent. Any collision stops the session;
there is no automatic reuse, alteration, rename, drop, or membership change.

Reinspect effective PUBLIC access. Environmental database `CONNECT`/`TEMP`,
schema `USAGE`, and ordinary built-in routine defaults may remain. Unexpected
PUBLIC privilege on a governed table that defeats isolation stops provisioning;
the session must not revoke it automatically. Do not alter default privileges.

## Credential boundary

The two LOGIN identities receive independent strong random secrets. Before DB
mutation, prove the governed runtime secret facility can accept and protect two
pending secret versions. Generate secrets in process, never print or echo them,
and store only pending versions in that facility. Secrets never enter Git,
Markdown, command evidence, logs, Telegram, Brain, or session journals.

If pending secure storage cannot be guaranteed, stop before LOGIN creation.

## Transaction and fail-closed recovery

PostgreSQL role creation, password assignment, grants, and membership changes
are performed in one explicit transaction. Inside it:

1. create both NOLOGIN privilege roles;
2. create both LOGIN identities with their independently staged secrets;
3. apply exact database, schema, table, and column grants;
4. grant the two exact one-to-one memberships;
5. verify catalogs, attributes, ownership absence, memberships, and effective
   privileges using the transaction-visible state;
6. commit only if every database assertion passes.

Any pre-commit failure rolls back all PostgreSQL changes. Pending secret
versions are then invalidated/deleted through the secret facility; the session
is not successful.

External authentication cannot validate an uncommitted PostgreSQL LOGIN.
Therefore bounded authentication probes follow commit, before pending secrets
are activated for any application. If either probe or postflight fails, declare
provisioning incomplete, keep application activation prohibited, and execute
the pre-approved fail-closed compensation: in a new bounded transaction set
both runtime identities to `NOLOGIN`. Preserve privilege roles and evidence for
governance review; do not drop or redesign objects automatically. Invalidate
pending secrets. No partial setup may be declared operational.

This recovery permission exists only to disable both new LOGIN identities after
a failed post-commit probe/postflight. It is not a retry or general role-change
authority.
