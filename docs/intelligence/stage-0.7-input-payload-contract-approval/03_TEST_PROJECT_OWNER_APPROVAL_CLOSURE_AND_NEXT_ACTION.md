# Test Requirements, Project Owner Approval, Closure, and Next Action

## Required future tests

The later adapter implementation must test at least:

1. exact two-key payload accepted;
2. missing instruction rejected;
3. missing data rejected;
4. unknown top-level field rejected;
5. blank and untrimmed instruction rejected;
6. overlong instruction rejected;
7. non-string instruction rejected;
8. non-mapping data rejected;
9. empty data accepted and rendered as `{}`;
10. nested bounded JSON-compatible data accepted;
11. every provider/config top-level field rejected as unknown;
12. exact deterministic rendering;
13. recursive sorted-key compact JSON serialization;
14. exactly one provider-native message;
15. exact user role and no system message;
16. no multi-turn/history/session semantics;
17. `output_schema_ref` remains separate;
18. provider/model/config are never taken from payload;
19. instruction/data do not enter logs or failure details; and
20. no Core dependency.

Tests must also prove no coercion/trimming, UTF-8 non-ASCII preservation,
`allow_nan=False`, no trailing newline, omission of provider `options`, and
validation before any HTTP/schema-provider side effect.

## Project Owner approval

I, as Project Owner, approve a minimal provider-neutral Stage 0.7 input payload contract based on one bounded instruction and one bounded JSON-compatible data mapping.

The payload must not contain provider/model/runtime configuration, tools, persistence, business action authority, or provider-native message structure.

The adapter may deterministically translate this provider-neutral payload into one Ollama user message, while output schema validation remains separately owned and fail-closed.

No adapter implementation, Brain integration, or production inference is authorized by this decision.

## Publication and activation

The allowed diff is this governance package only. Activation requires a normal
clean, mergeable pull request into `main`, with no force/history rewrite.
Merging activates only this semantic payload profile and Project Owner
acceptance; it creates no adapter/source/test/config/runtime authority.

## Closure and remaining blockers

The input-payload blocker is resolved when this package is merged. Adapter
implementation remains blocked until the implementation approval is rerun and
merged against this new authority baseline. Live staging inference, Brain
wiring, and production use remain separately prohibited.

## Next official action

`Intelligence Stage 0.7 — Ollama Provider Adapter Implementation Approval Rerun`

The rerun must incorporate this exact two-key profile and rendering algorithm,
freeze the three-path implementation/test scope, and preserve every existing
no-inference/no-Brain/no-production boundary.

`INTELLIGENCE STAGE 0.7 INPUT PAYLOAD CONTRACT VERIFIED — ACCEPTED — CLOSED`
