# Execution Gates, Recovery, and Approval

## Mandatory preflight and single execution

Immediately before the one authorized command, the operator must manually
authenticate sudo and verify, without displaying secret values:

1. `HEAD`, local `main`, and `origin/main` are identical at the merged
   governance commit, the worktree is clean, and history contains helper merge
   commit `4fc068532f197d399600229d73d5e570bee6bd74`;
2. a fresh mechanical SHA-256 of
   `scripts/admin/bootstrap_material_writer_secrets.py` equals
   `83e2723acf9efd5f56325cc3beb96c4354a5b124e5196d914681b0b13d4d5384`;
3. every filesystem invariant in this package passes exactly;
4. PostgreSQL is reached only at `/var/run/postgresql:5432/aios`;
5. capture a SHA-256 baseline of `/opt/aios/runtime/config/runtime.env`
   without displaying any file content;
6. `aios.service` is active and its restart count is recorded;
7. PostgreSQL is healthy and its version and server identity are confirmed;
8. `public.material_stock`, `public.material_receipts`,
   `public.material_receipt_items`, and `public.inventory_movements` exist;
9. row counts for receipts, items, and movements are exactly `0/0/0`;
10. capture a deterministic non-secret fingerprint of `material_stock`;
11. all four frozen writer identities are absent;
12. all governed relations have no PUBLIC table or column ACL;
13. statement logging, duration/error logging, sampling, preload hooks, pgaudit,
    and auto_explain posture satisfy the helper's fail-closed logging gate;
14. `aios_material_stock_reader`, its attributes, memberships, ACLs, and
    effective privileges exactly match the pre-approved baseline and it has no
    writer membership;
15. no concurrent bootstrap holds the fixed lock.

Any mismatch stops execution and returns to governance. The authority permits
one invocation only; a failed or interrupted run is not authority to retry.

Authority remains unconsumed after a failed invocation only when evidence proves
the failure occurred before secret generation, environment replacement, and any
database mutation. Once sensitive mutation begins, the authority is consumed.
No automatic or uncontrolled retry is authorized.

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

If provisioning fails before commit, the PostgreSQL transaction must roll back,
the original environment must be restored, and temporary secret artifacts must
be removed. Roles must not be automatically dropped in any recovery path.

SIGINT and SIGTERM are handled through fail-closed checkpoints. SIGKILL, power
loss, and concurrent mutation by root remain residual risks; after either event,
do not rerun. Preserve state and obtain a new reconciliation authorization.

## Evidence and approval activation

Permitted evidence contains only commit/hash/path, metadata, key names and
presence counts, role names/attributes, ACL/membership/ownership assertions,
authentication outcomes, compensation outcome if applicable, and timestamps.
It contains no credential, password hash, SQL password statement, or pgpass
record.

After helper success, independent non-secret verification must prove:

- `runtime.env` remains a regular single-link `root:aiosadmin` file at mode
  `0640`, unrelated bytes match the baseline, and exactly both governed keys are
  structurally present without exposing values;
- all four exact identities, attributes, one-to-one memberships, direct and
  inherited ACL matrices, grant-option absence, and zero ownership pass;
- both runtime identities authenticate using their matching credentials over
  the Unix socket and complete read-only probes;
- receipt, item, and movement counts remain `0/0/0`, the `material_stock`
  fingerprint is unchanged, and `aios_material_stock_reader` is unchanged;
- PostgreSQL and `aios.service` remain healthy and no unnecessary service
  restart occurred.

## Project Owner approval record

I approve exactly one manually authenticated production execution of the
reviewed Writer Secret Bootstrap helper.

The execution may atomically persist the two governed runtime database
credentials and provision exactly the frozen candidate/posting PostgreSQL
identities and privileges.

No credential may be exposed to ChatGPT, Codex, terminal output, logs, Git,
Telegram, or governance evidence.

No runtime service activation, Telegram integration, business data population,
or stock posting is authorized.

Sudo authentication must occur normally in an interactive operator terminal.
The sudo password must not be captured, requested by ChatGPT/Codex, automated,
or bypassed with `sudo -n`, NOPASSWD, or sudoers modification.

This package becomes eligible for use only after its documentation PR is
reviewed and merged and the Project Owner explicitly approves one manually
authenticated sudo execution. Until both events occur, production execution
authority remains NONE.
