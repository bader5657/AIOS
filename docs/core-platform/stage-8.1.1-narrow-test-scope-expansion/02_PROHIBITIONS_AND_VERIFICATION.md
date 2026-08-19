# Prohibitions and Verification

This expansion authorizes no change to Universal Ingestion, RequestContext,
Asset Pipeline, Telegram Storage, Registry, Event Engine, AIOS Core, Domain
Foundation, dependencies, configuration, migrations, Blueprint, Roadmap, or
architecture. Runtime semantics and the Active approval remain unchanged.

It authorizes no retry, media-group state, webhook, network execution, command
redesign, business behavior, broad Telegram SDK refactor, infrastructure, or
Stage 8.2.1 work.

Before implementation publication, all Stage 8.1.1 authority-relevant gates
must pass, including the focused integration test, reconciled Telegram boundary
test, relevant component regressions, compile/static checks, dependency and
prohibited-source audits, `git diff --check`, and the exact three-path
closed-world diff. Proven pre-existing unrelated environment/test-isolation
failures must be reported separately and must not be represented as green.
