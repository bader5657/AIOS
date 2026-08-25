# PostgreSQL Delivery, Ordering, and Fail-Closed Recovery

## Password delivery

The same root process that generated and persisted the values supplies them to
the fixed PostgreSQL provisioning session from process memory through a private
anonymous stdin/pipe. Passwords must not occur in argv, environment inherited by
unrelated processes, repository SQL, temporary SQL files, shell history, or
output. The PostgreSQL client uses fixed non-secret connection arguments,
`ON_ERROR_STOP`, tuple/output suppression, and no command echo.

Password-bearing `CREATE ROLE`/`ALTER ROLE` statements are delivered only in the
protected local session. Before execution, verify the server logging posture and
disable statement/duration logging for that privileged session where supported;
PostgreSQL password-command redaction remains required. Abort if an audit/logging
layer would record password statement bodies. Never report or hash passwords.

## Fail-closed ordering

1. verify source, production identity/health, exact schema, empty tables, reader,
   and absence of all planned identities;
2. verify PUBLIC/ACL/ownership/default-ACL baselines and root execution path;
3. lock and validate `runtime.env`;
4. generate secrets and atomically persist the two keys;
5. verify key presence/uniqueness plus owner/group/mode without values;
6. begin one PostgreSQL transaction;
7. create the two privilege roles and two matching LOGIN identities;
8. apply exact grants and one-to-one memberships frozen by PR #216;
9. validate attributes, ACLs, memberships, ownership absence, and effective
   privilege matrices;
10. commit only if every transaction-visible assertion passes;
11. perform bounded authentication and read-only probes;
12. finalize success, clear transient state, and remove the helper.

If file persistence fails, no DB mutation begins. If DB work fails before
commit, roll back PostgreSQL and atomically restore the original `runtime.env`.
If DB commit succeeds but either authentication/postflight fails, immediately
set both runtime identities `NOLOGIN` in the already-approved compensation
transaction, restore/remove the newly added keys atomically, remove transient
artifacts, stop, and return to governance. Do not broaden grants or retry.

This design keeps secret persistence before usable LOGIN commit while keeping
the same secret values in one root process. DB role creation is therefore part
of the same one-time bootstrap session, not an independent credential-transfer
process.
