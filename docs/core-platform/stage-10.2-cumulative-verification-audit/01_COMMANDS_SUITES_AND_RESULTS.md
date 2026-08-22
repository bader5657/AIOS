# Commands, Suites, and Results

## Verified execution environment

- Python: system Python `3.12.3` plus accepted
  `/opt/aios/runtime/venv/lib/python3.12/site-packages`;
- application dependencies: Telegram `22.8`, psycopg `3.3.4`, and accepted
  runtime requirements; test-only system `jsonschema` `4.10.3`;
- bytecode: disabled for tests;
- compile cache: redirected to `/tmp/aios-stage-10-2-compile-cache`, audited,
  then removed;
- database: disposable `postgres:17-alpine`, database/user `aios_stage102`,
  loopback-only `127.0.0.1:55433`, no persistent volume, production DSN unset,
  removed after tests;
- expected skips, xfails, final warnings, required failures: `0`.

## Automated matrix

| Gate | Exact execution | Result |
|---|---|---|
| Full unit excluding separately discovered Domain tree | `PYTHONPATH=/opt/aios/runtime/venv/lib/python3.12/site-packages PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/unit -p 'test_*.py' -v` | `148 PASS` |
| Domain Foundation | same environment; discover `tests/unit/domain` | `212 PASS` |
| Registry/database integration | isolated test DSN; discover `tests/integration` | `27 PASS` |
| Core Platform/Stage 8 integration | isolated test DSN; discover `tests/integration/core_platform` | `57 PASS` |
| Unique cumulative total | four discovery partitions above | `444 PASS`; failed 0; skipped 0; xfailed 0; warnings 0 |
| AIOS Core focused | `python3 -m unittest discover -s tests/unit/aios_core` | `13 PASS` |
| Service/systemd focused | `python3 -m unittest tests.unit.core_platform.test_aios_systemd_service` | `8 PASS` |
| Dependency/import focused | `python3 -m unittest tests.unit.core_platform.test_stage8_import_boundaries` | `9 PASS` |
| Python compile | `PYTHONPYCACHEPREFIX=/tmp/aios-stage-10-2-compile-cache python3 -m compileall -q core tests` | PASS |
| JSON schemas | parse all `config/*.json` | `3 PASS` |
| Migration static | ordering/up/down/table/no-binary assertions | PASS |
| Migration runtime | apply/catalog/reverse/reapply test inside Registry integration | `1 PASS` |
| Runtime dependency consistency | `/opt/aios/runtime/venv/bin/python -m pip check` | PASS |
| systemd static | `systemd-analyze verify deploy/systemd/aios.service` | PASS |
| Git static | `git diff --check` | PASS |

The Stage 8 lifecycle/failure coverage is the 57-test Core Platform integration
partition plus the 9-test dependency/import audit and relevant unit suites.
It covers RequestContext, Pipeline, Storage, Metadata, Manifest, Registry,
Event, Core, ownership, ordering, suppression/preservation, and no-Brain gates.

## Diagnostic classifications

Two preliminary environment-selection runs are retained, not hidden:

1. system Python unit discovery: missing Telegram/psycopg imports plus one
   order-sensitive timestamp failure; `ENVIRONMENT_LIMITATION` because the
   interpreter lacked application dependencies;
2. runtime-venv unit discovery: missing test-only `jsonschema`;
   `ENVIRONMENT_LIMITATION`.

The verified composite environment imported the complete dependency set and
the full final unit partition passed 148/148, including the timestamp test.
Therefore neither diagnostic is a `BASELINE_DEFECT` or unresolved `TEST_DEFECT`.
