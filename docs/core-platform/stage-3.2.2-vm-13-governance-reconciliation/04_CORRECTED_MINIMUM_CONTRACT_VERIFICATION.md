# Stage 3.2.2 VM-13 Corrected Minimum Contract Verification

| Control | Value |
|---|---|
| Lifecycle | **PUBLISHED AND ACTIVE** |
| Official interpreter | Repository execution environment `python3` |
| Official runner | Python standard-library `unittest` |
| Third-party dependency | **PROHIBITED** |

The normative correction is applied to
`../stage-3.2.2-authority-extension-package/05_MINIMUM_CONTRACT_VERIFICATION.md`.
It is substantive only after this reconciliation becomes Active.

| Gate | Exact command |
|---|---|
| Syntax compilation | `PYTHONDONTWRITEBYTECODE=1 python3 -c "from pathlib import Path; [compile(Path(p).read_text(encoding='utf-8'), p, 'exec') for p in ('core/storage/telegram_storage.py', 'core/ingestion/universal_ingestion.py')]"` |
| Targeted Stage 3.2.2 | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests/unit/core_platform/test_ingestion_lifecycle_boundaries.py tests/unit/core_platform/test_ingestion_capability_matrix.py tests/unit/core_platform/test_universal_ingestion.py tests/unit/core_platform/test_storage_path_contract.py` |
| Core Platform | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/unit/core_platform -p 'test_*.py' -v` |
| Full repository/domain | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/unit/core_platform -p 'test_*.py' -v && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/unit/domain -p 'test_*.py' -v` |
| Diff integrity | `git diff --check` |
| Scope evidence | `git diff --name-only` |

Full regression uses two explicit roots because higher-root discovery would not
reliably enter the non-package Domain directory. Both invocations must discover
tests and exit zero. Evidence and failure behavior are normative as stated in
the corrected `05_MINIMUM_CONTRACT_VERIFICATION.md`.

## Post-Activation Execution Evidence

| Evidence | Result |
|---|---|
| Activation baseline | `2fb7653` |
| Interpreter | Python 3.12.3 via `python3` |
| Syntax compilation | PASS — exit 0 |
| Targeted Stage 3.2.2 | PASS — 22 run, 0 failures, 0 errors, 0 skipped |
| Core Platform | PASS — 43 run, 0 failures, 0 errors, 0 skipped |
| Full repository/domain | PASS — 43 Core Platform + 212 Domain; 255 total; 0 failures, 0 errors, 0 skipped |
| `git diff --check` | PASS — exit 0, no output |
| Working-tree changed-file scope | PASS — exact two approved source and three approved test files |
| Governance lifecycle diff | PASS — corrected original `05` plus this package only |
| Dependency installation | NONE |

All commands were executed from repository root after activation. No test,
source, dependency, runtime data, or environment configuration was changed by
verification.
