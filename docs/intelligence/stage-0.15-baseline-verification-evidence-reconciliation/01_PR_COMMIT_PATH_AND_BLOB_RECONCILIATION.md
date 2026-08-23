# PR, Commit, Path, and Blob Reconciliation

Git history and GitHub PR metadata independently identify the Stage 0.15
implementation as follows:

| Identity | Authoritative value |
|---|---|
| Implementation branch | `implementation/intelligence-stage-0.15-core-to-brain-integration` |
| Implementation commit | `21aeed1ad0f87a3a28835a9aaf4b67a0f8fab44f` |
| Merge commit | `4a692a58e516520f7cb10cb3315eb348e7b5b34d` |
| Changed path | `tests/integration/test_core_to_brain_chain.py` |
| Changed path count | exactly `1` |
| Implementation-side blob | `435a4205cce7f64a51da41a6673c6bff9e0d5f96` |
| Merge-side blob | `435a4205cce7f64a51da41a6673c6bff9e0d5f96` |
| Blob identity | identical |

The previously supplied value
`21aeed1ad0f87a3a28835a9aaf4b67a0f8cab44f` does not identify the PR commit.
It is classified permanently as a governance documentation error. No history
rewrite is required or authorized, and the error does not alter the merged
implementation.

The accepted reviewer finding is preserved: the test-local recording
attribute was renamed from `requests` to `received` to prevent a prohibited-
source scanner false positive. No chain or production behavior changed.
