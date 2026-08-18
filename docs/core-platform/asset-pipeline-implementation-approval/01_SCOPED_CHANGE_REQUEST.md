# Scoped Change Request

## Objective

Create a new, minimum, contract-first Asset Pipeline runtime that replaces—
rather than restores—the historical implementation and integrates it with the
existing Universal Ingestion caller.

The implementation is limited to a bounded, single-execution orchestration and
handoff component. It delegates to active Stage 3 capabilities and preserves
their semantics, ordering, failure gates, and outputs.

## Required Outcome

- the Blueprint-named Asset Pipeline exists in current runtime;
- approved Request Context and upstream recognition reach it before execution;
- file-backed, Text, URL-only, and multi-file variants preserve accepted
  behavior;
- applicable Storage precedes Metadata and Metadata precedes Document Manifest;
- only a non-canonical bounded success/non-success result is returned;
- no persistent state model exists;
- no Registry or PostgreSQL behavior exists; and
- all changes remain inside the closed file list.

## Non-Goals

No retry, recovery, compensation, transaction, duplicate, deduplication,
idempotency, persistence, business workflow, routing, processing, Intelligence,
new media semantics, new canonical object, architecture redesign, deployment,
or later Stage 4 capability is authorized.
