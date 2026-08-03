# Core Platform Stage 2.1.2 Request Context Field Decisions

## Record

| Field | Value |
|---|---|
| Execution Plan position | Stage 2 — Main Step 2.1 — Sub Step 2.1.2 |
| Decision baseline | `d26f3a9b086950f6b8ce383cd778c87f9186c384` (`main`) |
| Input evidence | Sub Step 2.1.1 comparison, current configuration example, and current runtime dataclass |
| Decision date | `2026-08-03` |
| Result | **PASS — minimal current-runtime field contract confirmed** |

This record resolves the current configuration/runtime field gap without
adding behavior. It uses the Sub Step 2.1.1 findings as evidence only and does
not convert that report into authority.

## Decision Rules

The narrowest evidence-supported contract is selected:

1. Existing runtime fields and behavior are confirmed because they are current
   executable repository evidence for the Blueprint-named Request Context.
2. A similar label in the configuration example does not authorize a rename,
   nesting change, type conversion, generated value, or new semantic.
3. Configuration-only fields are accounted for but remain reserved and are
   not approved for runtime alignment until their behavior and ownership are
   established by an applicable later contract.
4. Reserved routing, specialist, clarification, memory, and other downstream
   values do not authorize Brain, router, specialist, or Memory behavior.
5. The current Telegram factory signature and behavior remain preserved.

“Reserved” means present in the configuration example but excluded from the
active runtime field contract. It does not mean silently implemented,
deprecated, deleted, or approved for a later phase.

## Confirmed Runtime Field Contract

| Runtime field | Confirmed type/behavior | Decision |
|---|---|---|
| `source` | Required `str`; `from_telegram()` supplies `telegram` | RETAIN |
| `user_id` | Required `int`; supplied unchanged by Telegram boundary | RETAIN |
| `chat_id` | Required `int`; supplied unchanged by Telegram boundary | RETAIN |
| `message_id` | Required `int`; supplied unchanged by Telegram boundary | RETAIN |
| `username` | Required `str`; supplied unchanged by Telegram boundary | RETAIN |
| `text` | Required `str`; supplied unchanged by Telegram boundary | RETAIN |
| `received_at` | Required `datetime`; Telegram factory creates timezone-aware UTC value | RETAIN |

`to_dict()` remains a flat serialization of these seven fields and converts
only `received_at` to its ISO string. This Sub Step approves no validation,
normalization, ID generation, alternate factory, lifecycle transition, nested
serialization, or additional default.

## Configuration Field Decisions

### Identity and relationship fields

| Configuration field | Current evidence | Decision |
|---|---|---|
| `schema_version` | Example value only; no runtime/schema-version behavior | RESERVED — do not add |
| `request_id` | Example pattern only; no generator or identity rule | RESERVED — do not add or derive from `message_id` |
| `conversation_id` | Empty example; no active Conversation contract in this scope | RESERVED — do not add |
| `parent_request_id` | Nullable example; no parent relationship semantics | RESERVED — do not add |

### Source and user fields

| Configuration field | Current evidence | Decision |
|---|---|---|
| `source.channel` | Conceptually overlaps runtime `source` | RETAIN runtime `source`; do not introduce nesting |
| `source.gateway` | Example value only | RESERVED — do not add |
| `source.user_id` | Conceptually overlaps runtime `user_id`, but example type differs | RETAIN runtime `user_id`; do not introduce nesting or conversion |
| `source.chat_id` | Conceptually overlaps runtime `chat_id`, but example type differs | RETAIN runtime `chat_id`; do not introduce nesting or conversion |
| `source.message_id` | Conceptually overlaps runtime `message_id`, but example type differs | RETAIN runtime `message_id`; do not introduce nesting or conversion |
| `user.display_name` | Possible but unproven relationship to runtime `username` | RETAIN runtime `username`; do not rename |
| `user.language` | Example default only | RESERVED — do not add |
| `user.timezone` | Example default only | RESERVED — do not add |

### Input fields

| Configuration field | Current evidence | Decision |
|---|---|---|
| `input.message_type` | Classification exists elsewhere, but Request Context ownership is not established | RESERVED — do not add |
| `input.raw_text` | Conceptually overlaps runtime `text` | RETAIN runtime `text`; do not introduce nesting |
| `input.normalized_text` | Empty example; no normalization contract | RESERVED — do not add or normalize |
| `input.attachments` | Empty example; attachment contract belongs to later ingestion work | RESERVED — do not add |
| `input.links` | Empty example; Web/YouTube handling belongs to later ingestion work | RESERVED — do not add |

