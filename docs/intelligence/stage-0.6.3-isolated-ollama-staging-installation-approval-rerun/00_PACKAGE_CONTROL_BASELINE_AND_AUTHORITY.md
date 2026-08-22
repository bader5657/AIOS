# AIOS Intelligence Stage 0.6.3 — Isolated Ollama Staging Installation Approval Rerun

| Control | Recorded value |
|---|---|
| Work type | `GOVERNANCE APPROVAL ONLY` |
| Approval baseline | `c5cc78096f2510a8f3d7c6efa76f2adf1439d97f` |
| Baseline gate | `HEAD == main == origin/main`; clean worktree |
| Stage 0.6.1 | `FIRST RUNTIME STRATEGY VERIFIED — ACCEPTED — CLOSED` |
| Stage 0.6.2 | `OPTION C APPROVED` |
| Provenance | `PASS WITH LIMITATION`; class `C — STRONGLY_RECONCILED` |
| Approval result | `ISOLATED STAGING INSTALLATION APPROVED` |
| Production authority | `NONE` |

Required limitation:

`Canonical model family/repository verified; exact source revision of the Ollama conversion not independently attested.`

This limitation is accepted only for the exact, controlled, isolated staging
artifact. It does not establish cryptographic revision-to-blob provenance or
authorize production use.

Merging this package activates authority to perform a separately controlled
installation under every recorded preflight, identity, resource, isolation,
stop, and rollback control. The merge does not itself install or download
anything, start a container, execute inference, integrate AIOS, or activate
production.

Records:

- `01_PINNED_IDENTITIES_STORAGE_AND_RESOURCE_CONTROLS.md`;
- `02_RUNTIME_NETWORK_PRIVILEGE_AND_CONFIGURATION.md`;
- `03_INSTALLATION_SEQUENCE_STOP_AND_ROLLBACK.md`;
- `04_PROJECT_OWNER_ACCEPTANCE_REVIEW_AND_ACTIVATION.md`.
