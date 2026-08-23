# Failure, Exception, State, and Boundary Evidence

## Failure and exception behavior

Every existing provider-neutral failed `InferenceResult` passes through by
identity and unchanged:

- `INVALID_REQUEST`
- `RUNTIME_UNAVAILABLE`
- `TIMEOUT`
- `PROVIDER_FAILURE`
- `MALFORMED_OUTPUT`
- `POLICY_DENIED`
- `RESOURCE_LIMIT`

`TypeError` and `ValueError` raised during `InferenceRequest` construction
propagate before provider invocation. Unexpected provider exceptions propagate
unchanged. `asyncio.CancelledError` propagates unchanged. No exception is
swallowed or translated and no retry follows any failure or exception.

## Negative boundary verification

Source, AST/import, focused-test, and repository regression evidence confirms:

- retry: none;
- fallback: none;
- logging: none;
- persistence: none;
- Memory access: none;
- Specialist routing or invocation: none;
- business semantics: none;
- Core import or reverse dependency: none;
- concrete Ollama dependency: none;
- runtime lifecycle control: none;
- composition root, singleton, registry, or global provider: none; and
- live or production inference activation: none.

The implementation neither starts nor stops runtime infrastructure, changes a
provider adapter, reads provider configuration, resolves schemas, mutates a
VPS, nor wires Core to Brain.