### Context fields

| Configuration field | Current evidence | Decision |
|---|---|---|
| `context.current_priority` | Example business priority only | RESERVED — do not add business-priority behavior |
| `context.conversation_summary` | Empty example; no summary ownership | RESERVED — do not add |
| `context.related_entity_type` | Empty example; no entity-link contract | RESERVED — do not add |
| `context.related_entity_id` | Empty example; no entity-link contract | RESERVED — do not add |

### Routing fields

| Configuration field | Current evidence | Decision |
|---|---|---|
| `routing.selected_mode` | Empty example; mode selection is downstream behavior | RESERVED — do not add |
| `routing.selected_specialist` | Empty example; Specialist Router is outside Core Platform | RESERVED — do not add |
| `routing.confidence` | Example value only; no confidence contract | RESERVED — do not add |
| `routing.requires_clarification` | Example value only; no Request Context ownership | RESERVED — do not add |
| `routing.clarification_question` | Empty example; no question-generation contract | RESERVED — do not add |

### Processing fields

| Configuration field | Current evidence | Decision |
|---|---|---|
| `processing.status` | Example `received`; lifecycle ownership is decided in Stage 3 | RESERVED — do not add transitions or status |
| `processing.requires_confirmation` | Example value only; no confirmation contract | RESERVED — do not add |
| `processing.approved` | Example value only; no approval workflow contract | RESERVED — do not add |
| `processing.memory_candidate` | Example value only; Memory is downstream | RESERVED — do not add |

### Timestamp fields

| Configuration field | Current evidence | Decision |
|---|---|---|
| `timestamps.received_at` | Conceptually overlaps runtime `received_at` | RETAIN runtime `received_at`; keep flat, timezone-aware UTC creation and ISO serialization |
| `timestamps.processed_at` | Empty example; no processing completion ownership | RESERVED — do not add |

## Configuration Artifact Disposition

`config/request-context.schema.json` remains unchanged configuration evidence,
not an executable conformance schema and not the active runtime field contract.
This decision neither deletes nor approves its reserved fields. Any future
change to that artifact must be separately within an authorized Sub Step.

For the active Stage 2 contract, the current seven-field runtime model is the
only approved implementation surface. Consequently, Sub Step 2.2.1 may
preserve it but may not add the reserved configuration fields or change its
Telegram compatibility under this decision record.

## Authority Findings

No new authority gap was discovered beyond the findings already evidenced by
Sub Step 2.1.1. This record resolves those findings conservatively by excluding
unsupported fields from the active runtime contract; it does not resolve them
by inventing semantics or by modifying repository authority.

Later work requiring conversation relationships, links, context enrichment,
routing, processing lifecycle, or processed timestamps must use the applicable
frozen-plan contract step. This is a scope boundary, not a Stage stop and not a
new authority.

## Validation Plan

Validation for this decision record consists of:

- JSON syntax validation of the unchanged configuration example;
- a read-only inventory confirming all 32 leaf configuration fields and all
  seven runtime fields are accounted for;
- the retained Core Platform focused regression suite; and
- the accepted repository-root Domain Foundation regression command.

These checks validate evidence completeness and repository consistency. They
do not claim runtime/schema conformance, which belongs to Sub Step 2.2.2.

Observed results:

```text
JSON syntax: PASS
Configuration leaf fields accounted for: 32
Runtime fields accounted for: 7
Core Platform focused suite: Ran 10 tests in 0.011s — OK
Official repository-root suite: Ran 212 tests in 0.050s — OK
```

## Scope Boundaries and Result

The only created artifact is this field-by-field decision record. No existing
schema, runtime, test, configuration, dependency, or behavior is changed. No
Blueprint, Roadmap, Governance, `VERSION`, Domain Foundation, Execution Plan,
freeze document, milestone, source, deployment, service, workflow, authority,
or architecture artifact is changed.

**Sub Step 2.1.2 result: PASS**

Main Step 2.1 is complete. The next frozen-plan position is Stage 2, Main Step
2.2, Sub Step 2.2.1. That Sub Step is not started by this record.
