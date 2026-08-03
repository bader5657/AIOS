# Core Platform Stage 2.1.1 Request Context Comparison

## Record

| Field | Value |
|---|---|
| Execution Plan position | Stage 2 — Main Step 2.1 — Sub Step 2.1.1 |
| Comparison baseline | `f4d2a021b98a67033467a6d3b990fea5baa97842` (`main`) |
| Blueprint evidence | Official pipeline and dependency direction |
| Repository evidence | `config/request-context.schema.json` and `core/app/request_context.py` |
| Review date | `2026-08-03` |
| Result | **PASS by explicit stop — component contract not approved** |

This record compares the Blueprint role of Request Context with the current
configuration artifact and runtime dataclass. It does not resolve fields,
approve a component contract, or change implementation.

## Blueprint Role

The Blueprint establishes only these Request Context facts:

1. Request Context is a named step in the official pipeline after Universal
   Ingestion and before Asset Pipeline.
2. Request Context is listed as a completed capability.
3. AIOS Brain may consume Request Context at the later downstream boundary.

The Blueprint does not publish Request Context fields, nesting, required or
optional status, types, identifiers, validation, normalization, lifecycle
transitions, routing ownership, timestamp semantics, or serialization rules.
The completed label therefore cannot establish those details by itself.

## Configuration Artifact Review

`config/request-context.schema.json` is syntactically valid JSON. Its content
is an example-shaped JSON object with 11 top-level keys:

```text
schema_version, request_id, conversation_id, parent_request_id, source, user,
input, context, routing, processing, timestamps
```

Despite its filename, the artifact is not an executable JSON Schema: it has no
`$schema`, `type`, `properties`, `required`, or validation constraints. The
current values demonstrate a proposed shape but do not define required fields,
accepted types, nullability, allowed values, or validation behavior.

## Runtime Comparison

The current `RequestContext` dataclass has seven flat fields:

```text
source, user_id, chat_id, message_id, username, text, received_at
```

The following matrix records structural comparison only. A “candidate
relationship” is not a field decision or approved mapping.

| Runtime evidence | Configuration evidence | Comparison finding |
|---|---|---|
| `source` | `source.channel`; `source.gateway` | Flat value versus nested object; channel is a possible conceptual relationship, but gateway has no runtime field |
| `user_id` | `source.user_id` | Same label concept at different nesting and with different example/runtime types |
| `chat_id` | `source.chat_id` | Same label concept at different nesting and with different example/runtime types |
| `message_id` | `source.message_id`; top-level `request_id` | Nested message field is related; no authority equates message identity with request identity |
| `username` | `user.display_name` | Possible user-label relationship, but username and display name are not proven equivalent |
| `text` | `input.raw_text`; `input.normalized_text` | Runtime has one text value; configuration proposes two distinct text roles without published semantics |
| `received_at` | `timestamps.received_at` | Related timestamp label at different nesting; serialization exists, but required format is not configured |

Configuration fields with no direct runtime field are:

- `schema_version`, `request_id`, `conversation_id`, and
  `parent_request_id`;
- `user.language` and `user.timezone`;
- `input.message_type`, `input.attachments`, and `input.links`;
- every field beneath `context`;
- every field beneath `routing`;
- every field beneath `processing`; and
- `timestamps.processed_at`.

The runtime fields are serialized by `to_dict()` as a flat object, with
`received_at` converted to ISO format. `from_telegram()` fixes `source` to
`telegram`, preserves the supplied Telegram identity/text values, and creates
a timezone-aware UTC receipt timestamp. None of those runtime observations
proves the larger configuration shape to be authoritative.

## Boundary Review

The configuration artifact includes selected mode, selected specialist,
clarification, approval, and memory-candidate concepts. The Blueprint places
AIOS Brain, Specialist Router, specialists, and Memory downstream of Core
Platform. Merely carrying data does not necessarily implement those later
capabilities, but ownership and semantics are not established. This Sub Step
therefore does not accept, reject, rename, or implement those fields.

The comparison confirms a material dataclass/configuration gap while
preserving the official pipeline position. It does not show that either the
runtime dataclass or the configuration example is the complete component
contract.

## Authority Finding and Explicit Stop

No approved evidence defines the authoritative Request Context field set or
resolves the structural and later-phase ambiguities above. Approving the
configuration example as a contract, selecting mappings, or defining missing
semantics would require assumptions prohibited by the frozen plan.

Accordingly, the required evidence outcome for Sub Step 2.1.1 is an **explicit
stop**, not an approved component contract. Advancement into Sub Step 2.1.2
requires Project Owner direction sufficient to review and resolve the fields
without inventing behavior. This finding creates no authority and does not
pre-decide the field-by-field record reserved for Sub Step 2.1.2.

## Validation Evidence

JSON syntax validation:

```text
python3 -m json.tool config/request-context.schema.json
```

Result: **PASS**.

Read-only field inventory observed 11 configuration top-level keys and seven
runtime dataclass fields. The accepted repository-root test command and the
retained Core Platform focused suite are run as regression checks; neither is
represented as schema conformance, which belongs to Sub Step 2.2.2.

Observed regression results:

```text
Core Platform focused suite: Ran 10 tests in 0.007s — OK
Official repository-root suite: Ran 212 tests in 0.033s — OK
```

## Scope Boundaries and Result

The only created artifact is this comparison and explicit-stop record. No
schema, runtime, test, dependency, or configuration behavior is changed. No
Blueprint, Roadmap, Governance, `VERSION`, Domain Foundation, Execution Plan,
freeze document, milestone, source, deployment, service, workflow, or
architecture file is changed.

**Sub Step 2.1.1 result: PASS by explicit stop**

Main Step 2.1 remains in progress and cannot advance under the unresolved
authority finding. The next frozen-plan position is Stage 2, Main Step 2.1,
Sub Step 2.1.2, but it is not started by this record.
