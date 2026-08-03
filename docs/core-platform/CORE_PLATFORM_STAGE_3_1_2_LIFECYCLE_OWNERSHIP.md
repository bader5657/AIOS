# Core Platform Stage 3.1.2 Lifecycle Ownership and Boundaries

## Record

| Field | Value |
|---|---|
| Execution Plan position | Stage 3 — Main Step 3.1 — Sub Step 3.1.2 |
| Mapping baseline | `98f20a08be83f68486cc535785edebf6343fd8ed` (`main`) |
| Lifecycle scope | Receive → Store Original → Extract Metadata → Create Manifest → Register → Process → Route → Respond |
| Input evidence | Blueprint, Sub Step 3.1.1 matrix, current call path, Registry/Event Engine dispositions |
| Mapping date | `2026-08-03` |
| Result | **PASS with required stop at undefined Process/Route ownership** |

This record maps ownership and hand-off boundaries for exactly the Blueprint
ingestion lifecycle. It makes no runtime change, implements no transition, and
does not pull Intelligence behavior into Core Platform.

## Ownership Terms

| Term | Meaning in this record |
|---|---|
| Transport owner | Receives or delivers data through the existing Telegram communication boundary |
| Orchestration owner | Orders calls and passes outputs between bounded executors |
| Execution owner | Performs one named lifecycle operation |
| Downstream owner | Receives a completed bounded output but is not implemented by the preceding component |
| Unresolved | Blueprint names the step but current authority does not define its responsible component or behavior |

These terms describe current/approved boundaries only. They do not create a
new service, module, API, state machine, event, or workflow.

## Approved Ownership and Boundary Map

| Lifecycle step | Approved owner/boundary | Current implementation evidence | Decision/status |
|---|---|---|---|
| Receive | Telegram Adapter owns transport receipt; Universal Ingestion owns acceptance of the handed-off Telegram message | `handle_update()` validates the update and calls `ingest_telegram_message()` | BOUNDED — adapter performs no ingestion business logic |
| Store Original | Universal Ingestion orchestrates; Storage owns file persistence | Ingestion calls `save_telegram_attachment()`; Telegram storage downloads; `save_file()` persists | BOUNDED for file attachments, with capability/path gaps retained |
| Extract Metadata | Universal Ingestion orchestrates; Metadata Engine owns extraction | Ingestion calls `extract_basic_metadata()` only after a stored path exists | BOUNDED for the current stored-file path; metadata contract remains Stage 3.3.1 |
| Create Manifest | Universal Ingestion currently orchestrates; Document Manifest module owns current file creation | Ingestion calls `create_document_manifest()` after metadata extraction | CURRENT BOUNDARY ONLY — official pipeline alignment is not established |
| Register | PostgreSQL Registry owns registration downstream of Document Manifest | No current Registry runtime or ingestion registry call exists; historical no-op Registry was rejected | MISSING — declared hand-off, not ingestion-owned persistence |
| Process | No owner defined by current Blueprint/authority | No current function or approved component contract maps this lifecycle term | UNRESOLVED — required stop |
| Route | No Core Platform owner defined; Specialist Router behavior is explicitly excluded | No current route call exists; Event Engine/Core contracts are reserved for Stages 6–7 | UNRESOLVED — required stop before Intelligence |
| Respond | Telegram Adapter owns transport delivery only; response-content ownership is unresolved | Current adapter formats and sends a receipt-style response after ingestion/Request Context | PARTIAL BOUNDARY — delivery is evidenced; lifecycle response semantics are not approved |

## Authoritative Ingestion-Owned Boundary

Within current authority, Universal Ingestion may own only bounded
orchestration of:

```text
accepted Telegram input
→ request Storage execution where applicable
→ request Metadata Engine execution after successful storage
→ request Document Manifest execution after storage/metadata
→ expose the bounded result for a future Register hand-off
```

Universal Ingestion does not own:

- PostgreSQL persistence or Registry behavior;
- Process semantics;
- routing, specialist selection, or clarification behavior;
- AIOS Event Engine dispatch;
- AIOS Core behavior;
- AIOS Brain or Specialist Router behavior; or
- business-response generation.

