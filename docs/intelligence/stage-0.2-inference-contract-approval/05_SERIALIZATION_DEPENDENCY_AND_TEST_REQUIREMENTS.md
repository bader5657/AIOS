# Serialization, Dependency, and Test Requirements

## Python and serialization direction

Future implementation must use project-consistent:

- frozen + slots dataclasses;
- string enums with the stable values approved in this package;
- explicit constructor/post-construction validation;
- recursively immutable snapshots of nested mappings/sequences;
- explicit JSON-compatible serialization and deserialization;
- included `schema_version`;
- no pickle, Pydantic addition, arbitrary object serialization, or
  provider-specific serialization; and
- fail-closed rejection of unsupported schema versions.

The exact JSON wire representation and compatibility procedure must be frozen
in implementation approval. V1 does not promise compatibility with an
unapproved schema; additive or breaking changes require explicit contract
version authority.

## Provider neutrality and dependencies

No Ollama, OpenAI, Anthropic, Gemini, provider SDK, endpoint, network client,
credential, provider-native schema, response, or error object may appear in
the contracts. Future adapters translate to/from the approved types.

Static dependency gates must prove:

- Core Platform does not import Brain implementation;
- `core/brain/inference_contracts.py` does not import AIOS Core, provider SDKs,
  Memory, Specialist, business, tool, persistence, network, or runtime code;
- provider adapters cannot redefine Brain/Core ownership; and
- no reverse semantic dependency is introduced.

## Required implementation tests

Future implementation approval must require tests for:

1. frozen immutability, slots, and recursively immutable nested values;
2. all required, optional, deferred, and prohibited field decisions;
3. schema version `1`, positive-integer validation, and unsupported rejection;
4. non-empty/bounded opaque correlation and request IDs and exact preservation;
5. sole `STRUCTURED_INFERENCE` capability and rejection of other values;
6. bounded JSON payload and output-schema-reference validation;
7. opaque, immutable, bounded reference behavior without retrieval;
8. positive timeout, Brain ceiling, `TIMEOUT`, and no retry;
9. success/failure invariant exclusivity;
10. exact seven-code `InferenceFailureCode` completeness;
11. malformed/partial output fail-closed behavior;
12. nullable provider/model semantics and no secret metadata;
13. bounded non-negative duration;
14. failure-detail sanitization and empty v1 warnings;
15. explicit JSON serialization and enum string values;
16. raw provider response, persistence, tool, Memory, Specialist, and business
    field absence;
17. provider-neutral import/source audit; and
18. no Core Platform reverse import or semantic modification.

These are future gates only. No test or contract implementation runs in this
governance task.
