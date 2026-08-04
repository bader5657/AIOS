# AIOS Canonical Model

| Field | Value |
|---|---|
| Document | `AIOS_CANONICAL_MODEL.md` |
| Status | **ACTIVE** |
| Document class | Vocabulary Authority |
| Approval authority | Project Owner |
| Effective authority | Current vocabulary authority for the declared scope |

## Purpose

Define canonical names, authority-supported meanings, and the limited recognition boundaries explicitly established by the Blueprint or an applicable approved authority.

This document is vocabulary authority only. It is not a Domain Model, Entity Model, Database Schema, or Implementation Contract.

## Authority Sources

1. `docs/AIOS_ARCHITECTURE_v1.md` — Blueprint and highest Source of Truth.
2. `docs/architecture/AIOS_AUTHORITY_HIERARCHY.md` — Published material used for review without treating it as Active authority.
3. `docs/architecture/domain/AIOS_DOMAIN_FOUNDATION_MASTER.md` — only explicitly published contracts.
4. Active Governance Decisions — only for governance and lifecycle treatment.

The Frozen Roadmap remains the implementation roadmap. It supplies no canonical vocabulary and is not changed or reinterpreted here. Implementation and descriptive evidence do not create canonical concepts.

## Scope

Record canonical vocabulary and accepted input-format boundaries explicitly supported by the authority sources, and classify candidates whose authority is absent or outside this document's scope.

## Non-Goals

This document does not determine fields, schema, persistence, API, DTOs, lifecycle, behavior, processing, routing, orchestration, workflow, dependencies, ownership, serialization, transport implementation, storage layout, service boundaries, interfaces, integrations, or capabilities.

Recognition boundaries in this document establish only which declared input
forms are canonical or accepted. They do not prescribe detection,
classification, validation implementation, precedence, fallback, parsing,
normalization, canonicalization, storage, or processing behavior.

## Status Meanings

- **Canonical** — the name and limited meaning are explicitly established by an authority source.
- **UNRESOLVED** — authority does not establish the proposed object, name equivalence, or meaning.
- **OUT OF SCOPE** — the subject is outside this vocabulary authority and is not decided here.

## Canonical Vocabulary

### Request Context

**Status:** Canonical

Explicitly named in the Official Pipeline and as information AIOS Brain may consume. No fields, construction, lifecycle, behavior, dependency, or ownership are defined here.

### Metadata

**Status:** Canonical

Explicitly named in `Extract Metadata` and in the information stored by PostgreSQL. No fields, format, behavior, persistence design, or ownership are defined here.

### Document Manifest

**Status:** Canonical

Explicitly named in the Official Pipeline. The Blueprint also names `Create Manifest`. No fields, construction, lifecycle, behavior, persistence, or ownership are defined here. Whether `Manifest` is a short name for `Document Manifest` is **UNRESOLVED**.

### PostgreSQL Registry

**Status:** Canonical

Explicitly named in the Official Pipeline. No Registry Entry, schema, record shape, interface, behavior, or ownership is defined here. Whether `Registry` is identical to `PostgreSQL Registry` is **UNRESOLVED**.

### Registry

**Status:** Canonical

Explicitly named as information AIOS Brain may consume. No equivalence to `PostgreSQL Registry`, structure, interface, behavior, persistence design, or ownership is defined here.

### DomainEvent

**Status:** Canonical

The abstract base for an immutable domain record that identifies a fact that occurred, as explicitly published by the Domain Foundation Master. This document does not change its contract. The broader term `Event` is **UNRESOLVED**; `AIOS Event Engine` is a component name.

### EventEnvelope

**Status:** Canonical

The immutable, transport-neutral wrapper for one published `DomainEvent`, as explicitly published by the Domain Foundation Master. This document does not change its contract.

### AIOS Memory

**Status:** Canonical

Explicitly named as part of AIOS Brain. No structure, behavior, lifecycle, persistence, dependency, or ownership is defined here. Whether `Memory` is identical to `AIOS Memory` is **UNRESOLVED**.

### Memory

**Status:** Canonical

Explicitly named as information AIOS Brain may consume. No equivalence to `AIOS Memory`, structure, behavior, lifecycle, persistence, dependency, or ownership is defined here.