The Register hand-off is declared but cannot execute until the Stage 5
Registry contract and runtime exist. It must not be silently skipped when the
end-to-end lifecycle is later represented as complete.

## Current Call Path Versus Official Pipeline

The current Telegram call path is:

```text
Telegram Adapter
→ Universal Ingestion
→ Storage
→ Metadata Engine
→ Document Manifest
→ return IngestionResult
→ RequestContext.from_telegram()
→ Telegram receipt response
```

The official pipeline instead places Request Context and Asset Pipeline before
Document Manifest, followed by PostgreSQL Registry, AIOS Event Engine, and
AIOS Core. The current ingestion call path therefore:

- creates Document Manifest before the adapter creates Request Context;
- has no current Asset Pipeline call;
- has no Register call;
- has no Process or Route call with approved ownership; and
- sends a receipt response without proving the complete lifecycle.

This record does not approve the current ordering as final architecture. Asset
Pipeline integration belongs to Stage 4, Registry integration to Stage 5,
Event Engine to Stage 6, and AIOS Core authority/boundary work to Stage 7.

## Required Stop Boundary

The Execution Plan explicitly requires this Sub Step to stop where Process or
Route ownership is undefined. Both are undefined by current authority.

Accordingly:

1. the approved ownership map ends at the declared Register hand-off;
2. no Process transition, processor, status, API, or component is inferred;
3. no Route transition, router, specialist behavior, dispatch rule, or API is
   inferred; and
4. Respond remains limited to evidenced adapter transport delivery, not a
   claim that the lifecycle has completed.

This stop is an authority boundary within the completed mapping deliverable.
It does not create a new authority document or alter the Execution Plan.

## Retained Findings from Sub Step 3.1.1

The following findings are outside lifecycle-ownership resolution and remain
unresolved:

- Audio/Video storage destinations;
- media subtype and spreadsheet extension/MIME rules;
- URL/YouTube recognition and original-link representation;
- mixed Telegram input handling;
- distinct runtime storage roots and naming;
- original Telegram filename preservation; and
- complete ten-input runtime coverage.

They are not solved, reclassified, or used to expand this Sub Step.

## Authority Findings

Newly explicit lifecycle findings are:

- Blueprint names Process but does not map it to Asset Pipeline, Registry,
  Event Engine, AIOS Core, or another owner after Register;
- Blueprint names Route but does not establish a Core Platform routing owner,
  while Specialist Router is a later excluded capability;
- Blueprint names Respond but does not define response-content ownership or
  distinguish acknowledgement from completed business response; and
- current manifest creation order bypasses the official Request Context and
  absent Asset Pipeline positions.

These findings require later frozen-plan contracts or Project Owner authority.
They do not authorize implementation here.

## Validation Plan

Validation consists of:

- read-only source inspection of the Telegram adapter and Universal Ingestion
  call path;
- static confirmation that Store precedes Metadata and Manifest calls in the
  current function;
- static confirmation that no Register, Process, or Route call exists;
- the retained Core Platform focused regression suite; and
- the accepted repository-root Domain Foundation regression command.

No new runtime test is required for this mapping-only Sub Step. Sequence and
boundary tests belong to Sub Step 3.1.4 after authoritative transitions and
hand-offs are implementable.

Observed results:

```text
Current call order: Store → Metadata → Manifest
Register call: ABSENT
Process call: ABSENT
Route call: ABSENT
Adapter delivery after ingestion: CONFIRMED
Core Platform focused suite: Ran 16 tests in 0.009s — OK
Official repository-root suite: Ran 212 tests in 0.041s — OK
```

## Scope Boundaries and Result

The only created artifact is this lifecycle ownership/boundary record. No
existing runtime, Request Context contract, schema, test, dependency,
configuration, or behavior is changed. No Blueprint, Roadmap, Governance,
`VERSION`, Domain Foundation, Execution Plan, freeze document, milestone,
source, deployment, service, architecture, authority, or workflow artifact is
changed.

**Sub Step 3.1.2 result: PASS with required stop boundary**

Main Step 3.1 remains in progress. The next frozen-plan position is Stage 3,
Main Step 3.1, Sub Step 3.1.3. That Sub Step is not started by this record.
