# Proposed Tooling, Boundaries, and Next Action

The remaining proposed authorization is internally bounded but inactive:

- detached clean checkout at `/opt/aios/runtime/verification/stage-0.15-src`;
- `/usr/bin/python3` version `3.12.3` with standard-library `venv`;
- disposable venv `/opt/aios/runtime/verification/stage-0.15-venv`;
- exact repository `requirements.txt` pins;
- `pytest==8.4.2`, classified only as `TEST_ONLY_VERIFICATION_TOOL`;
- no other test-only package;
- standard TLS-verified package index acquisition limited to those packages;
- immutable raw evidence at
  `/opt/aios/runtime/verification/stage-0.15-evidence`; and
- the complete approved 17-gate non-live verification matrix.

The proposed network authority ends after acquisition. Production source,
production venv, services, runtime/VPS state, PostgreSQL, Telegram, Ollama,
Docker production state, firewall, secrets, business data, models, and live
inference remain prohibited. Stage 0.16 remains unauthorized.

Any source, acquisition, installation, collection, tooling, or gate failure
must stop and preserve evidence without source edits, dependency additions,
version changes, retry improvisation, or skip conversion. Historical counts
remain comparison-only. Checkout, venv, and raw evidence cleanup remains
separately governed after Stage 0.15 final closure.

Project Owner approval is not activated. The next authority must copy exactly
the PR #163 implementation SHA:

`21aeed1ad0f87a3a28835a9aaf4b67a0f8fab44f`

`STAGE 0.15 FINAL CORRECTED VERIFICATION AUTHORIZATION BLOCKED`
