# Stage 0.33C-P4S7-R6 Regenerated Package Frozen-Binding Amendment

Classification: `P4S7_REGENERATED_PACKAGE_BINDING_AMENDMENT_READY_FOR_REVIEW`.

## Decision and narrow scope

This governance artifact replaces only the active package-specific frozen
bindings for the controlled Step-4 installation path. The obsolete private
package is unavailable; the replacement pair was produced by the consumed
PR #282 one-shot regeneration authority and independently verified by
P4S7-R5-R1 with status `VERIFIED`.

This amendment contains metadata only. It does not copy package JSON into Git,
regenerate either artifact, create or renew an approval, change Project Owner
facts or provenance, select another retained source, or change Model B or TF-A
semantics. Historical governance remains intact and auditable.

## Active regenerated-package bindings

The only active package-specific bindings after independent review and human
merge of this amendment are:

| Binding | Verified value |
|---|---|
| regeneration authority | `1284ecc0-54d9-4df8-9d30-791710770f9b` |
| review-material workspace | `/opt/aios/data/documents/.stage-0.33c-p4s7-regeneration-1284ecc0-54d9-4df8-9d30-791710770f9b` |
| retained manifest ID | `9801b5e4-453d-429a-b51f-e8ffaa17a2c9` |
| approval ID | `122625d8-d3fd-42a7-b9c6-c54fc1f367bf` |
| `approved_at_utc` | `2026-09-19T21:24:52.273127Z` |
| `not_after_utc` | `2026-09-26T21:24:52.273127Z` |
| input semantic bytes | `1327` |
| input transport bytes | `1328` |
| input semantic SHA-256 | `e3c66fddf815c57f17baad49926c44588279d60cb4e78df867e0ae2189237a6d` |
| input transport SHA-256 | `2506e3ca741a2ee0429112af641c2febdae5675f522cd58a855f6b1d6896a837` |
| `trusted_facts_sha256` | `c006afcad84984baea6af164067fdd4cfc31cdcac5f86baf7b1ceefd6e4c5065` |
| `package_payload_sha256` | `3b25029b1015bd67eddab2557cfef8202a48fff546ffc79fc3ab708c144de1f4` |
| approval semantic bytes | `3579` |
| approval transport bytes | `3580` |
| approval semantic SHA-256 | `2ea9e735d7a5183a3e247abf57438d6e095fd7e9858d5ce688d221f7e9050f26` |
| approval transport SHA-256 | `1d24f693154e0e8c2ac4504b9e81086662670c870e785c4f0d4d79c3ded16ac8` |
| provenance | exactly `26` governed pointers |
| Model B | `registry_record_id: null == null`; `registration_succeeded: false` |
| independent verification | `P4S7-R5-R1: VERIFIED` |

The payload digest above was independently derived from canonical
`package_payload` bytes and matched both the approval wrapper and regeneration
summary. A malformed 65-character request-side literal was discarded; it is
not a binding and was not edited to derive this digest.

`trusted_facts_sha256` is exclusively the merged TF-A digest: SHA-256 of the
canonical deterministic DTO projection of validated `TrustedReceiptFacts`.
It is not the digest of the raw `trusted_receipt_facts` input subobject. The
semantic-input, transport-input, TF-A, payload, approval-semantic, and
approval-transport hash domains remain separate.

The regenerated input semantic bytes and digest happen to equal the historical
input semantic bytes and digest. This is the independently verified result of
deterministic reconstruction from unchanged governed facts and evidence. It is
not reuse or recovery of the unavailable old package. The approval ID,
timestamps, TF-A digest, payload digest, approval bytes, and approval digests
are fresh.

## Historical bindings superseded, not deleted

The merged installation authority historically froze these unavailable-package
values:

| Historical binding | Preserved historical value |
|---|---|
| input semantic bytes | `1327` |
| input transport bytes | `1328` |
| input semantic SHA-256 | `e3c66fddf815c57f17baad49926c44588279d60cb4e78df867e0ae2189237a6d` |
| approval semantic bytes | `3549` |
| approval transport bytes | `3550` |
| approval semantic SHA-256 | `266c39426fae0b04dacf009436334dd34d6791368dcad5066a9b2a37b9bd8a57` |

Those values remain historical evidence but cease to be the active package
bindings after this amendment is independently reviewed and human-merged. In
particular, the old approval counts and digest are not valid for the regenerated
approval.

## Executor identity and non-execution boundary

The currently merged TF-A installer at
`docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/one_shot_install.py`
independently hashes on merged `main` to SHA-256
`b82591be0d8f4f9876a8925e4428c3c0dc85589431733dfca178f86b3e415412`.
This amendment changes neither that file nor its semantics, filesystem safety,
claim handling, partial-install behavior, or result-evidence rules.

The unchanged executor still contains historical package constants. This
governance artifact does not claim that the current executable accepts the
regenerated pair and does not authorize editing or running it. A later,
separately governed runtime-install execution authority must reconcile its
executable bindings with the active values above, freeze the resulting
executor identity, and receive independent review and human merge before any
installation attempt.

Approval freshness was rechecked before publication of this amendment. Expiry
before a later governed action is a STOP; this amendment does not renew or
replace the approval.

## Preserved contracts

The retained manifest remains exactly
`9801b5e4-453d-429a-b51f-e8ffaa17a2c9`. The 26-pointer provenance map remains
unchanged and contains only `EVIDENCE_DERIVED` and
`PROJECT_OWNER_APPROVED`. Model B remains exact JSON equality:

```text
approval.package_payload.evidence.registry_record_id
==
approved_input.ingestion_result.registry_record_id
```

Its verified value is `null == null`, with `registration_succeeded == false`.
No PostgreSQL lookup is required or authorized.

## Runtime and stage boundary

This amendment does not authorize copying either regenerated artifact into
`/run/aios/stage-0.33c-p4s5-source`, synchronizing `/opt/aios-src`, changing
runtime evidence-directory permissions, restarting a service, executing the
installer or harness, creating a candidate or `authorization.json`, contacting
PostgreSQL, closing Step 4, or authorizing Step 5.

The mandatory remaining order is: this package-binding amendment PR;
independent review; human merge; separately governed runtime checkout
synchronization; evidence-directory remediation; separately governed private
source materialization; repeated P4S7 post-merge/pre-execution verification;
runtime-install execution authority; independent review; human merge; exactly
one installation attempt; post-execution verification; Step-4 closure; and only
then Step-5 consideration. No stage may be collapsed.
