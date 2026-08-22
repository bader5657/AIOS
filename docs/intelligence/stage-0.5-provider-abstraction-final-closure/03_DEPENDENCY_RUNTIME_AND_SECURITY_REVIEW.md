# Dependency, Runtime, and Security Review

## Dependency direction

`core/brain/provider.py` imports only Python standard-library ABC/dataclass/enum
facilities and `core.brain.inference_contracts`. It imports no AIOS Core,
Telegram, Registry, Event Engine, Storage, database, Memory, Specialist,
business/domain runtime, network/HTTP client, subprocess/runtime loader, or
provider SDK.

AIOS Core does not import Brain/provider code. Core remains unchanged and stops
at `AIOS_BRAIN_BOUNDARY`. The approved conceptual direction remains Brain
orchestration → provider abstraction → future provider adapter; no orchestration
or adapter is implemented or activated.

## Provider neutrality and security

There is no Ollama, OpenAI, Anthropic, Gemini, provider SDK, branded provider
type, endpoint, credential, network authority, filesystem/shell authority,
tool, Memory, Specialist, business, or persistence ownership in production
source.

The string-enum equality finding discovered during implementation was closed by
explicit enum-type validation, preventing a raw capability string from being
accepted as an `InferenceCapability` member.

## Runtime and production state

- provider adapter/runtime/model: none;
- model/provider selection: none;
- Brain activation: none;
- network/local process authority: none;
- dependency/requirements change: none;
- service/VERSION/database change: none;
- production/VPS action: none.
