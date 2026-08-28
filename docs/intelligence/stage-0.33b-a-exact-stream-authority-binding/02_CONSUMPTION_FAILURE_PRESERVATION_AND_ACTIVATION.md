# Stage 0.33B-AB Consumption, Failure, and Activation Contract

The existing PR #249 authority is consumed permanently at the first attempt to launch the exact governed production control plane, even if docker/psql fails, PostgreSQL rejects the connection, stdin fails, or BEGIN fails. No probe, manual psql, SELECT 1, alternate argv, retry, or second launch is permitted.

Before any future launch, execution evidence must be flushed and fsynced with PR #249 and this amendment identity, PR #251 reviewed HEAD/merge, exact argv, nonce, template/Migration/assembled hashes and bytes, 57/49/106 counts, 49 frames/chunks, parser configuration, exact-delta identity, assembly PASS, and framing PASS. The verified evidence root remains `/opt/aios/runtime/intelligence/production-execution-evidence/stage-0.33b-d`; lstat/stat verification is required and no privileged repair is authorized.

Fresh Stage 0.33B-D production gates remain mandatory: identity, prestate, locks, zero-row gate, fingerprints, object/security baselines, Migration UP hash, post-UP verification, preservation, and pre-COMMIT health. C01 COMMIT remains final SQL. This amendment does not replace those gates or authorize candidate activation.

Activation is eligible only after independent PASS of this amendment, zero blockers, unchanged merge, synchronized clean main, independent confirmation that PR #249 is ACTIVE/UNCONSUMED, exact PR #251 identities, Migration 0005 unexecuted, and no superseding governance. The amendment itself does not consume authority.

Current safety state: production PostgreSQL contacted NO; production launch NO; production evidence session NO; Migration 0005/0004 NOT EXECUTED; PR #249 ACTIVE/UNCONSUMED; runtime, services, Telegram, Universal Ingestion, evidence root, and candidate traffic unchanged.
