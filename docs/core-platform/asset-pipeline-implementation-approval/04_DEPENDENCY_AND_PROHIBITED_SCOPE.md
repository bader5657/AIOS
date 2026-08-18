# Dependency and Prohibited Scope

## Allowed Dependencies

The new Pipeline may import only the existing capabilities needed by its active
contract:

- active `RequestContext` type for input-boundary validation/typing;
- current Telegram Storage handoff used by Universal Ingestion;
- current Metadata Engine entrypoint; and
- current Document Manifest entrypoint.

Universal Ingestion may import the new Pipeline runtime. Same-layer integration
and the existing Ingestion → App/Storage permissions create no new general
dependency direction. No dependency package may be added.

## Prohibited Dependencies

- Pipeline → Registry or Registry Entry;
- Pipeline → PostgreSQL, ORM, migration, database connection, or transaction;
- Pipeline → Event Engine, downstream AIOS Core behavior, Brain, Intelligence,
  Specialist Router, Specialist, or business domain;
- Pipeline → classifier or recognition behavior that causes reclassification;
- Storage → App or a disguised replacement alias/shared module;
- any new cross-layer direction; and
- any external network client or retrieval capability.

## Prohibited Historical Elements

- checkout, restoration, copy, or cherry-pick of commit `9d1288c` runtime;
- historical `core/pipeline/state.py`;
- `AssetPipelineStatus` or equivalent six-state model;
- historical Telegram-scalar `process()` signature;
- historical `AssetPipelineResult.status` semantics;
- image-root storage for every media type;
- obsolete Metadata or Manifest call signatures;
- unconditional `COMPLETED`; and
- historical test restoration as sufficient coverage.

No canonical `Asset`, `Original Asset`, `Pipeline Asset`, aggregate, entity, or
value object may be introduced.
