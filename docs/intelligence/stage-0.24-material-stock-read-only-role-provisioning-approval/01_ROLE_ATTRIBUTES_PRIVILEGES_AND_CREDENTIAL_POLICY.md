# Role Attributes, Privileges, and Credential Policy

## Exact role posture

Future controlled provisioning may create `aios_material_stock_reader` as a
dedicated login with:

- `LOGIN`;
- `NOSUPERUSER`;
- `NOCREATEDB`;
- `NOCREATEROLE`;
- `NOINHERIT`;
- `NOREPLICATION`;
- `NOBYPASSRLS`;
- no role membership and no admin option;
- no ownership of any database, schema, table, sequence, function, or procedure.

The role may receive only the minimum equivalent explicit grants:

- `CONNECT` on database `aios`;
- `USAGE` on schema `public`;
- `SELECT` on table `public.material_stock`.

It must not receive `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `REFERENCES`,
`TRIGGER`, schema/database `CREATE`, sequence privileges, function/procedure
`EXECUTE`, unrelated-table access, role management, replication, bypass-RLS,
superuser, or ownership rights.

No default privilege may be modified. Future tables must not automatically
become readable. No grant may use `WITH GRANT OPTION` or membership admin option.

## Credential policy

The login secret must be generated and provisioned out of band during the future
controlled provisioning session. It must never be committed, printed in
governance or command evidence, logged, stored in a session journal, passed to
Brain, or exposed through process output. The final connection secret belongs in
the separately governed runtime secret facility only.

Brain permanently receives neither database credentials nor connection handles.

## Search path and connection use

Retrieval SQL must reference `public.material_stock` explicitly. It must not
accept a caller-controlled schema or rely on untrusted mutable `search_path`
resolution. The dedicated identity must be used instead of the broad Registry
connection identity.

Role provisioning alone does not authorize retrieval. Every future material
stock request still requires `business_context_authorized=True` or equivalent
separately governed session authority.
