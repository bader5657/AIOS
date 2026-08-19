# Dependency Audit

AIOS Core runtime dependencies are limited to:

- Domain Foundation `EventEnvelope`;
- standard-library `dataclasses` and `enum`; and
- AIOS Core-local result and enum types.

There is no dependency on Event Engine runtime or result types, Registry,
PostgreSQL, Storage, Metadata, Manifest, Brain, Memory, Specialist Router,
business modules, infrastructure, or external services. The dependency audit
reports no broken requirements.
