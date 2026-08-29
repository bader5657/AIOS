# Stage 0.33B-V-FP Operator Authority and Scope

Date: 2026-08-29 (Asia/Jakarta)

## Authority basis and purpose

PR #254 was reviewed at `ef285fa6c800dbe470ac3755abf10f18eed1193a`
and merged as `9bc451f0d8f07f56048ca22b3869e290aa8854ee`.
Stage 0.33B-V read-only authority is merged but execution remains blocked until
its evidence namespace is separately provisioned and verified.

This package governs exactly one operator filesystem-provisioning operation to
establish only:

```text
/opt/aios/runtime/intelligence/production-execution-evidence/stage-0.33b-v
```

It does not create that directory during publication. It authorizes no
PostgreSQL connection or query, Stage 0.33B-V execution, Migration 0004 or 0005
execution, `DOWN`, runtime or service change, Telegram or Universal Ingestion
change, candidate creation/confirmation/posting/traffic activation, or change
to Stage 0.33B-D evidence.

## Project Owner approval and human boundary

The Project Owner approves only creation of the exact Stage V evidence root by
an authenticated human Project Owner or explicitly authorized VPS operator,
using the one exact privileged command frozen in this package. This is not
general sudo or root authority.

Codex must never request, receive, capture, log, store, or pipe a sudo password;
use `sudo -S` or `expect`; modify sudoers; create passwordless sudo; or open a
root shell. If sudo requests a password, the human enters it directly in the
VPS terminal.

The following are explicitly prohibited: `sudo bash`, `sudo sh`, `sudo su`,
`sudo -i`, `sudo python`, `sudo tee`, `sudo sed`, `sudo rm`, `sudo mv`,
`sudo cp`, `sudo find`, recursive `chmod` or `chown`, arbitrary `sudo mkdir`,
sudoers modification, and any root shell. Only the exact `/usr/bin/sudo
/usr/bin/install ... stage-0.33b-v` command in this package is approved.

## Historical evidence and authority separation

The existing root and every child beneath
`/opt/aios/runtime/intelligence/production-execution-evidence/stage-0.33b-d`
remain immutable. Provisioning must not read for content, write, chmod, chown,
delete, move, replace, or recreate Stage D evidence.

Provisioning, bounded post-provision path verification, and the single
write/fsync probe do not consume Stage 0.33B-V authority. That authority is
consumed only at the first attempt to launch the exact production Docker/psql
control plane governed by PR #254. This package neither launches nor authorizes
that process.

## Publication safety

This governance publication contacts no production PostgreSQL endpoint,
executes no production SELECT or migration, runs no sudo command, creates no
production filesystem path, executes no Stage 0.33B-V session, and changes no
Stage D evidence, `runtime.env`, service, Telegram, Universal Ingestion, or
candidate activation state.
