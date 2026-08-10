# Stage 3.2.2 VM-13 Full Authority Trace

| Control | Value |
|---|---|
| Lifecycle | **DRAFT EVIDENCE** |
| Accepted baseline | `0845dc4f836b3fafff5a9c66a346b5ca098863ab` |
| Rule | Accepted-history authority; no working-tree behavior used as authority |

| Authority/evidence | Trace result |
|---|---|
| Blueprint, Frozen Roadmap, Execution Plan | Stage and lifecycle intent retained; unchanged |
| Authority Hierarchy, GD-002, GD-007 | Ordered lifecycle and accepted-history rule retained |
| Canonical Model, Layer Architecture, Pipeline Model | No change or supersession |
| Stage 1.3.1 Root Test Command | Authorizes repository `python3`, standard-library `unittest`, explicit discovery root, and no dependency |
| Stage 3.2.2 Draft `308a289` | Existing authority package drafted |
| Proposed `c0762d8` | Proposal accepted after Draft |
| Reviewed `5035d9e` | Review PASS, but pytest command contradiction was not detected |
| Approved `51cf5c4` | Original package approved |
| Published `e612223` | Original package published |
| Active `0845dc4` | Latest accepted baseline; implementation authority active except unresolved VM-13 verification consistency |
| Original Minimum Contract Verification | Mandates `python -m pytest` without dependency authority, contradicting Stage 1.3.1 and reproducibility |
| Project Owner VM-13 decision dated 2026-08-10 | Explicitly selects standard-library `unittest` for the complete Stage 3.2.2 suite |
| This reconciliation | Scope-limited supersession of VM-13 commands only; existing governance class reused |

VM-01 through VM-12 and VM-14, Stage 3.2.2 implementation scope, runtime and
storage behavior, and every higher authority remain unchanged. Working-tree
implementation/test changes are evidence candidates only and are not authority.
