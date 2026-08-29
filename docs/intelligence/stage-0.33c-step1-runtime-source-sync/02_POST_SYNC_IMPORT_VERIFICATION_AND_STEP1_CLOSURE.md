# Post-Sync Import Verification and Step 1 Closure

## Exact non-write verification

After a separately authorized synchronization, run from `/opt/aios-src` with
the existing interpreter and no bytecode generation:

```sh
cd /opt/aios-src
PYTHONDONTWRITEBYTECODE=1 /opt/aios/runtime/venv/bin/python -c '
import core.app.material_receipts.controlled_candidate_create as controlled
import core.app.material_receipts.candidate_create_authorization as authorization
import core.app.material_receipts.candidate_create_evidence as evidence
assert callable(controlled.controlled_create_review_candidate)
print(controlled.__file__)
print(authorization.__file__)
print(evidence.__file__)
'
test "$(git rev-parse HEAD)" = "964193f2e567b5109de50c427bbbf632b2198958"
test -z "$(git status --porcelain)"
```

The command proves the three Stage 0.33C modules and their direct imports resolve
from `/opt/aios-src`, the callable exists, the checkout is exactly pinned, and
the worktree is clean. It does not invoke the callable, construct a request,
read a secret, connect to PostgreSQL, or write evidence. Any generated-file,
import, commit, or cleanliness failure is a STOP.

## Post-sync service and secret checks

Separately record that `aios.service` remains active and that its PID and
`ExecMainStartTimestamp` are unchanged from the pre-sync bounded metadata. Verify
the existing EnvironmentFile mechanism and safe metadata without printing its
contents or the candidate DB password. No credential validity check is performed
in this synchronization stage.

## Step 1 closure gate

Step 1 may close only after all of the following have independent evidence:

- `/opt/aios-src` is the exact target commit and clean;
- the controlled callable and authorization/evidence dependencies import in the
  existing runtime venv without code installation or bytecode artifacts;
- runtime identity remains `aiosadmin:aiosadmin` and the governed secret
  inheritance mechanism remains intact without value exposure;
- the future one-shot caller context is viable;
- service health/PID identity is preserved, or a separate restart authority is
  approved; and
- no production PostgreSQL contact or candidate write occurred.

Until that record is independently reviewed, Step 1 remains open. Step 2 is
NOT AUTHORIZED. The next official action is separate review and execution of
this exact synchronization contract—not synchronization itself in this task.

## Safety and ownership boundary

Project Owner approval for this publication does not approve runtime mutation,
checkout synchronization, restart, filesystem provisioning, harness creation,
real input, first-write authority, or candidate execution. Those remain separate
governance decisions. Production candidate activation remains NOT AUTHORIZED.
