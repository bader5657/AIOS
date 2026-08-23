# Test, Regression, Dependency, and Prohibition Gates

## Focused tests

`tests/unit/brain/test_input_contracts.py` must verify at minimum:

- frozen, slotted class and exact seven ordered fields;
- exact local schema version and rejection of Boolean/wrong versions;
- valid, blank, oversized, whitespace-only, and control-character IDs;
- exact `BrainIntent.STRUCTURED_INFERENCE` and rejection of raw/unsupported
  intent values;
- mapping and empty data acceptance; nested JSON acceptance;
- rejection of non-mapping data, non-string keys, NaN/infinity, unsupported
  objects, depth/member/encoded-size overflow;
- recursive immutability and detached snapshot behavior;
- optional input reference and every reference bound;
- list/tuple context input normalized to an immutable tuple and count bound;
- absence of instruction, timeout, schema, provider/model, canonical-object,
  Memory, Specialist, business, serialization, logging, and persistence APIs;
- constructor rejection of unknown fields; and
- standard-library-only imports with no Core, inference-contract, provider,
  runtime, Memory, Specialist, or business imports.

Durable AST/source audits must establish that neither authorized file embeds
or imports `CoreRouteResult`, `EventEnvelope`, Manifest, Registry rows, or
canonical business objects. The focused tests may inspect symbols/source but
must not require a third helper path.

## Required regression matrix

After implementation, run:

- focused BrainInput tests;
- `tests/unit/brain/test_inference_contracts.py`;
- `tests/unit/brain/test_inference.py`;
- `tests/unit/brain/providers/test_ollama.py` with mocks only;
- Core and Domain regression suites;
- Stage 8 failure/import gates and existing Stage 9 gates;
- compile/static checks;
- dependency/import and prohibited-source audits;
- full repository tests;
- `git diff --check`; and
- exact closed-world diff audit proving only the two authorized paths changed.

No test may make a live inference request.

## Dependency direction and exclusions

`input_contracts.py` uses standard-library dependencies only and imports no
Core or inference/provider implementation. This approval does not authorize
general Core imports of Brain. A future mapper may construct `BrainInput` only
under separately approved narrow boundary dependency authority.

No whole `CoreRouteResult`, `EventEnvelope`, Manifest, Registry row, or
business canonical object may be a field or nested semantic shortcut. Opaque
references and bounded semantic data are the only approved representation.

Logging, persistence, Memory, Specialists, business behavior, retry, fallback,
provider/model/runtime configuration, and production use are all absent.
