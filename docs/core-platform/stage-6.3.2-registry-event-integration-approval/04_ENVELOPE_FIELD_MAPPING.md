# EventEnvelope Field Mapping

Universal Ingestion constructs one envelope only after Registry success and
only when `domain_event` is present.

| Active field | Exact source |
|---|---|
| `event` | Exact caller-supplied `domain_event` object |
| `event_id` | Read-only mirror of `domain_event.id` |
| `event_name` | Read-only mirror of `domain_event.event_name` |
| `occurred_at` | Read-only mirror of `domain_event.occurred_at` |
| `aggregate_id` | `None`; no approved integration value |
| `correlation_id` | `None`; no approved integration value |
| `causation_id` | `None`; no approved integration value |
| `schema_version` | Exact explicit caller input `event_schema_version` |

The additional backward-compatible keyword input is:

```python
event_schema_version: int | None = None
```

When `domain_event` is supplied, a valid positive non-boolean schema version is
required. Absence/invalidity is a caller contract error; no value is guessed.
Envelope construction relies on the active Domain Foundation constructor and
does not duplicate domain semantic validation.
