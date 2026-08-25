# Migration 0003 — Baseline, Provenance, and Down-Hash Reconciliation

| Control | Verified value |
|---|---|
| Clean-main baseline | `dc567260c8f7c70f3e651531c2ab7ed8fcff7855` |
| Implementation PR | `#212` |
| Implementation commit | `1a8b64b0c86e9025d6512443718c6485d35c2cd6` |
| Authority PR | `#213` |
| Previous execution result | preflight blocked; no database connection or change |
| Previous transaction attempts | `0` |
| Previous authority accounting | `NOT_CONSUMED_BEFORE_PRODUCTION_ATTEMPT` |

Path-specific Git history proves that implementation commit `1a8b64b` introduced
both Migration 0003 files reviewed in PR `#212`. No later commit modifies either
path. Independent hashing of the blobs in that implementation commit matches the
files on the clean-main baseline exactly.

The production execution stopped at the local source-hash gate. Production
PostgreSQL was not contacted, no transaction began, no DDL ran, no attempt was
consumed, and neither migration file was modified.

PR `#213` itself records the same actual down hash as the repository artifact.
The conflicting hash appeared in the later execution instruction, not in Git or
the merged authority package. The discrepancy classification is therefore:

`GOVERNANCE_TRANSCRIPTION_ERROR`

The independently recalculated authoritative hashes are:

- up: `e858f5ad210aca2d7e6a2badf3dab2585cf33eacdcf46e6b6bf839dcea7d37eb`;
- down: `c374837cad14df82126ab56ae487766694911ed89cbdace1382faeb40aebb8fe`.

The candidate down value copied into the reconciliation request does not match
the independently calculated artifact and is not adopted.
