# Harness, Request, Result, and Evidence

Use one temporary operator-side Python harness under `/tmp`, importing the
exact clean repository checkout. Do not commit the harness or modify source.
It must construct an explicit validated OllamaProviderConfig and use repository
`create_staging_composition`; no temporary provider composition or schema
resolver/validator is allowed.

Call counts are exactly:

- projector: `1`;
- mapper: `1`;
- Brain boundary: `1`;
- provider inference: `1`;
- HTTP `POST /api/chat`: `1`.

A composition client factory may install a bounded httpx request event hook to
count the sole POST. It must not issue a health call. There is no retry,
fallback, second request, warm run, or benchmark loop. Reaching or exceeding
120000 ms fails the execution.

Success requires an InferenceResult with `success=True`, no failure code,
exact provider/model and preserved correlation/request IDs, and a structured
Mapping with exact key set `{result}` whose value is a string. Repository
`validate_schema("brain_structured_inference_result_v1", structured_output)`
must return None. No particular semantic answer is required.

Do not retain a raw provider response. Retain one bounded, secret-free evidence
record at exactly:

`/opt/aios/runtime/intelligence/staging/stage-0.20-evidence/00_CONTROLLED_SYNTHETIC_EXECUTION.json`

The record contains source SHA/module paths; runtime/config identity; preflight;
synthetic input and projected mapping; IDs; CoreRouteResult; provenance; call
counts; latency; InferenceResult metadata; bounded structured output; schema
validation; resource observations; postflight; production preservation; and
final classification. It must be created once and must not overwrite any
existing file or Stage 0.15 evidence.
