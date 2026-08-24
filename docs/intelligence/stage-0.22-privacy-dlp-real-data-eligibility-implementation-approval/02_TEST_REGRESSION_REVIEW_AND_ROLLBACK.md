# Test, Regression, Reviewer Audit, and Rollback

The focused test module must cover the 63 minimum cases authorized by the
Project Owner, including:

- explicit authorization and inability to infer authority from content;
- exact `{"text": ...}` shape, unsupported modalities, prohibited metadata,
  and unsupported structures;
- empty input and exact Stage 0.17 character/UTF-8 bounds;
- bearer/authorization tokens, private keys, password/API-key/bot/session and
  cookie credentials;
- PIN, OTP, CVV/CVC, email, telephone, customer identifier, and supported
  deterministic address detection;
- Telegram metadata rejection and ordinary minimized business prose;
- exact fresh allowed output, immutable result, input preservation, and no
  rejected-content leakage;
- standard-library-only imports and absence of database, Registry, network,
  filesystem, environment, config, provider, Brain, mapper, logging,
  persistence, and enrichment edges; and
- rejection before mapper/Brain/provider activity, with zero downstream calls.

Additional durable tests inside the single authorized test path are allowed.

## Regression gates

The later implementation task must run focused Stage 0.22 tests; Stage 0.17
projection tests; relevant Stage 0.21 governance/static gates; Stage 0.18
schema binding; Stage 0.16 wiring; Stage 0.15 integration; Stage 0.14 mapper;
Stage 0.12 receiver; Stage 0.11 BrainInput; Stage 0.9 invoker; Stage 0.7 adapter
mocks; Stage 0.3 contracts; Core, Domain, Stage 8, and Stage 9 regressions; the
full suite; compile/static checks; dependency/import and prohibited-source
audits; `git diff --check`; and the exact two-path closed-world audit.

No live inference or real-data activation is part of verification.

Immediately before commit, `git diff --name-only` must contain exactly the two
authorized implementation paths. Reviewer audit must reject raw secret or
content leakage, redaction-and-continue, mutable authoritative state,
conflicting bounds, new dependencies, provider/Brain coupling, DB/Registry or
environment/config access, Telegram metadata acceptance, automatic business
enrichment, runtime activation, and Universal Ingestion wiring.

Fixes are limited to the two paths. A required third path, third-party package,
architecture change, or wiring change triggers
`INTELLIGENCE STAGE 0.22 SCOPE EXPANSION REQUIRED`.

Rollback is repository-only removal or reversion of exactly the two future
implementation additions before activation. There is no runtime, schema,
database, migration, dependency, configuration, or service rollback because
none is authorized.
