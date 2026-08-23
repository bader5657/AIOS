# Preflight, Postflight, Privacy, and Deferred Debt

## Mandatory immediate preflight

Before the sole invocation require and record:

- exact clean temporary source SHA and all module-path isolation checks;
- existing venv compatibility and `httpx==0.28.1`;
- exact approved-ID equality gate;
- production source unchanged at its recorded SHA;
- AIOS active/running with `NRestarts=0`;
- PostgreSQL healthy and exactly one Telegram poller;
- staging Ollama healthy, private-only, and within unchanged limits;
- model-loaded state observed read-only, preferably unloaded but never forced;
- stable swap, responsive host, and safe staging disk; and
- no public/host Ollama exposure or configuration drift.

Any failed or indeterminate mandatory item stops before inference.

## Mandatory postflight

Whether the request returns success/failure, raises, or is cancelled, verify
where possible:

- AIOS active with `NRestarts=0`;
- PostgreSQL healthy and exactly one Telegram poller;
- responsive host and stable swap;
- Ollama within the 3 GiB and 1-vCPU ceilings;
- staging disk safe;
- production and Stage 0.13 source unchanged; and
- no network, firewall, runtime, configuration, service, container, database,
  or production mutation.

## Privacy and state

Only synthetic content is used. Instruction, data, raw response, and
structured output are not durably logged or persisted. The operator terminal
may display bounded synthetic result evidence; durable evidence retains only
bounded metadata, counts, IDs, status/failure, timing, validation, identity,
and safety state. Memory, session, Specialist, and business actions are absent.

## Preserved debts

The temporary resolver/validator does not establish production schema binding.
The temporary object assembly does not establish a production composition
root. The Core-to-Brain mapper remains unimplemented. No `CoreRouteResult`,
`EventEnvelope`, Core change/wiring, production inference, or production data
is authorized.

Preserve Stage 0.8, Stage 0.10, and future Stage 0.13 temporary sources until
separate cleanup authority is granted.
