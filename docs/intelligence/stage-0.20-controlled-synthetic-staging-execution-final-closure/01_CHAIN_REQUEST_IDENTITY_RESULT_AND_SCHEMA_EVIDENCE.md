# Chain, Request Identity, Result, and Schema Evidence

The sole request used only this repository-owned chain:

`project_text_semantics → CoreToBrainMapper → BrainInput → create_staging_composition → BrainSemanticReceiver → BrainInferenceInvoker → OllamaInferenceProvider → repository resolve_schema / validate_schema → isolated Ollama/Qwen → InferenceResult`

Universal Ingestion and AIOSCore routing were not invoked. One exact eligible
prebuilt CoreRouteResult supplied `success=True`,
`route_target=AIOS_BRAIN_BOUNDARY`, `failure_code=None`, and
`failure_reason=None`.

| Request control | Verified value |
|---|---|
| Synthetic text | `Temperature stable and vibration within normal range.` |
| Projected mapping | `{"text":"Temperature stable and vibration within normal range."}` |
| Correlation ID | `corr-20000000000040008000000000000020` |
| Request ID | `brain-20000000000040008000000000000021` |
| Input reference | `stage-0.20-synthetic-input-1` |
| Context references | `()` |
| Projector calls | `1` |
| Mapper calls | `1` |
| Brain boundary calls | `1` |
| Provider inference calls | `1` |
| `POST /api/chat` calls | `1` |
| Retry / fallback | `0 / 0` |
| Total / provider latency | `75670 / 75479 ms` |

The InferenceResult was successful with no failure code, provider ID
`ollama-local`, model ID `qwen2.5:1.5b-instruct-q4_K_M`, and the exact preserved
correlation and request IDs. Its bounded structured output was:

```json
{"result":"Temperature remains constant and vibration levels are within normal parameters."}
```

The output was a Mapping with exact key set `{result}` and exact string value
type. Repository
`validate_schema("brain_structured_inference_result_v1", structured_output)`
returned successfully. Evidence 02 retains bounded request/result metadata and
structured output only; it does not retain the raw provider response.
