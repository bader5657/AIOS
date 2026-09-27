# First Recovery Evidence Binding — Separate Population Authority

Classification: `P4S7_FIRST_RECOVERY_BINDING_AUTHORITY_READY_FOR_REVIEW`

## Authority and narrow scope

This governance-only addendum requires independent review and human merge.
After those prerequisites, it authorizes only later population of one first
recovery evidence record with the bindings below, for its own independent
review and human merge. No record is populated by this change. Review readiness
is not effective authority; no automatic merge is authorized.

This supplies the separate binding-supersession authority required by step 5 of
the [PR #301 bootstrap contract](../stage-0.33c-p4s7-recovery-review-merge-evidence/00_RECOVERY_REVIEW_MERGE_EVIDENCE_CONTRACT.md#bootstrap-anti-circularity-and-supersession)
and the [R34 binding transition blocker](../stage-0.33c-p4s7-recovery-activation/00_RECOVERY_ACTIVATION_GOVERNANCE.md#executor-impact-and-activation-blockers).
Neither mechanism-only PR #301 nor PR #302's implementation/policy digest grants
that authority. No existing addendum freezes this post-PR #302 binding.

Reuse [R15's separate immutable addendum](../stage-0.33c-p4s7-final-authority-supersession/00_R13_FINAL_EXECUTOR_AND_ACTIVATION_BINDING_SUPERSESSION.md)
and [R24's pinned-runtime/later-governance separation](../stage-0.33c-p4s7-activation-binding-supersession/00_POST_PR295_ACTIVATION_BINDING_SUPERSESSION.md).
Their historical activation schemas and identities are not imported into
recovery. PR #301's operator-verified protected-pin trust model remains unchanged.

## Frozen prospective binding and preserved baseline

The exact R34 baseline artifact is the immediate predecessor, not an invented
binding UUID. R34 historically freezes runtime HEAD
`ba717f6990d775748f46d62ef03a696f1618077b` and executor SHA-256
`da020dff0974acf0bb7fc22bc1b54f17d149ee8f11ace67420eb16cca73cd6be`.
Those values remain immutable history; the later first record may supersede
only that runtime/executor binding with the following exact runtime, executor
and policy identities. An ancestor or another clean checkout is not equivalent.

| Binding | Exact value |
|---|---|
| `expected_runtime_head` | `b5fa2acaa66db799ebd8ec03d2a06a04e34753a2` |
| `executor_sha256` | `7b38ce601cbeb930a4277af8f4dfe66bbf4b7b9df9ad94059e504082f58a8beb` |
| `policy_sha256` | `39b0768d989c89fa64c6593834220f9846c6013e7e10c03ec5eec34cd78098c0` |
| `authority_id` | `7bc638e2-e1f4-4e87-a54a-4d0df031b130` |
| `approval_id` | `3a478d87-5c4f-4778-9f88-2228f4d7167f` |
| `package_payload_sha256` | `be7a1750eb77ae77e8f020fc3f29c5f047cf88d1720a387f50f58f58c877962e` |
| `policy_reference` | `docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/00_ONE_SHOT_RUNTIME_INSTALLATION_AUTHORITY.md` |
| `activation_governance_reference` | `docs/intelligence/stage-0.33c-p4s7-recovery-activation/00_RECOVERY_ACTIVATION_GOVERNANCE.md` |

Executor bytes must equal the executor blob at the frozen runtime HEAD, their
SHA must equal the policy-bound executor SHA above, and exact policy bytes must
hash to `policy_sha256`. The separately completed runtime-sync verification is
retained operator evidence, not a sync or privileged live verification performed
by this addendum. Runtime remains pinned when this later governance is merged.

Merging this addendum authorizes the bounded population step only. R34 remains
authoritative until the separately reviewed/human-merged evidence supersession
and separately authorized selector publication establish the new binding under
PR #301. This document alone never makes a new operational binding effective.

## Exact component review/merge identities

| Evidence object | `pr_number` | `reviewed_head_sha` | `merge_sha` |
|---|---|---|---|
| `r32` | 299 | `fd36b9abe6920ea807a070ea63589622e1d2e2cb` | `ba717f6990d775748f46d62ef03a696f1618077b` |
| `r34` | 300 | `ed7f75551a118a96fc26e805057c1a875345c55a` | `8e9a8023742773b055e17dba002b2ebf07528118` |
| `reader` | 302 | `f379a15eb5f64b5b5a6ffd7cb7ca0d27c847e368` | `b5fa2acaa66db799ebd8ec03d2a06a04e34753a2` |

Preparation cross-checked these PR/head/merge mappings against GitHub PR metadata
and original local Git commit objects. Each merge has exactly two parents and
its second parent equals the listed head. Exact reviewed/merged blob equality
was verified for R32's amendment, executor and policy; R34's document; and the
reader's executor and policy. The PR #301 contract merge
`7f124e307d9a516b4ce278d800c92d29d476cf5e` is required in the reader lineage.

These are repository identity checks, not proof of human review by topology.
The PR #302 CLEAN review is retained in the operator review record. GitHub PR
review arrays observed during preparation are empty for PRs #299, #300 and
#302; no GitHub approval is inferred. Before population, independently verify
retained review acceptance and actual merge evidence for all three exact heads,
as well as this addendum's accepted head and actual human merge. Missing,
contradictory or unavailable retained evidence is STOP. Preserve PR #301's
separate independent verification before selector publication; root ownership,
Git ancestry or an API merged flag alone never establishes trust.

## First-record predecessor and unchanged schema

The later `supersedes` object has exactly these four required strings:

| Field | Exact value |
|---|---|
| `kind` | `r34-baseline` |
| `commit` | `8e9a8023742773b055e17dba002b2ebf07528118` |
| `path` | `docs/intelligence/stage-0.33c-p4s7-recovery-activation/00_RECOVERY_ACTIVATION_GOVERNANCE.md` |
| `transport_sha256` | `299296d106d6d661ac2fd55b1442b9980485d7f2bdf64b228fbfebbbb73dcf31` |

The baseline digest was computed from all 15,344 exact Markdown blob bytes at
the specified PR #300 merge, with no stripping, normalization or JSON parsing:

```sh
git --no-replace-objects cat-file blob \
  8e9a8023742773b055e17dba002b2ebf07528118:docs/intelligence/stage-0.33c-p4s7-recovery-activation/00_RECOVERY_ACTIVATION_GOVERNANCE.md \
  | sha256sum
```

The later record belongs only at
`docs/intelligence/stage-0.33c-p4s7-recovery-review-merge-evidence/records/<binding-id>.json`
in `bader5657/AIOS`, using schema version
`aios-p4s7-recovery-review-merge-evidence-v1`. Allocate one canonical lowercase
UUID at the later population step; it identifies that new record, never R34.
No UUID, record, evidence merge SHA or selector is created here.

Its exact fifteen fields remain `schema_version`, `repository`, `binding_id`,
`authority_id`, `policy_reference`, `activation_governance_reference`,
`approval_id`, `package_payload_sha256`, `expected_runtime_head`,
`executor_sha256`, `policy_sha256`, `reader`, `r32`, `r34`, `supersedes`.
The review objects remain exactly `pr_number`, `reviewed_head_sha`, `merge_sha`.
PR #301's closed nested schemas, exact types, duplicate rejection at every depth,
canonical UTF-8 serialization (`ensure_ascii=False`, `sort_keys=True`,
`separators=(",", ":")`, `allow_nan=False`), exactly one ASCII LF, and no
normalization apply without amendment. R34's eight-key activation schema and
PR #301's four-key selector schema remain unchanged.

## Later population gates and exclusions

After independent review and human merge of this addendum, the later population
step must reverify exact runtime/executor/policy identities and complete tracked,
staged and untracked cleanliness; required R32/R34/PR #301/reader lineage;
component review/merge evidence; the exact predecessor bytes/hash; and absence
of an intervening or conflicting authorized evidence successor. Review both
parent histories with the merged reader's replacement/graft-resistant semantics.
Any drift, conflict, unavailable evidence, malformed binding or ambiguity is
STOP, not authority to repair, choose another predecessor or create a second
record. Local Git checks do not prove global freshness; independent operator
verification of the complete authoritative succession remains mandatory.

The later evidence PR must descend from this addendum's actual merge and the
frozen runtime lineage, retain the exact predecessor, and undergo independent
review and human merge with reviewed/merged blob equality. Its own future merge
SHA is learned only afterward; no artifact embeds its own commit or digest.
The addendum merge and evidence merge do not replace the frozen runtime HEAD.
No additional machine-readable field or trust mechanism is introduced.

All R32/R34/PR #301 and merged PR #302 artifacts stay byte-identical. Preserve
the approval window `2026-09-26T23:24:12.093093Z <= now <
2026-10-03T23:24:12.093093Z` at the existing applicable gates, with no renewal,
extension or reservation. Package, interpreter, custody, unused-authority,
TF-A, Model B, freshness and preclaim controls remain unchanged. This preparation
does not establish fresh private-source, privileged custody or UNUSED evidence.

This authority does not authorize selector publication or transition; recovery
activation creation or execution; an installation attempt or authority
consumption; claim/result/staging/target creation; runtime sync; service restart,
rebuild or reconfiguration; database operations; historical-record modification;
or Step 5. Every later operational action retains its separate authorization and
fresh verification requirements. The reader's local success is necessary but
insufficient authority to execute.

Only this Markdown addendum is added. Next action: independent review and human
merge if accepted; later bounded evidence population is a separate task. STOP.
