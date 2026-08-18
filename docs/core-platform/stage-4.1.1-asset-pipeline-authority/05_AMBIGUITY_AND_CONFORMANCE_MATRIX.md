# Ambiguity and Conformance Matrix

| Subject | Active authority | Historical `9d1288c` evidence | Current `main` / tests | Stage 4.1.1 disposition |
|---|---|---|---|---|
| Component position | Between Request Context and Document Manifest | Separate `core/pipeline` package | No Asset Pipeline runtime/tests | AUTHORITATIVE POSITION |
| Responsibility | Newly approved bounded orchestration/handoff | Direct storage/metadata/Manifest orchestrator | Universal Ingestion currently coordinates Stage 3 | MINIMUM BOUNDARY APPROVED; runtime move deferred |
| Initial input | Existing Request Context plus authorized upstream values | Source path and Telegram scalar arguments | Request Context and recognized values exist | HISTORICAL SIGNATURE NOT APPROVED |
| Storage sequencing | Store original before processing | Calls `save_file()` first | Accepted Stage 3 behavior/tests | MUST PRESERVE |
| Metadata | Stage 3 authority owns semantics | Calls basic extractor | Active implementation/tests | CONSUME; DO NOT REDEFINE |
| Document Manifest | Stage 3.4 authority owns semantics | Calls creator and returns path | Active runtime/schema/tests | HANDOFF/CONSUME; DO NOT REDEFINE |
| Terminal result | Bounded success/failure only | Dataclass with status and three values | Existing ingestion result is evidence | CONCEPT APPROVED; RUNTIME SHAPE UNRESOLVED |
| Pipeline states | No persistent state machine required | Six enum values, only completed returned | No current Pipeline states | NOT AUTHORIZED |
| Failure | Preserve accepted gates | Missing-file exception only | Stage 3 gates tested | ACCEPTED GATES REQUIRED; NEW POLICY UNRESOLVED |
| Duplicate | No authority | No meaningful handling/test | No Pipeline duplicate contract | NOT AUTHORIZED IN 4.1.1 |
| Multi-file | Preserve accepted Stage 3 behavior | Image-only test | Stops at aggregate storage readiness | NO REPRESENTATIVE MANIFEST INVENTION |
| URL-only | No retrieval | Not covered | No-network behavior accepted/tested | MUST PRESERVE |
| Registry | Next boundary only | Absent | Handoff readiness only | EXECUTION PROHIBITED |
| PostgreSQL | Stage 5 persistence concern | Absent | No Registry implementation | EXCLUDED |
| Package/API | Execution Plan allows current organization or approved boundary later | `core/pipeline/` candidate | Package absent | UNRESOLVED UNTIL 4.1.2/APPROVAL |
| Tests | Later contract verification | One JPEG happy path | Stage 2/3 suites active | HISTORICAL TEST INSUFFICIENT |

## Remaining Unresolved Authority

The following are intentionally unresolved and must not be guessed:

- final package/module placement and public API;
- concrete result type and field names;
- synchronous versus asynchronous execution;
- exception translation, retry, compensation, timeout, and transaction policy;
- duplicate/idempotency semantics;
- whether any implementation-local transient representation is necessary;
- concrete dependency/import list;
- any changed treatment of current multi-file behavior; and
- migration from current Universal Ingestion call ownership.

These gaps block implementation authority, not Stage 4.1.1 activation.
