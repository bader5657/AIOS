# Contract, Lifecycle, and Input Outcome

## Accepted Asset Pipeline Outcome

The runtime is a non-canonical, stateless, single-execution bounded
orchestrator/handoff. It has no historical six-state model, persistent
Pipeline state, canonical `Asset`/`Original Asset`, business semantics, or
ownership of Storage, Metadata, or Document Manifest meaning.

Its frozen runtime transport surface is limited to bounded success/non-success,
stored path where applicable, existing metadata, Manifest path, and Register
handoff readiness.

## Verified Lifecycle

```text
Recognition
  → Request Context
  → Asset Pipeline
  → Store Original where applicable
  → Extract Metadata
  → Create Document Manifest
  → Register handoff readiness
```

- recognition remains upstream;
- the active seven-field Request Context is constructed before Pipeline;
- applicable Storage precedes Metadata;
- Metadata precedes Document Manifest;
- readiness is true only after successful Manifest creation; and
- Registry itself is never executed.

## Input Result

| Approved class/variant | Result |
|---|---|
| Text | PASS |
| Image | PASS |
| Voice | PASS |
| Audio | PASS |
| Video | PASS |
| PDF | PASS |
| DOC/DOCX | PASS |
| Spreadsheet | PASS |
| Web Link | PASS — exact URL; no retrieval |
| YouTube Link | PASS — exact URL; no retrieval |
| Single-file | PASS |
| Multi-file | PASS — aggregate behavior preserved; no representative Manifest invented |

No media class was added. `Manifest` remains invalid as an input/media class.
