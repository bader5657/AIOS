# Stage 4.1.1 Conformance Matrix

| Historical behavior | Classification | Evidence and consequence |
|---|---|---|
| Separate Asset Pipeline component shell | ADAPTABLE | Component is required, but package/API placement is not approved by history |
| Coordinates storage → metadata → Manifest | CONFORMS | Same ordering is active; semantic ownership must remain external |
| Directly delegates to existing capability modules | ADAPTABLE | Direction is permitted, but modern APIs and closed imports require later approval |
| Source-existence guard | ADAPTABLE | Local precondition may be useful; not a complete validation/failure contract |
| `source_path` plus Telegram scalar API | CONFLICTS | Does not accept active Request Context or upstream recognized facts |
| Free `media_type` string from caller | CONFLICTS | Does not prove upstream recognition preservation or ten-input validity |
| Historical `AssetPipelineResult` | ADAPTABLE | Non-canonical result concept is usable; enum and exact fields are not |
| Six-value persistent-looking enum | NOT AUTHORIZED | Stage 4.1.1 explicitly authorizes no persistent state machine |
| Always returns `COMPLETED` on success | ADAPTABLE | Must become minimum bounded success/failure disposition without speculative states |
| No failure result | MISSING | Active failure contract requires deterministic non-success disposition |
| Image-root storage for every source | CONFLICTS | Violates active media-class storage paths and Stage 3 semantics |
| Historical metadata call/signature | CONFLICTS | Current Stage 3 metadata contract requires recognized type and variant facts |
| Historical Manifest call/signature/model | CONFLICTS | Current Document Manifest authority/schema uses different fields and semantics |
| Store → Metadata → Manifest order | CONFORMS | Strongest reusable conceptual behavior |
| No Request Context use | MISSING | Official input boundary requires active Request Context |
| No Text/URL-only handling | MISSING | Active ten-input contracts include them; URL-only must not fetch |
| No multi-file behavior | MISSING | Accepted aggregate storage behavior must be preserved |
| No retry/recovery/transaction | CONFORMS | Those semantics remain unauthorized, so absence is correct |
| No duplicate handling | CONFORMS | Duplicate semantics are not authorized in Stage 4.1.1 |
| No Registry/PostgreSQL | CONFORMS | Both remain excluded |
| No network behavior | CONFORMS | Required for URL-only preservation |
| No production integration | MISSING | Stage 4 later requires integration; history proves none |
| One JPEG test | ADAPTABLE | Scenario can guide a new test but is insufficient and asserts obsolete details |
| Empty package markers | IRRELEVANT | Mechanical packaging evidence only |

## Overall Conformance

The orchestration idea and ordering conform. Most executable contract surface
does not: input API, result status, storage assumptions, metadata call,
Manifest call, capability coverage, failure representation, and integration
must all be replaced or newly defined under later approval.
