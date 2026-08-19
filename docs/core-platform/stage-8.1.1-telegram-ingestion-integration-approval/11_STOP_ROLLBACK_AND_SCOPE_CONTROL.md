# Stop, Rollback, and Scope Control

Stop before implementation expansion if any of these becomes necessary:

- Universal Ingestion runtime change;
- RequestContext runtime/contract change;
- Storage runtime/semantics change;
- media-group state or aggregation;
- broad Telegram SDK decoupling;
- real Telegram network;
- production deployment or configuration change.

For a Universal Ingestion result incompatibility, report exactly
`STAGE 8.1.1 UNIVERSAL INGESTION SCOPE DECISION REQUIRED`. For other conflicts,
report the concrete stop condition and request separate authority. Do not solve
the conflict by widening paths or semantics.

Implementation rollback is the revert of only the authorized adapter/test diff.
No data or infrastructure rollback is applicable because none is authorized.
