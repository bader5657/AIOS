# Boundary, Dependency, and Invariant Review

## Result invariants

Successful construction requires all of:

- `success is True`;
- `failure_code is None`;
- bounded `structured_output` is present; and
- non-null bounded `provider_id` and `model_id` are present.

Failed construction requires all of:

- `success is False`;
- an exact `FailureCode` is present; and
- `structured_output is None`.

Provider/model identifiers may independently be `None` on failure according to
the boundary reached. Partial or malformed output has no success form; the
approved representation is `MALFORMED_OUTPUT` failure with discarded content.
Constructor validation rejects impossible success/failure states.

## Dependency and ownership review

The contract module imports only Python standard-library modules. It imports
no Core implementation, provider SDK, Ollama, OpenAI, Anthropic, Gemini, HTTP
client, database, persistence, Memory, Specialist, tool, or business runtime.
No dependency/requirements file changed.

Core does not import `core.brain`; dependency direction and Core semantics are
unchanged. `output_schema_ref` remains an opaque bounded reference: there is no
schema registry, resolution, or execution in Stage 0.3.

## Closed boundary findings

Final review confirms:

- provider-neutrality and stateless invocation boundary: PASS;
- no Core reverse dependency or architecture change: PASS;
- no persistence, retry, Memory, Specialist, tool, or business semantics: PASS;
- no raw/partial provider response field or serialization path: PASS;
- no false-success or partial-success state: PASS;
- bounded stable JSON-compatible serialization: PASS;
- no Brain orchestration, provider runtime, model execution, or activation:
  PASS; and
- no service, production, VERSION, database, or VPS mutation: PASS.
