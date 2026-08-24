# Immutable Path, Attempt Lineage, and Execution Controls

## Evidence disposition

The existing `00_CONTROLLED_SYNTHETIC_EXECUTION.json` is retained as immutable
historical evidence of a blocked attempt. It must not be deleted, overwritten,
truncated, edited, replaced, renamed, or reused.

The existing `01_PRIVILEGED_NETWORK_PREFLIGHT.txt` is retained unchanged as
the approved privileged read-only network-preflight evidence. It may be
referenced by the next attempt but must not be modified.

The sole newly authorized final execution target is:

`/opt/aios/runtime/intelligence/staging/stage-0.20-evidence/02_CONTROLLED_SYNTHETIC_EXECUTION.json`

Immediately before any future Stage 0.20 operational preflight or inference,
the operator must establish that this exact path does not exist. If it exists,
the attempt must stop before inference and return to governance. No alternate
path may be selected automatically.

The future harness must create the target exactly once with exclusive-create,
fail-if-exists semantics. Ordinary overwrite mode is prohibited.

## Attempt lineage

| Attempt | Result | Inference count |
|---|---|---|
| `0` | blocked because privileged network inspection was indeterminate | `0` |
| `1` | blocked because the authorized evidence target already existed | `0` |
| next authorized attempt | use immutable execution record `02` | at most the one previously approved request |

Cumulative live inference count before the next attempt is `0`. Neither
blocked attempt consumed the one-request authority: projector, mapper, Brain
boundary, provider, and `POST /api/chat` counts were all zero.

## Unchanged execution controls

Only the evidence path changes. The next attempt remains limited to exactly
one request with the fixed synthetic text, correlation and mapper UUIDs,
eligible prebuilt CoreRouteResult, exact provenance, repository projector and
mapper, Stage 0.19 composition, Stage 0.18 schema binding, and isolated
Ollama/Qwen runtime. Retry, fallback, a second request, runtime mutation,
production activation, and Level B activation remain prohibited.

The next attempt must start from the beginning. Before the request it must
freshly verify source, AIOS, PostgreSQL, Telegram, host RAM, swap, load, disk,
staging container, naturally unloaded model state, and current network and
listener state. The approved privileged firewall/NAT evidence may be
referenced, but it does not replace those fresh gates.
