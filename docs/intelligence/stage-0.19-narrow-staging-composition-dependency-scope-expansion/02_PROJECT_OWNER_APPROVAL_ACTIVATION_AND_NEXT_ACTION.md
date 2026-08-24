# Project Owner Approval, Activation, and Next Action

## Project Owner approval

I, as Project Owner, approve the narrow Stage 0.19 dependency-policy scope
expansion adding only:

`tests/unit/core_platform/test_stage8_import_boundaries.py`

to authorize exactly:

`core/brain/staging_composition.py → httpx`

This exception exists solely so the Brain-local isolated staging composition
can own one httpx.AsyncClient and inject it into the already-approved
OllamaInferenceProvider.

It does not authorize construction-time network access, health checks,
inference, new dependencies, production startup integration, Level B
activation, or broader third-party import permissions.

## Publication and activation

The allowed diff for this approval is this governance package only.
Publication requires a normal clean, mergeable PR into `main`, without force or
history rewrite. The two existing uncommitted implementation paths must not be
staged or modified by this governance publication.

After merge and synchronized-main audit, authority activates as:

`INTELLIGENCE STAGE 0.19 NARROW STAGING COMPOSITION DEPENDENCY SCOPE EXPANSION APPROVED — READY TO RESUME IMPLEMENTATION`

Activation modifies no implementation, runtime, or VPS state.

## Next official action

Resume Stage 0.19 implementation, update only the exact Stage 8 policy test,
rerun the complete approved non-live verification matrix, and publish the
three-path implementation only if every gate passes.
