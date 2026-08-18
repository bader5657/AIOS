# Minimum Asset Pipeline Contract

## Identity and Responsibility

`Asset Pipeline` is the Blueprint-named Ingestion-layer component and a bounded
orchestration/handoff boundary. It coordinates already-authorized boundary
operations and dispositions. It is not an `Asset`, `Original Asset`, `Pipeline
Asset`, aggregate, entity, value object, persistence owner, Registry, metadata
authority, Document Manifest authority, or business workflow engine.

No canonical or domain object is created by this contract.

## Lifecycle Position

```text
Request Context
  → Asset Pipeline
  → Document Manifest
```

Within its bounded coordination scope, the accepted Stage 3 order remains:

```text
Store Original where applicable
  → Extract Metadata
  → Create Document Manifest
  → Register handoff readiness
```

Asset Pipeline owns coordination of calls/handoffs only. Each invoked boundary
retains its existing semantic authority and failure contract.

## Minimum Input Contract

The initial accepted input is composed only from already-authorized values:

- one approved Request Context using its active seven-field contract;
- the upstream-recognized input/media identity, passed without reclassification
  or reinterpretation; and
- the accepted original input or accepted non-file value needed by the existing
  Stage 3 lifecycle.

The following are ordered boundary values produced and consumed during the
coordination, not additional initial-call requirements:

- successful Store Original disposition where applicable;
- successful Stage 3 metadata result; and
- existing Document Manifest-facing values required by the active minimum
  Document Manifest contract.

Reserved Request Context fields are not activated. Asset Pipeline does not
derive a new request identity, media identity, asset identity, business
identity, normalized URL, metadata meaning, or Manifest meaning.

## Manifest-facing Handoff

After successful prerequisite boundaries, Asset Pipeline may hand the existing
approved values to the Document Manifest boundary. The handoff does not create,
validate, serialize, store, or reinterpret Document Manifest semantics; those
remain owned by the active Document Manifest authority and implementation.

## Minimum Terminal Output Contract

The terminal output is a non-canonical bounded execution disposition:

- **success** — every applicable coordinated boundary through successful
  Document Manifest completion succeeded, and the existing downstream Register
  handoff-readiness disposition may be exposed; or
- **failure** — one coordinated boundary failed and no downstream success or
  readiness is represented.

The disposition may carry only existing results/references needed by the
caller, such as the accepted storage result, Stage 3 metadata result, or
Document Manifest reference. Concrete runtime type, field names, serialization,
and API shape are deliberately not defined or authorized here.

The result is not persisted as a Pipeline object and is not a Registry Entry.
It executes no Registry behavior and defines no PostgreSQL representation.

## Existing Variants

File-backed, Text, URL-only, and multi-file behavior must remain within their
accepted Stage 3 contracts. In particular, URL-only inputs perform no network
retrieval, and current multi-file behavior may not invent a representative
Manifest. Any proposed change to those accepted behaviors requires separate
authority and is not implied by this contract.
