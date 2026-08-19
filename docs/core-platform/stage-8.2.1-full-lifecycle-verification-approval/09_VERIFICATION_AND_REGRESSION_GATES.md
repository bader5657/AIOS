# Verification and Regression Gates

Focused evidence must prove all thirty approved points: action owners; exact
RequestContext placement; single Asset Pipeline execution; Store-before-Metadata;
Metadata-before-Manifest; Manifest-before-Registry; real Registry commit and
independent visibility; Process and Route gates; same-envelope identity; one
Core call; `AIOS_BRAIN_BOUNDARY` readiness; zero Brain calls; Adapter-owned
Respond after Route; preserved `register_handoff_ready` gate; no ownership
leakage; no retry/deduplication/cross-component transaction; representative
failure stops; upstream preservation; and zero runtime changes.

The unchanged regression matrix includes Stage 8.1.1–8.1.4, RequestContext,
Asset Pipeline, Metadata/Manifest, Registry, Event Engine, AIOS Core, Core
Platform, full Domain, compile/static, dependency, prohibited-source, and
`git diff --check` audits. Known capability-matrix environment/test-isolation
subfailures remain separately classified only if their fingerprint is unchanged.

All mandatory focused cases must run with zero skips.
