# Conformance Matrix

| Area | Active authority | Historical `d58c1c3` implementation | Stage 5.1.1 disposition |
|---|---|---|---|
| Registry terminology | Blueprint/Canonical Model name `PostgreSQL Registry`; global `Registry` equivalence unresolved | Class named `Registry` | Full name is canonical; shorthand allowed only when locally unambiguous; no global equivalence claim |
| Identity | PostgreSQL stores identity | `id` field | Category authorized; field and format remain unapproved |
| Metadata | PostgreSQL stores metadata; Stage 3.3.1 governs semantics | `media_type` only | Persist approved upstream metadata without expansion |
| Relationships | PostgreSQL stores relationships | Absent | Category authorized; representation and business semantics excluded |
| Status | PostgreSQL stores status | Absent | Category authorized; vocabulary/transitions excluded |
| File location | PostgreSQL stores file location | `storage_path`, `manifest_path` | Category authorized; historical names are evidence, not contract fields |
| Original binary | Must remain outside PostgreSQL as primary binary | No binary field | Explicitly excluded; narrow compatible evidence only |
| Register handoff | Completed Manifest disposition toward PostgreSQL Registry; readiness only | No lifecycle integration | Boundary preserved; no execution or API |
| Registry Entry | Canonical Model: unresolved | `RegistryRecord` dataclass | No canonical/domain object created; historical record is unauthorized as contract |
| PostgreSQL | Intended persistence technology | No PostgreSQL use | Named target preserved; runtime access prohibited |
| Schema | Requires later explicit authority | Absent | Not authorized |
| Persistence | Responsibility named; mechanism deferred | `save()` returns input without persistence | Mechanism not authorized; pass-through rejected as implementation |
| Transaction behavior | Requires later explicit authority | Absent | Not authorized |

The historical component neither supplies missing authority nor satisfies this
contract. Absence of implementation detail is deliberate Stage 5.1.1
conformance.
