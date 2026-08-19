# Exact Scope, Stop Rules, and Prohibitions

The only authorized implementation path is:

`tests/unit/core_platform/test_stage8_import_boundaries.py`

Runtime files authorized: `NONE`. No second test file is authorized. If another
path is required, Stage 8.3.1 must stop for explicit scope expansion.

If the audit proves an actual prohibited runtime edge, work must stop with:

`STAGE 8.3.1 RUNTIME CORRECTION APPROVAL REQUIRED`

The report must identify the source file, imported target, violated authority,
and smallest correction scope. Runtime must not be patched under this approval.
Defects in the static test itself may be corrected only in the authorized test
file without reinterpreting architecture.

Prohibited scope includes package moves, new interfaces or abstractions,
dependency inversion, Telegram DTO migration, Psycopg/ORM replacement, Brain,
Memory, Specialist Router, business features, broker/queue, LLM/Ollama,
deployment, retry/dedup redesign, and Stage 8.4.1 failure work.
