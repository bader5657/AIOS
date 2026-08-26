# Execution Gates, Recovery, and Approval

## Mandatory preflight and single execution

Immediately before the one authorized command, the operator must manually
authenticate sudo and verify, without displaying secret values:

1. `HEAD`, local `main`, and `origin/main` equal
   `4fc068532f197d399600229d73d5e570bee6bd74` and the worktree is clean;
2. a fresh mechanical SHA-256 of
   `scripts/admin/bootstrap_material_writer_secrets.py` equals
   `83e2723acf9efd5f56325cc3beb96c4354a5b124e5196d914681b0b13d4d5384`;
3. every filesystem invariant in this package passes exactly;
4. PostgreSQL is reached only at `/var/run/postgresql:5432/aios`;
5. all four frozen identities are absent;
6. all four governed relations exist and have no PUBLIC table or column ACL;
7. statement logging, duration/error logging, sampling, preload hooks, pgaudit,
   and auto_explain posture satisfy the helper's fail-closed logging gate;
8. no concurrent bootstrap holds the fixed lock.

Any mismatch stops execution and returns to governance. The authority permits
one invocation only; a failed or interrupted run is not authority to retry.

## Secret and transaction boundary

The helper generates exactly two unequal secrets from independent 32-byte
CSPRNG inputs. They are unpadded Base64URL values and may exist only in process
memory, the governed `runtime.env`, password-bearing SQL on protected stdin,
and sealed anonymous memfd pgpass descriptors passed to the intended auth
child. Values, hashes, SQL bodies, and pgpass records must not enter output,
logs, argv, governance evidence, or persistent temporary artifacts.

Environment replacement occurs durably before database provisioning. Role
creation, attributes, memberships, grants, and exact precommit validation occur
inside one `ON_ERROR_STOP` transaction. Authentication probes use the matching
generated credential, the exact Unix socket, and read-only queries.

## Failure and recovery

A client failure leaves database outcome UNKNOWN until read-only reconciliation
proves all four identities absent, proves a complete valid committed state, or
detects partial/unexpected state. The old environment must not be restored while
usable matching LOGIN identities may remain.

If post-commit authentication fails, a separate transaction must set both
runtime identities NOLOGIN, verify exactly those two rows and
`rolcanlogin=false`, and commit before restoring the original environment.
Compensation failure is a high-severity stop: retain the staged environment and
return to governance without claiming safe recovery.

SIGINT and SIGTERM are handled through fail-closed checkpoints. SIGKILL, power
loss, and concurrent mutation by root remain residual risks; after either event,
do not rerun. Preserve state and obtain a new reconciliation authorization.

## Evidence and approval activation

Permitted evidence contains only commit/hash/path, metadata, key names and
presence counts, role names/attributes, ACL/membership/ownership assertions,
authentication outcomes, compensation outcome if applicable, and timestamps.
It contains no credential, password hash, SQL password statement, or pgpass
record.

This package becomes eligible for use only after its documentation PR is
reviewed and merged and the Project Owner explicitly approves one manually
authenticated sudo execution. Until both events occur, production execution
authority remains NONE.
