# Exact Scope and Brain Package Prerequisite

## Repository finding

At the approval baseline, `core/brain/` and `tests/unit/brain/` do not exist.
Existing source and test package directories consistently contain
`__init__.py`. Creating the Brain initializer is therefore required for a
repository-conformant explicit Python package; it creates the already-approved
Brain namespace, not an Intelligence layer.

## Exact authorized implementation paths

Exactly these three paths may be added in the future implementation change:

1. `core/brain/__init__.py`
2. `core/brain/inference_contracts.py`
3. `tests/unit/brain/test_inference_contracts.py`

The initializer must contain no runtime activation, provider selection, or
side effects. No additional source, test, configuration, dependency,
documentation, service, migration, or production path is authorized. If a
fourth implementation path is necessary, implementation must stop with
`INTELLIGENCE STAGE 0.3 SCOPE EXPANSION REQUIRED`.

## Type ownership and API names

`core/brain/inference_contracts.py` owns:

- `InferenceRequest`: frozen, slotted dataclass and recursively immutable
  snapshot;
- `InferenceResult`: frozen, slotted dataclass and recursively immutable
  snapshot;
- `InferenceCapability`: `str, Enum`, with only
  `STRUCTURED_INFERENCE = "structured_inference"`; and
- `FailureCode`: `str, Enum`, with exactly the seven approved values.

`FailureCode` is the Stage 0.3 public Python name for the Stage 0.2 failure
taxonomy. Its values are exactly:

- `INVALID_REQUEST = "invalid_request"`
- `RUNTIME_UNAVAILABLE = "runtime_unavailable"`
- `TIMEOUT = "timeout"`
- `PROVIDER_FAILURE = "provider_failure"`
- `MALFORMED_OUTPUT = "malformed_output"`
- `POLICY_DENIED = "policy_denied"`
- `RESOURCE_LIMIT = "resource_limit"`

No aliases or additional enum members are authorized.

## Explicit exclusions

No provider/model implementation, SDK, HTTP client, Ollama, database,
persistence, tools/functions, session, Memory, Specialist, business action,
Core wiring, service change, model invocation, production import-path change,
or runtime activation is authorized.
