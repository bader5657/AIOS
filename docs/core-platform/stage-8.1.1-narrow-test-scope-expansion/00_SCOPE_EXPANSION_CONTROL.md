# Stage 8.1.1 Narrow Test Scope Expansion

| Control | Value |
|---|---|
| Governing approval | Active Stage 8.1.1 Telegram Ingestion Integration Approval |
| Expansion baseline | `5fcb460c0cbe50462b4616c22e44c52618b6a711` |
| Expansion class | Test-only closed-world correction |
| Runtime effect | **NONE** |
| Additional authorized path | `tests/unit/core_platform/test_telegram_input_boundary.py` |

The implementation attempt proved that the existing boundary test still
requires `core.app.request_context` to be imported by the Telegram Adapter.
That assertion is obsolete under the Active Stage 8.1.1 authority, which makes
Universal Ingestion the sole RequestContext constructor and requires the
adapter-side RequestContext import and construction to be removed.

This record authorizes exactly one additional test path. It does not alter the
approved integration behavior, runtime scope, or Stage 8 boundary.
