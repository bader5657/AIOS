# Validator, Failure, Provider, and Side-Effect Contract

Implement the existing provider-compatible callable shape:

`validate_schema(schema_ref: str, value: Mapping[str, object]) -> None`

Reference validation is identical to the resolver: non-string raises TypeError
and unknown string raises ValueError. The value must be a Mapping or TypeError
is raised. It must contain the exact key set `{"result"}` or ValueError is
raised. The result value must have exact string type; every other type raises
TypeError. Empty and Unicode strings are accepted unchanged. There is no
coercion, repair, stripping, canonicalization, input mutation, or returned
replacement. Success returns None.

No custom exception hierarchy or FailureCode change is authorized. Existing
Ollama behavior remains unchanged: resolver exceptions follow its current
INVALID_REQUEST path, while validator exceptions follow MALFORMED_OUTPUT.

The binding is provider-neutral and must not import Ollama, provider
implementation/configuration, httpx, model/runtime data, Receiver, Core,
Telegram, Registry/database, filesystem/network helpers, environment/config,
logging, persistence, Memory, Specialist, or business/domain modules.

Future composition may inject `resolve_schema` and `validate_schema` into the
existing Ollama seams. Stage 0.18 does not modify the provider or receiver and
does not create composition, runtime lifecycle, Level B activation, or live
inference.
