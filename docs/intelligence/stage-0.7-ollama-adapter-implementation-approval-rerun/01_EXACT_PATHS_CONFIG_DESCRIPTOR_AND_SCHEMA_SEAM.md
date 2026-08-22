# Exact Paths, Configuration, Descriptor, and Schema Seam

## Authorized paths

Repository convention uses explicit `__init__.py` files for production
packages, including `core/brain`. The complete authorized implementation diff
is exactly:

1. `core/brain/providers/__init__.py`;
2. `core/brain/providers/ollama.py`;
3. `tests/unit/brain/providers/test_ollama.py`.

No fourth source/test/configuration path is authorized. The package marker may
export only the approved adapter/configuration API; it must contain no runtime
logic or side effects.

## Configuration and descriptor

Implement `OllamaProviderConfig` as `@dataclass(frozen=True, slots=True)` with
exactly these fields:

- `base_url: str`;
- `model_id: str`;
- `timeout_ceiling_ms: int`;
- `keep_alive: str`.

The first approved values are model
`qwen2.5:1.5b-instruct-q4_K_M`, timeout ceiling `120000`, and keep-alive `5m`.
The base URL is supplied to the constructor; `172.31.63.2` must not be a code
constant or default. No credentials, routing, retry, fallback, business,
Telegram, database, production, or arbitrary provider-options fields exist.

Base URL validation must use parsed URL/IP semantics, with no DNS/network
lookup. Accept only scheme `http`, no username/password, no query/fragment,
path empty or `/`, an explicit valid port, and a host that is an IPv4/IPv6
private or loopback literal or exactly `localhost`. Reject public IPs, other
hostnames, malformed URLs, and every other component. Normalize only one
trailing `/` for safe endpoint joining; do not silently rewrite any other
invalid form.

The configured model ID must equal the single approved exact model. Timeout
must equal `120000` and keep-alive must equal `5m` in this first implementation;
invalid alternatives fail construction. These remain immutable configuration,
not per-request controls.

`OllamaInferenceProvider.descriptor` returns exactly:

- `provider_id="ollama-local"`;
- the configured exact model ID;
- `ProviderRuntimeKind.LOCAL`; and
- `(InferenceCapability.STRUCTURED_INFERENCE,)`.

## Injected schema seam

Define the minimal resolver and validator callable protocols/type aliases
inside `core/brain/providers/ollama.py`; do not create a registry or fourth
module.

- resolver accepts one opaque `output_schema_ref` and returns one approved,
  bounded JSON-compatible schema mapping;
- validator accepts that ref and the parsed output mapping, returning normally
  only on conformance and raising a documented bounded validation exception on
  mismatch.

Both are constructor-injected. Resolution occurs after request/payload checks
and before HTTP. Unknown/unapproved refs map to `INVALID_REQUEST`. A detached
plain schema is sent in Ollama `format`; after parsing, the validator is invoked
independently. Provider-side enforcement is defense in depth only.

No policy seam is added in v1. `POLICY_DENIED` remains in the provider-neutral
taxonomy for future approved policy use but is not synthesized by this adapter.
