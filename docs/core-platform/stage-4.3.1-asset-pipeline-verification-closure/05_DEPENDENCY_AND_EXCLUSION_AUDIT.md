# Dependency and Exclusion Audit

## Allowed Runtime Imports

AST inspection at the verification baseline found only:

- `core.app.request_context`;
- `core.storage.telegram_storage`;
- `core.storage.metadata_engine`;
- `core.storage.document_manifest`;
- Telegram transport typing; and
- Python standard-library `dataclasses` and `typing`.

These match the closed dependency set in the active implementation approval.

## Prohibited Boundary Results

| Audit | Result |
|---|---|
| Storage → App imports across `core/storage/*.py` | ZERO / PASS |
| Pipeline → Registry or Registry Entry | ABSENT |
| Pipeline → PostgreSQL/ORM/migration/transaction | ABSENT |
| Pipeline → Event Engine | ABSENT |
| Pipeline → Brain/Intelligence | ABSENT |
| Pipeline → Specialist Router/Specialists | ABSENT |
| Pipeline → business domain | ABSENT |
| Pipeline → classifier/reclassification | ABSENT |
| Relevant runtime → external network client/retrieval | ABSENT |
| New cross-layer dependency | ABSENT |
| Canonical/domain Asset object | ABSENT |
| Persistent/six-state Pipeline model | ABSENT |
| Retry/recovery/duplicate implementation | ABSENT |

Registry execution remains **NONE**. PostgreSQL and production persistence are
Stage 5 concerns and are untouched by Stage 4.3.1.