### Knowledge

**Status:** Canonical

Explicitly named as part of AIOS Brain and as information AIOS Brain may consume. No structure, behavior, lifecycle, persistence, dependency, or ownership is defined here.

## Canonical Recognition Contract — Universal Ingestion

This contract is limited to the Universal Ingestion input names already
established by the Blueprint. It adds no input capability and does not alter
the Official Pipeline or ingestion lifecycle.

### Spreadsheet Recognition

**Status:** Canonical

`Spreadsheet` is the canonical input type for documents in the accepted
formats `XLS`, `XLSX`, `CSV`, and `ODS`. This is the complete accepted
document-format set established by this contract.

This statement defines no parser, library, MIME value or precedence,
extension precedence, content inspection, fallback strategy, or processing
behavior.

### Web Link Recognition

**Status:** Canonical

`Web Link` is the canonical input type for a valid URL. Its canonical identity
is that URL. Identity here establishes only what the recognized input is; it
does not establish a stored, normalized, or canonicalized URL representation.

This statement defines no URL validation mechanism, normalization,
canonicalization, redirect handling, query cleanup, storage representation, or
processing behavior.

### YouTube Link Recognition

**Status:** Canonical

`YouTube Link` is the canonical input type for a URL whose host is a member of
this complete supported YouTube host set:

- `youtube.com`
- `www.youtube.com`
- `m.youtube.com`
- `youtu.be`

Its canonical identity is that URL. Identity here establishes only what the
recognized input is; it does not establish a stored, normalized, or
canonicalized URL representation.

This statement defines no matching algorithm, canonical URL, playlist
behavior, channel behavior, redirect handling, or processing behavior. The
host set is a recognition boundary only.

### Mixed Telegram Input

**Status:** Canonical transport fact

A Telegram transport message may carry more than one media input. `Message`
in this statement refers only to the Telegram transport message and does not
establish a canonical AIOS `Message` object.

This statement defines no precedence, selection, ordering, aggregation,
deduplication, fallback, or runtime handling behavior.

### Audio

**Status:** Canonical

`Audio` is a canonical Universal Ingestion input type, as explicitly named by
the Blueprint. Its canonical identity is `Audio`. No storage path, format set,
metadata, or processing behavior is defined here.

### Video

**Status:** Canonical

`Video` is a canonical Universal Ingestion input type, as explicitly named by
the Blueprint. Its canonical identity is `Video`. No storage path, format set,
metadata, or processing behavior is defined here.

## Authority-Supported Statements

- AIOS Brain may consume `Request Context`, `Manifest`, `Registry`, `Memory`, and `Knowledge`, using the Blueprint's exact terms.
- `EventEnvelope` wraps one published `DomainEvent`, as stated by the Domain Foundation Master.

These statements define no alias, runtime flow, lifecycle, routing, orchestration, dependency, or ownership.

## Candidate Disposition

