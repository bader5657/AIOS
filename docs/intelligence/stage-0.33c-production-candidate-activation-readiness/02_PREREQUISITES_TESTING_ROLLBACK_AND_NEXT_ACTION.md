# Prerequisites, Testing, Rollback, and Next Action

## Narrowest viable future activation

The first viable activation is **candidate-create only**, manually/operator
initiated, through one newly implemented controlled entrypoint, for one exact
Project-Owner-approved real-business source at a time. It must not be a general
runtime switch, Telegram workflow, Universal Ingestion write-through, agent
write path, confirmation path, or posting path.

This is a design recommendation for the next implementation package, not an
authority. A synthetic production candidate is prohibited unless later separate
governance establishes a business-valid test-data lifecycle; the default first
write therefore requires real-data eligibility and explicit Owner approval.

## Required implementation work

Before activation governance can be ready, a separately reviewed implementation
package must provide:

1. one controlled operator entrypoint exposing only
   `create_review_candidate_from_ingestion`;
2. an authenticated, immutable source for the canonical operator UUIDv4—never
   caller-selected arbitrary actor text;
3. exact retained-manifest and approved trusted-facts input binding;
4. activation-safe credential acquisition without printing, copying, rotating,
   or broadly exposing the candidate database password;
5. explicit disabled-by-default configuration with no Telegram, ingestion,
   background, HTTP, or agent registration;
6. bounded execution evidence and deterministic failure mapping; and
7. an operational off-switch that removes the caller/wiring or disables the
   entrypoint without database `DOWN`, schema weakening, privilege broadening,
   or evidence rewriting.

This package does not decide a permanent user interface. If the project requires
Telegram, automatic ingestion, or an HTTP endpoint, that is a later architecture
and trust-boundary decision.

## Required test and validation evidence

Activation readiness requires reviewable evidence for:

- focused unit tests for exact input, canonical actor authorization, and all
  fail-closed branches;
- zero-operational-capability tests proving rejected input cannot construct a
  repository, load credentials, connect, persist, confirm, post, move inventory,
  or mutate stock;
- candidate repository tests for atomic receipt/item creation, `NEEDS_REVIEW`
  state, creator immutability, transaction rollback, and error sanitization;
- duplicate and concurrent-source tests against the active-source uniqueness
  contract;
- actor-provenance propagation tests showing the single approved operator is
  retained exactly and no alternate actor reaches persistence;
- confirmation/posting non-escalation tests, including no posting credential or
  repository construction;
- isolated PostgreSQL 17 validation of the exact runtime role, transaction,
  expected rows, forbidden side effects, rollback paths, and R03/R04/V05
  privilege invariants; and
- static runtime wiring tests proving Telegram, Universal Ingestion, background
  tasks, agents, and public endpoints remain disconnected.

No disposable PostgreSQL was launched in this readiness review. Existing
disposable Stage 0.32/0.33A tests and Stage V2 production read-only evidence are
inputs, not substitutes for validating the future controlled entrypoint.

## First-write governance contract

Any later first-write authority must be a separate, independently reviewed,
single-use or equivalently bounded authority fixed before launch. It must freeze:

- authority and attempt count, exact executable/entrypoint, target environment,
  runtime role, PostgreSQL role, and transaction contract;
- exact retained source, payload eligibility decision, canonical actor identity,
  and Project Owner approval, without embedding secrets or unrestricted data;
- expected creation of exactly one receipt plus the approved item count, all in
  `NEEDS_REVIEW`;
- forbidden confirmation, posting, inventory movement, stock mutation, other
  table writes, privilege changes, service changes, and automatic retry;
- pre-write identity/configuration/health gates, post-write bounded verification,
  failure/rollback behavior, and operational deactivation; and
- durable evidence before advancing.

Required bounded evidence includes request/correlation identity, canonical actor
reference or approved bounded cryptographic representation, candidate identity,
source-manifest identity/hash, transaction outcome, per-table affected counts,
candidate/confirmation/posting state, inventory/stock non-effects, and
runtime/service health. It must exclude credentials and unrestricted business
payloads.

Future executors retain the existing evidence debt: status/PASS-only events are
insufficient. Actual semantic validator payloads or approved bounded
cryptographic equivalents must be durably written, flushed/fsynced, and bound to
the execution before complete proof is claimed.

## Rollback and deactivation

Before commit, failure means rollback of the same candidate-create transaction
and no automatic retry. After a successful commit, the created business record
is not erased or rewritten as technical rollback. The capability is deactivated
operationally by disabling/removing the controlled caller while retaining the
schema, creator provenance, privileges, and evidence. Any business rejection or
cancellation follows separately governed domain behavior.

No migration `DOWN`, column removal, privilege weakening, historical evidence
rewrite, `runtime.env` mutation, or service restart is an acceptable rollback in
this package.

## Decision and next action

Readiness is classified exactly:

> **B. IMPLEMENTATION_WORK_REQUIRED_BEFORE_ACTIVATION**

Blocking prerequisites are the absent controlled operator entrypoint, unresolved
operator identity source for production use, runtime-secret/activation-safety
closure, exact real-business input approval, and first-write evidence/execution
contract. No broad architecture decision is needed for the recommended manual
candidate-create-only first step; broader interfaces remain deferred decisions.

The next official action is a fresh independent review of this readiness
package, followed—only if merged—by a separate Stage 0.33C implementation
governance package. Production candidate activation remains **NOT AUTHORIZED**.
