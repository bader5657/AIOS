# Identifier Policy, Semantic Ownership, and Provenance

## Correlation identity

The originating request context owns `correlation_id`. A future boundary
mapper validates and copies it unchanged; neither AIOS Core nor Brain may
rewrite or regenerate it. If a valid correlation identifier is absent, mapping
fails before inference. It remains stable through `BrainInput`, future
`InferenceRequest`, and `InferenceResult`.

## Request identity

The future Core-to-Brain boundary mapper solely owns creation of one unique
`request_id` for one Brain handoff attempt. Core routing and Brain must not
independently create competing IDs. The mapper freezes it in `BrainInput`, and
Brain preserves it into inference request/result metadata.

## Instruction, data, timeout, and schema ownership

- Core supplies no prompt or instruction. It supplies an approved semantic
  `intent` and bounded semantic `data` to the boundary mapper.
- The semantic source feeding the mapper owns the meaning and authorization of
  `data`; the mapper only validates/snapshots it. V1 approval authorizes only
  synthetic/general data, not customer/order/transaction content.
- Brain policy maps an approved `intent` to provider-neutral `instruction`.
- Brain policy owns inference `timeout_ms` within existing contract ceilings.
- Brain policy owns `output_schema_ref` selection and resolution.

Those Brain-policy mappings are not implemented or approved by this
evaluation. Core cannot select them.

## Provenance

`input_reference` is the sole optional opaque source/provenance reference. A
future mapper may place an already-authoritative string event reference there;
it may not embed or stringify an entire `EventEnvelope`. `context_references`
carry only bounded opaque references. V1 neither dereferences nor persists
them and adds no separate `originating_event_id` field.

## Stage 0.10 equality control

Before any inference side effect, the future receiver must verify that
`correlation_id` and `request_id` in the values passed to
`BrainInferenceInvoker` exactly equal the immutable `BrainInput` values. A
mismatch fails closed before provider invocation. Controlled test harnesses
must additionally derive frozen identifiers from their governing approval.