| Candidate | Status | Authority assessment |
|---|---|---|
| Conversation | **UNRESOLVED** | Conversation contracts are not yet published; the Blueprint defines no Conversation object. |
| Message | **UNRESOLVED** | No applicable authority defines Message. |
| Request Context | **Canonical** | Explicitly named in the Blueprint. |
| Asset | **UNRESOLVED** | `Asset Pipeline` is a component name and does not establish an Asset object. |
| Original Asset | **UNRESOLVED** | Original files are required, but no object named Original Asset is established. |
| Metadata | **Canonical** | Explicitly named in the Blueprint. |
| Document Manifest | **Canonical** | Explicitly named in the Blueprint. |
| Manifest | **Canonical** | Explicitly named; equivalence to Document Manifest is **UNRESOLVED**. |
| PostgreSQL Registry | **Canonical** | Explicitly named in the Blueprint. |
| Registry | **Canonical** | Explicitly named; equivalence to PostgreSQL Registry is **UNRESOLVED**. |
| Registry Entry | **UNRESOLVED** | No individual Registry Entry object is established. |
| DomainEvent | **Canonical** | Explicitly published by the Domain Foundation Master. |
| Event | **UNRESOLVED** | A component name does not establish a broader Event object. |
| EventEnvelope | **Canonical** | Explicitly published by the Domain Foundation Master. |
| Decision | **UNRESOLVED** | `Decision Engine` does not establish a Decision object. |
| Task | **UNRESOLVED** | No applicable authority defines Task. |
| Response | **UNRESOLVED** | `Respond` is an action and does not establish a Response object. |
| AIOS Memory | **Canonical** | Explicitly named in the Blueprint. |
| Memory | **Canonical** | Explicitly named; equivalence to AIOS Memory is **UNRESOLVED**. |
| Knowledge | **Canonical** | Explicitly named in the Blueprint. |
| Spreadsheet | **Canonical** | Blueprint input; accepted document formats are XLS, XLSX, CSV, and ODS under the Canonical Recognition Contract. |
| Web Link | **Canonical** | Blueprint input; its canonical identity is a valid URL. |
| YouTube Link | **Canonical** | Blueprint input; its canonical identity is a URL whose host is `youtube.com`, `www.youtube.com`, `m.youtube.com`, or `youtu.be`. |
| Audio | **Canonical** | Explicitly named as a Universal Ingestion input by the Blueprint. |
| Video | **Canonical** | Explicitly named as a Universal Ingestion input by the Blueprint. |
| Tool | **UNRESOLVED** | No applicable authority defines Tool. |
| Mission | **UNRESOLVED** | `Mission Control v1` does not establish a Mission object. |
| Workflow | **OUT OF SCOPE** | Workflow and orchestration are outside vocabulary authority. |
| Configuration | **OUT OF SCOPE** | Configuration treatment is outside vocabulary authority. |

## Conflict, Precedence, and Supersession

The Blueprint remains the highest Source of Truth. The Domain Foundation governs only its explicitly published scope. Missing authority remains **UNRESOLVED** and is not completed by inference. This document supersedes no artifact.

## Final Architecture Review

Final Architecture Review was completed on 2026-08-03 against the Blueprint, Published Authority Hierarchy, active Governance Decisions, and explicitly published Domain Foundation contracts.

The review confirmed that this document uses only traceable names and meanings; marks unestablished objects and equivalences **UNRESOLVED**; keeps workflow and configuration **OUT OF SCOPE**; and adds no capability, implementation detail, schema, ownership, lifecycle, dependency, runtime behavior, routing, or orchestration.

The Canonical Recognition Contract extension was reviewed on 2026-08-04
against the same authorities and the Stage 3.1.1–3.1.3 evidence records. The
review confirmed that it adds only input identity, accepted Spreadsheet
document formats, URL/YouTube recognition boundaries, and the evidenced mixed
Telegram transport fact. It changes no Official Pipeline, lifecycle, layer,
dependency, storage rule, implementation detail, runtime behavior, Blueprint,
Layer Architecture, or Frozen Roadmap.

No substantive conflict was found within the declared scope.

## Approval Record

The Project Owner instruction dated 2026-08-03 explicitly approved transition through Proposed, Reviewed, and Approved after the required Final Architecture Review, followed by Publication and Activation after their gates were satisfied. Those requirements are satisfied.

## Lifecycle History

| Date | Status | Record |
|---|---|---|
| 2026-08-03 | Draft | Initial working content; no authority. |
| 2026-08-03 | Proposed | Content completed and submitted for Final Architecture Review. |
| 2026-08-03 | Reviewed | Final Architecture Review completed with no substantive conflict in scope. |
| 2026-08-03 | Approved | Project Owner approval applied after successful review. |
| 2026-08-03 | Published | Approved document and approval record accepted into repository history in commit `e719091`. |
| 2026-08-03 | Active | Published document explicitly activated for its declared vocabulary-authority scope after publication commit `d7ec441`. |
| 2026-08-04 | Active | Canonical Recognition Contract extended by explicit Project Owner instruction for the proven Stage 3.1.3 recognition gaps; authority class, hierarchy, and Active status are unchanged. |

## Publication and Activation

The approved document and approval record entered accepted repository history in commit `e719091`. Publication was explicitly recorded in commit `d7ec441`. This document is now explicitly Active as current vocabulary authority only for its declared scope.
