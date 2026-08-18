# Selected Disposition — REPLACE

## Decision

**HISTORICAL ASSET PIPELINE IMPLEMENTATION DISPOSITION: REPLACE**

The historical implementation is not restored, copied, or used as the base
runtime. A later implementation may use only the conceptual evidence expressly
listed in this package and must be designed against the active Stage 4.1.1 and
Stage 2–3 contracts.

## Rationale

The useful orchestration idea is real, but retaining the historical file would
require rewriting most of its meaningful contract surface. Replacement is
smaller, clearer, and less likely to preserve unauthorized state/API semantics.
It also avoids sentimental code preservation while satisfying the Blueprint
and Execution Plan requirement for an Asset Pipeline runtime.

## Historical Code That Must Not Return

- the historical `process(source_path, media_type, original_filename,
  telegram_*_id)` signature;
- `core/pipeline/state.py` and its six-value enum;
- `AssetPipelineResult.status: AssetPipelineStatus`;
- image-root storage for every input;
- historical metadata and Manifest call signatures or field semantics;
- unconditional `COMPLETED` status;
- inferred retry, recovery, duplicate, transaction, or state transitions;
- the historical test as sufficient coverage; and
- direct restoration or cherry-pick of commit `9d1288c`.

## Disposition Authority Limit

`REPLACE` authorizes only the future direction. It grants no runtime, test,
schema, dependency, integration, or implementation approval.
