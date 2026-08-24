# Input, Privacy, Journal, and Safety Contract

The future candidate must be genuinely typed or confirmed by the operator,
plain text, low-risk, operational or business-relevant, within Stage 0.22
bounds, and free of secrets, credentials, financial authentication data,
deterministic PII, customer/supplier identifiers, Telegram metadata, file
content, and database/Registry-derived context.

Manual business-like prose may qualify only when directly supplied and allowed
by Stage 0.22. Business records, enrichment, lookups, hydration, actions, and
state writes remain prohibited. `PII_REQUIRES_EXPLICIT_SCOPE` has no override.
Secret or credential findings deny the whole request without
redaction-and-continue.

## Journal and retention

Reuse the append-only, immutable Stage 0.21 session model with
`data_class = real_text`. Record only:

- session/source/runtime identity and explicit operator authority state;
- eligibility classification and reason code;
- raw input code-point and UTF-8 byte lengths;
- raw input SHA-256 and allowed minimized-data SHA-256;
- correlation ID and, only after mapping, Brain request ID;
- independent lifecycle, projection, eligibility, admission, mapper, Brain,
  provider, HTTP, retry, and fallback counters;
- bounded provider/model, latency, schema, resource, cleanup, and final-state
  metadata.

Raw input, rejected content, detected substring, and raw model output must not
appear in the journal, logs, governance evidence, or debug output. Raw output
is displayed transiently to the operator only. No output hash is retained.
Input hashes are pseudonymous evidence and must never be represented as
anonymization.

The only persistence is governed metadata in the session journal. Memory,
business persistence, semantic input/output persistence, and Specialist or
business-action routing are prohibited.

## Safety gates

Reuse the full Stage 0.21 preflight and per-request safety controls. In
addition, verify the identity of `core.ingestion.real_data_eligibility`, its
clean-checkout source, real-text authority and data classification, explicit
operator state, retention policy, and corrected counter taxonomy.

The authoritative interpreter remains `/opt/aios/runtime/venv/bin/python`,
Python `3.12.3`, httpx `0.28.1`, with repository root
`/home/aiosadmin/AIOS`. Reuse accepted privileged evidence and perform fresh
lightweight network-drift checks. No new sudo inspection is implied without
separate authority.

Before eligibility, require clean source/interpreter/runtime identity, active
authority, operator confirmation, stable AIOS and Telegram poller, healthy
PostgreSQL/container, safe resources, isolated network, and request counter
zero. Denial does not admit a request or call mapper, Brain, or provider.
