# Runtime Contract

## Responsibility

The new Asset Pipeline is an Ingestion-layer, non-canonical, stateless
single-execution orchestrator/handoff. It coordinates existing functions but
does not own or recreate recognition, storage, metadata, or Document Manifest
semantics.

## Minimum Input

Universal Ingestion remains upstream and must supply:

- one active seven-field `RequestContext`, constructed through the existing
  approved factory before Pipeline invocation;
- `recognized_input_type.value` or the equivalent already-authorized primitive
  string, without reclassification;
- the already accepted Telegram original/non-file transport value required by
  current Storage behavior;
- the upstream-enumerated primitive file-original type values for multi-file
  input, without Pipeline reinterpretation; and
- exact accepted Text or URL value where applicable.

Successful storage disposition, Stage 3 metadata, and Document Manifest-facing
values are sequential internal handoffs produced by the delegated capabilities;
they are not duplicated input semantics.

No new input DTO, canonical type, media enum, normalization, or reserved Request
Context field is authorized.

## Minimum Output

A runtime-only `AssetPipelineResult`-style transport value is permitted with no
more than:

- a boolean bounded handoff success/non-success disposition;
- accepted stored path or `None`;
- existing Stage 3 metadata result;
- accepted Document Manifest path or `None`; and
- existing Register handoff-readiness boolean.

Names may follow current project style, but these meanings and fields are the
maximum approved surface. The value is not canonical, domain, serializable by
contract, persistent, a lifecycle state machine, or a Registry Entry.

Success is true only after successful Document Manifest completion and existing
Register handoff readiness. Multi-file aggregate-only handling remains
non-success for downstream handoff and must not invent a representative
Manifest.

## Execution

```text
Universal Ingestion recognition
  → approved Request Context
  → Asset Pipeline
  → Store Original where applicable
  → Extract Metadata
  → Create Document Manifest
  → bounded result / Register handoff readiness only
```

Pipeline must call current capabilities; it must not copy their logic. URL-only
inputs perform no network retrieval. Register is never called.
