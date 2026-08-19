# Dependency and Brain Boundary Audit

Runtime dependencies are limited to `EventEnvelope`, standard-library
`dataclasses` and `enum`, and AIOS Core-local result/enum types.

There is no import or dependency on Event Engine runtime or delivery results,
Registry, PostgreSQL, Storage, Manifest, Brain, Memory, Specialist Router,
Specialists, business modules, or external services. `AIOS_BRAIN_BOUNDARY` is
only the bounded value meaning eligible for handoff; the runtime performs no
Brain call, LLM/Ollama call, model selection, prompt construction, or response
handling.
