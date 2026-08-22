# Observability, Security, Dependency, and Resource Boundaries

## Observability

After separate runtime approval, an adapter may emit only bounded metadata by
default:

- `correlation_id`;
- `request_id`;
- `provider_id`;
- `model_id`;
- duration;
- success/failure; and
- `failure_code`.

Default logs must exclude `input_payload`, `structured_output`, raw provider
response, prompt, Telegram content, user/business content, and credentials.
Stage 0.4 activates no logging.

## Security and policy

The abstraction owns no tool permission, shell execution, filesystem
authority, Memory, Specialist Router, Specialist, business action, or policy
store. Approved policy must be applied before provider execution. Provider
execution remains data-only unless later authority explicitly expands it.

## Core and Brain dependency direction

AIOS Core must not import the provider abstraction. Core remains unchanged and
stops at `AIOS_BRAIN_BOUNDARY`.

The allowed conceptual direction is:

`Brain orchestration → provider abstraction → provider adapter`

A provider adapter may import Brain inference contracts and approved provider
abstraction types. It must not import Core implementation to acquire semantic
ownership. This approval does not implement or activate Brain orchestration.

## Resource ceiling boundary

The abstraction and descriptor carry sanitized identity/classification
metadata only. They do not enforce CPU, RAM, model-size, concurrency, or
timeout resources unless later runtime authority explicitly assigns that
responsibility.

Before activation, future runtime configuration must establish exact CPU, RAM,
disk/model-size, concurrency, timeout, startup-impact, and production-service
interaction ceilings. No resource controller or production consumption is
approved here.
