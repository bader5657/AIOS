# Import, Compatibility, and Prohibited Scope

## Allowed imports and dependency direction

`core/brain/provider.py` may import only:

- Python standard-library modules needed for `ABC`, `abstractmethod`,
  dataclasses, and enums; and
- `InferenceRequest`, `InferenceResult`, and `InferenceCapability` from
  `core.brain.inference_contracts`.

No new dependency or requirements change is authorized. The module must not
import AIOS Core implementation, Telegram, Registry, Event Engine, Storage,
Memory, Specialist, business/domain runtime, database, HTTP/network clients,
subprocess/runtime loaders, provider SDKs, or provider adapters. Core modules
must remain unchanged and must not import Brain/provider code.

## Provider neutrality and compatibility

Static/source audits must reject provider-specific implementation imports or
ownership strings such as Ollama, OpenAI, Anthropic, or Gemini except as
negative assertions inside the focused test. No SDK type may appear in the
public or internal contract.

Both `LOCAL` and `REMOTE` descriptors must validate without network,
subprocess, filesystem, model, endpoint, or provider implementation code.

- LOCAL compatibility grants no installation, download, process startup, or
  model invocation authority.
- REMOTE compatibility grants no DNS, HTTP, socket, credential, or outbound
  network authority.

## Explicitly prohibited implementation

The future change must not implement `OllamaProvider`, `OpenAIProvider`,
`AnthropicProvider`, `GeminiProvider`, `LocalProvider`, `RemoteProvider`, a
provider factory/router/registry/runtime loader, schema validator/registry,
configuration format, credential resolution, model selection, Brain
orchestration, persistence, retry/fallback, or resource controller.

No provider/model selection or installation, service/VERSION modification,
production mutation, or VPS action is authorized.
