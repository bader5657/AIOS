# Stage 10.2.1 Cumulative Verification Matrix

Stage 10.2.1 must run against the frozen baseline after Stage 10.1.1 and
10.1.2 complete. The execution report must record SHA, environment, command or
review method, start/end time, result, skips, findings, and artifact cleanup.

| Gate | Required coverage |
|---|---|
| Baseline integrity | `HEAD == main == origin/main` at the evidence baseline, clean tracked/untracked state before and after controlled generated-artifact cleanup |
| Full unit suite | All `tests/unit/`, including Domain Foundation, Core Platform, Event Engine, Registry, Asset Pipeline, and AIOS Core |
| Full integration suite | All `tests/integration/`, including official lifecycle and component handoffs |
| Schema/migration | JSON schemas plus Registry schema/migration creation and regression behavior |
| Database | Registry CRUD, transaction/isolation, failures, migrations, and integrations using fresh disposable non-production schemas only |
| Dependencies/imports | Installed dependency consistency, import graph/direction, cycles, optional dependency boundaries, and prohibited reverse edges |
| Stage 8 lifecycle | Official pipeline ownership/order and Respond-boundary regressions |
| Stage 8 failure | Storage, metadata, manifest, registry, dispatch/Event, Core-boundary failure and preservation regressions |
| Core boundary | Stateless/deterministic routing, accepted input/result contracts, and Brain/Memory/Specialist/business separation |
| Domain Foundation | Entire accepted Domain Foundation regression suite |
| Service/systemd | Tracked `deploy/systemd/aios.service` contract, entrypoint, working directory, user/environment, restart/single-poller policy, and static service tests |
| Operational | Accepted Stage 9 evidence reuse plus only the bounded read-only current checks defined in `05_PRODUCTION_VERIFICATION_BOUNDARY.md` |
| Compile/static | Compile all tracked Python source/tests; syntax/static checks required by accepted closures; `git diff --check` |
| Prohibited source | No later-phase imports/capabilities, embedded secrets, runtime paths/data, or unauthorized coupling |
| Generated artifacts | No tracked/uncontrolled caches, archives, temp/test/runtime residue, backups, dumps, or build output |
| Documentation claims | README and CHANGELOG agree with Stage 9.3.1 capability boundary and `VERSION` |

Commands must be derived from the repository's accepted root-test command and
closure records at execution time; the report must spell out the exact final
commands. Database checks require `AIOS_REGISTRY_TEST_DATABASE_URL` pointed at
an isolated, disposable non-production database/schema. Production data is
never test input.

## Result taxonomy

- `PASS`: the required check executed and satisfied its contract, or accepted
  immutable evidence was explicitly reused with validity proven.
- `EXPECTED_SKIP`: an authority-backed environmental/optional condition made
  the test inapplicable, with reason and authority recorded. A required check
  cannot become an expected skip merely because a dependency is unavailable.
- `FAIL`: assertion failure, error, unexpected skip, missing required
  environment, evidence mismatch, baseline drift, or required check not run.

No required failure may be reclassified as `EXPECTED_SKIP` without separate
authority. Any required `FAIL` makes Stage 10.2.1 fail and blocks 10.3.1.
