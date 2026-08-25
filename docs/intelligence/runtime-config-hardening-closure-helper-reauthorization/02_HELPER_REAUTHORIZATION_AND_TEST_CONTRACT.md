# Writer Secret Bootstrap Helper Reauthorization

## Blocker disposition

The prior repository helper implementation was blocked solely because the
root-mediated parent-directory security invariant was not satisfied. The
independent closure evidence proves the complete invariant now holds. That
blocker is resolved.

Upon merge of this governance package, authorize one separately scoped,
repository-only implementation task for the fixed Writer Runtime Secret
Bootstrap helper. Repository convention review must select
`scripts/admin/bootstrap_material_writer_secrets.py` or the exact conventional
equivalent. Authorized changes are limited to helper source, isolated tests,
and narrow non-secret documentation required by that implementation.

This reauthorization does not authorize production installation or execution,
root execution, credential generation, `runtime.env` modification, production
PostgreSQL provisioning, writer-role creation, privileges, runtime-service
activation, Telegram changes, or business-data population. Those actions need
separate authority after review of the exact helper artifact.

## Frozen implementation contract

The helper must fail closed unless the following exact objects and metadata
hold:

- `/opt/aios` is `root:aiosadmin 0755`;
- `/opt/aios/runtime` is `root:aiosadmin 0755`;
- `/opt/aios/runtime/config` is `root:aiosadmin 0750`;
- `/opt/aios/runtime/config/runtime.env` is a regular, non-symlink file with
  `root:aiosadmin 0640`.

The only governed keys remain
`AIOS_MATERIAL_RECEIPT_CANDIDATE_DB_PASSWORD` and
`AIOS_MATERIAL_INVENTORY_POSTING_DB_PASSWORD`. The implementation must preserve
all requirements frozen by the Writer Runtime Secret Bootstrap Governance:
one later manually authenticated sudo execution; no persistent sudoers or
`NOPASSWD`; two distinct secrets generated independently from at least 32 CSPRNG
bytes; no secret output, logging, hashing, or transcript exposure; fixed paths,
keys, roles, and targets; locking; secure same-directory temporary files;
atomic replacement and parent-directory `fsync`; byte preservation of unrelated
environment lines; duplicate-key rejection; no persistent plaintext backup;
private password delivery with no password-bearing SQL in argv; server logging
preflight; one DB transaction for roles and grants; restoration on DB failure;
post-commit authentication-failure compensation using `NOLOGIN` plus secret-file
restoration; complete cleanup; and no business-row mutation.

## Required isolated tests

The repository implementation must test:

- parent-chain metadata validation and failure when `config` is writable by
  non-root;
- target metadata validation plus symlink and wrong-file-type rejection;
- unrelated environment preservation and duplicate-key rejection;
- atomic replacement, secure temporary-file permissions, and locking;
- secret non-output and fixed role/key/path behavior;
- private PostgreSQL delivery construction;
- DB failure recovery and authentication-failure compensation;
- cleanup on success and failure.

Tests must use isolated non-production fixtures and doubles. They must not use
production secrets or a production database.
