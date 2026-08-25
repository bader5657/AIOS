# AIOS Intelligence Stage 0.23 — First Real-Text Session Execution Authority

| Control | Authorized value |
|---|---|
| Authority baseline | `345284460b1e547feddb21b6995c28956616f880` |
| Activation classification | `SESSION_BOUND_LEVEL_B_REAL_TEXT_V1` |
| Candidate source | direct operator-confirmed plain text |
| Candidate | `berapa stok bahan sekarang?` |
| Candidate modification | `PROHIBITED` |
| Data class | `real_text` |
| Request/session limit | exactly one request in exactly one separately authorized session |
| Execution during publication | `PROHIBITED` |
| Level C | `PROHIBITED` |

This package grants first real-text execution authority only after publication,
merge into `main`, clean-main verification, and a fresh successful preflight.
It does not execute inference, create the future session journal, or invoke the
future harness during authority publication.

The exact operator candidate is frozen byte-for-byte. It must not be rewritten,
translated, capitalized, punctuated, substituted, contextualized, or enriched.
No other text, second request, retry, fallback, or second session is authorized.

The candidate asks about current material stock, but this authority grants no
PostgreSQL, Registry, inventory, business-record, Universal Ingestion, or
external-context lookup. No stock quantity may be fabricated. Model-content
quality is evaluated separately from infrastructure validity; only the
authorized minimized text may reach Brain.

The authority is inference-only. It grants no stock update, order creation,
product change, transaction write, workflow action, or other business action.
