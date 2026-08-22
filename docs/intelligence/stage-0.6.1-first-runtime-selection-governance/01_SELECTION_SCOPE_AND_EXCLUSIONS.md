# Selection Scope and Exclusions

## First runtime selection

`FIRST_RUNTIME_CLASS = LOCAL`

LOCAL is selected solely to prove the approved request/provider/result path in
controlled isolated staging without a paid API dependency, outbound inference
content exposure, vendor dependency, or production activation.

`FIRST_RUNTIME_TECHNOLOGY_CANDIDATE = OLLAMA`

`OLLAMA STATUS = SELECTED FOR CONTROLLED STAGING EVALUATION ONLY`

Ollama is compatible with the existing provider abstraction, CPU execution,
configurable external model storage, and structured-output/JSON-schema use,
and has a simpler initial operational surface than direct llama.cpp packaging.
This selection does not authorize installation, download, model execution,
public/private API activation, or production use.

`llama.cpp = SECONDARY FALLBACK CANDIDATE`

llama.cpp is not selected for first implementation. Dual-runtime support is
prohibited.

## Count and selection policy

The first milestone is bounded to exactly:

- one runtime;
- one provider adapter;
- one model;
- one loaded model at a time;
- one concurrent inference; and
- at most one pending request.

Provider routing, dynamic model selection, multi-model loading, ensemble,
retry, fallback provider, fallback model, and alternate model are prohibited.

## Production and paid API status

`LOCAL PRODUCTION INFERENCE = NOT AUTHORIZED`

`PAID_REMOTE_AI_API = NOT AUTHORIZED`

There is no API key, subscription, remote fallback, or paid use authority. A
generic REMOTE provider remains only a separately governed future strategy.
