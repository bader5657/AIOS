# Stage 3.5.1 Dependency Boundary Assessment

## Git-Resolved Baseline

After `git fetch origin`, Git resolved both references as follows:

| Reference | SHA |
|---|---|
| `main` | `36a5fb77f005330b6a5a6fa734672f8601ed3d86` |
| `origin/main` | `36a5fb77f005330b6a5a6fa734672f8601ed3d86` |

The worktree was clean. The baseline contains the accepted Stage 3.4.2 closure
and its explicit result:
`STAGE 3.4.2 VERIFIED — ACCEPTED — PUBLISHED — ACTIVE — CLOSED`.

GitHub evaluation found one unrelated open PR, PR #1 from
`sprint-18-conversation-engine`, with no reported review decision or checks. It
does not target or modify this assessment baseline. No relevant unresolved PR
or check blocks this assessment. The only listed Actions run for `main` was a
completed successful Dependency Graph run on an older SHA; no current failing
or pending check was reported.

## Authority Applied

The assessment applied, in precedence and scope order:

1. `docs/AIOS_ARCHITECTURE_v1.md`;
2. `docs/AIOS_Roadmap_Frozen.md`;
3. `docs/architecture/AIOS_AUTHORITY_HIERARCHY.md`;
4. `docs/architecture/AIOS_CANONICAL_MODEL.md`;
5. `docs/architecture/AIOS_LAYER_ARCHITECTURE.md`;
6. `docs/core-platform/CORE_PLATFORM_AUTHORITY_DECISION.md`;
7. `docs/core-platform/CORE_PLATFORM_EXECUTION_PLAN_v1.md`;
8. the Stage 3.4.2 closure package; and
9. implementation, tests, and Git history as evidence only.

The Blueprint permits Ingestion to depend on App and Storage. The Active Layer
Architecture authorizes those same two directions and states that every other
dependency direction is `UNRESOLVED`. It does not authorize Storage to depend
on App. The Execution Plan identifies this exact coupling as the Stage 3.5.1
risk and requires removal or explicit approval.

## Exact Dependency Trace

```text
core.ingestion.universal_ingestion
  -> core.app.input_classifier
       -> InputType
       -> recognize_telegram_message()
       -> classify_telegram_message()
  -> core.storage.telegram_storage.save_telegram_attachment()
       -> core.app.input_classifier.InputType
       -> core.app.input_classifier.recognize_telegram_message()
       -> core.storage.file_storage.save_file(storage_class=<InputType.value>)
```

The exact source import is:

```python
from core.app.input_classifier import InputType, recognize_telegram_message
```

Symbols used by Storage:

- `InputType` is used in the public parameter annotation, attachment-selection
  branches, grouped document subtype branches, and `.value` conversion for
  `storage_class`.
- `recognize_telegram_message()` is called when `input_type` is absent.

Storage needs only enough information to select the Telegram attachment and
the existing filesystem storage class. It does not need classification
behavior as a storage responsibility.

The dependency is both enum-driven and runtime-driven. It is not type-only.
Production code exercises it: the single-file path in
`ingest_telegram_message()` calls `save_telegram_attachment(message, context)`
without `input_type`, which causes Storage to invoke the App classifier. The
multi-file path supplies `InputType` values explicitly, but still crosses the
same boundary through the function contract.

Tests exercise and encode the behavior indirectly. The ingestion capability,
universal ingestion, and lifecycle-boundary suites mock or assert storage
calls; `test_telegram_input_boundary.py` also inspects the current storage
decision tree. At the baseline, 37 focused tests passed through `unittest` with
bytecode writing disabled. `pytest` was unavailable in the environment.

## Layer-Boundary Finding

**UNAUTHORIZED / UNRESOLVED DIRECTION REQUIRING DISPOSITION.**

The current Storage -> App import is not an explicitly allowed direction in
the Active Layer Architecture. This finding does not declare a new forbidden
direction and does not expand Layer Architecture authority. It records that an
unresolved dependency may not be treated as authorized merely because current
code imports it.

## Existing Neutral Alternative

An existing neutral representation already exists in runtime contracts:

- `InputType` is a `StrEnum` whose `.value` supplies media strings;
- `core.storage.file_storage` accepts `storage_class: str`;
- `core.storage.metadata_engine` accepts `media_type: str`; and
- `core.storage.document_manifest` accepts `represented_media_type: str`.

Therefore, the existing media string value is sufficient at the Storage API
boundary. No new canonical object, shared enum, domain type, or storage-local
enum is required. The accepted Blueprint media set and existing storage path
contract remain the governing values; this assessment creates no second source
of truth.

## Option A — Remove Coupling

**Supported and preferred.** The smallest safe future refactor is to keep
recognition/classification in Ingestion/App, pass the already-recognized media
value into Storage for every file-original call, and make Storage accept that
neutral string rather than `InputType`. Storage can continue selecting the
corresponding Telegram attachment and passing the same string to `save_file`.

This removes both imported symbols and the classifier fallback without adding
a layer, module, enum, canonical concept, lifecycle step, or media type. A
storage-local enum would duplicate the accepted media vocabulary and risk
authority drift, so it is expressly not proposed.

## Option B — Explicitly Approve Narrow Coupling

**Not recommended.** A narrow exception could technically permit only
`core.storage.telegram_storage -> core.app.input_classifier.InputType` and
`recognize_telegram_message`, while prohibiting every other Storage -> App
dependency. However, the exception is unnecessary because the existing neutral
string contract supports the same behavior with a small refactor. Retaining
classification fallback in Storage also preserves behavior ownership in the
wrong boundary. Approval would add boundary authority where none is needed.

## Recommendation

**REMOVE COUPLING**

This is the smallest authority-consistent disposition, follows the Project
Owner preference, retains one classifier source of truth in App/Ingestion, and
requires no architectural invention.
