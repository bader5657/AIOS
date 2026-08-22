# Exact Scope, Policy Preservation, and Verification

## Closed-world implementation/publication scope

After activation, the complete authorized implementation diff is exactly:

1. `core/brain/providers/__init__.py`;
2. `core/brain/providers/ollama.py`;
3. `tests/unit/brain/providers/test_ollama.py`;
4. `tests/unit/core_platform/test_stage8_import_boundaries.py`.

No fifth path is authorized. The sole permitted change in path 4 is adding
`core/brain/providers/ollama.py` to the exact approved-location set for the
top-level `httpx` dependency.

## Dependency decision

- exact permitted dependency: `httpx`;
- exact permitted importing module/path:
  `core/brain/providers/ollama.py`;
- pinned version: `httpx==0.28.1`;
- new dependency: `NO`;
- dependency/requirements file change: prohibited;
- provider SDK: prohibited; and
- repository-wide, Brain-wide, Core-wide, or Domain-wide `httpx` permission:
  prohibited.

The adapter may retain its constructor-injected `httpx.AsyncClient`. It must
not be rewritten merely to conceal the legitimate dependency edge.

## Stage 8 policy preservation

The Stage 8 test remains fail-closed and path-specific. Implementation must
retain every previous allowlist entry and restriction, Core/Domain boundary,
provider-SDK prohibition, reverse-dependency protection, and failure behavior
for unauthorized third-party imports. A wildcard, directory prefix, glob,
default-allow rule, or generic `httpx` permission is prohibited.

This change represents no architecture, runtime, capability, network,
production, or Brain-integration expansion. It aligns the existing dependency
audit with the already-approved first Brain provider adapter.

## Required verification after implementation

Rerun and require zero unresolved failures across:

- focused Ollama adapter tests;
- Stage 0.3 inference contracts;
- Stage 0.5 provider abstraction;
- Stage 8 gates;
- Stage 9 gates;
- Core and relevant Domain regressions;
- the full repository suite;
- compile/static checks;
- dependency/import and prohibited-source audits;
- `git diff --check`; and
- exact four-path closed-world diff audit.

No live inference, staging access, or runtime/VPS mutation is authorized for
verification.

## Rollback

Rollback is repository-only revert/removal of the adapter/test changes,
including the one exact Stage 8 allowlist entry. No database, staging runtime,
model, or VPS rollback applies.
