# Exact Edge, Default-Deny Boundary, and Verification

## Sole exception

Permit only this source-to-target edge:

`core/brain/staging_composition.py → httpx`

The intended use is `httpx.AsyncClient` construction and lifecycle ownership
inside the explicit Brain-local isolated staging composition. No wildcard
`core/brain/* → httpx`, package-wide permission, arbitrary staging-module
permission, or unrelated third-party import is authorized.

## Boundary meaning and retained protections

The composition owns exactly one AsyncClient and injects it into the already
approved OllamaInferenceProvider. The exception permits object construction
and deterministic cleanup only. It does not authorize an HTTP request,
endpoint probe, health check, inference, model lifecycle action, retry,
fallback, or runtime mutation.

Default-deny remains intact for AIOSCore, Universal Ingestion, Domain,
unrelated Brain modules, and every other repository path. The implementation
must retain its caller-supplied OllamaProviderConfig, repository
`resolve_schema` and `validate_schema`, single provider/invoker/receiver/mapper
graph, external projector, narrow exposed mapper and async Brain boundary, and
deterministic cleanup. Production startup and Level B remain unchanged.

No requirements, lockfile, installation, SDK, or dependency-file change is
authorized.

## Required verification after activation

Resume the same Stage 0.19 worktree and modify only
`tests/unit/core_platform/test_stage8_import_boundaries.py` to represent the
exact approved edge. Then rerun the focused Stage 0.19, Stage 0.18 through
Stage 0.3, Core, Domain, Stage 8, Stage 9, and full repository suites;
compile/static, dependency/import, and prohibited-source audits;
`git diff --check`; and the exact three-path closed-world audit. Zero unresolved
failures are required. No live inference is authorized.

Rollback reverts the two Stage 0.19 implementation paths and the exact Stage 8
policy exception. No runtime or VPS rollback is required.
