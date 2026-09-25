# AIOS P4S7-R22A Git Safe-Directory Amendment

Classification: `P4S7_R22A_GIT_SAFE_DIRECTORY_AMENDMENT_READY_FOR_REVIEW`

## Scope

Both executor Git helpers now invoke `/usr/bin/git -c
safe.directory=/opt/aios-src -C /opt/aios-src ...`. The trust exception is
process-local, literal, and limited to the governed repository. The subprocess
environment remains exactly `{"PATH": "/usr/bin:/bin"}`. No global or system
Git configuration is written and no wildcard trust is introduced.

The executor digest and the current policy table are both:

`3eec6a3b0cf0e1d9a768c15bf445876d3a463f38528a8fb4046ea27ba750ed97`

This amendment changes only the Git invocation and its executor digest binding.
Historical executor digests remain historical. PR #292 is merged history and
was not edited. Review and merge of this amendment do not create activation or
authorize an installer attempt or Step 5.

## Ownership evidence and limits

The supplied production observation is that root Git succeeds with its ordinary
environment but fails with only PATH. A direct repeat using `sudo -n` was blocked
because sudo requires a password; no actual root execution is claimed here.

Read-only checks against the exact `/opt/aios-src` repository reproduced Git's
ownership rejection with `GIT_TEST_ASSUME_DIFFERENT_OWNER=1` and the minimal PATH.
The same command with the process-local exception succeeded. Both amended
helpers passed this ownership check; an unamended subsequent process still
failed. The test-only ownership flag is injected by the test wrapper and is not
part of the executor environment. A different temporary repository remained
rejected by both helpers. Readable system, user, and repository configuration
bytes and modification times were unchanged.

The exact helper command and exact PATH-only environment are separately asserted
without the ownership-test flag. The host ownership proof skips on CI hosts
without `/opt/aios-src`; it ran successfully on this host. A live root/PATH-only
recheck remains an operational verification before any separately governed
activation action.

## Validation

- Focused preclaim, activation serialization, control, and orchestration tests:
  **176 passed, 16 subtests passed**, using
  `/home/aiosadmin/aios-test-venv/bin/python -m pytest -q` with
  `tests/unit/intelligence/test_stage033c_r13a_preclaim.py`,
  `test_stage033c_activation_serialization.py`, `test_stage033c_control.py`, and
  `test_stage033c_orchestration.py` in the same test directory.
- Full intelligence suite:
  `/tmp/aios-stage-0-31b-venv/bin/python -m pytest -q tests/unit/intelligence`:
  **290 passed, 1 skipped, 42 subtests passed**. The existing root-metadata test
  skips when run as non-root. The first test environment lacked the `psycopg`
  import dependency and stopped at collection; the existing complete environment
  resolved collection without installing dependencies or contacting PostgreSQL.
- `py_compile` and AST parsing passed for the amended executor and test module.
- `git diff --check` passed. SHA-256 was recomputed and exactly matched against
  the policy table; a regression test also enforces this equality.
- Tracked, staged, and untracked dirt still fail closed. Merge ancestry, exact
  runtime HEAD, and authority-document lineage checks remain covered.
- A real Git assume-unchanged fixture proves executor bytes are still compared
  with the HEAD blob even when status is clean.
- Failures from both text and byte Git helpers remain `PRECONDITION_FAILED`;
  preclaim failure tests assert claim/staging/publication counts of **0/0/0**.

## Operational boundary and next action

The production activation path was checked and remains absent. No activation,
claim, runtime target, candidate, or `authorization.json` was created. The
production installer and harness were not invoked. PostgreSQL was not contacted
and Step 5 was not authorized. Temporary unit-test fixtures are isolated from
production runtime paths.

Next action: independent review of this amendment, followed by human merge if
accepted. Runtime synchronization, live-root verification, and any activation
creation require their separately governed follow-up actions.
