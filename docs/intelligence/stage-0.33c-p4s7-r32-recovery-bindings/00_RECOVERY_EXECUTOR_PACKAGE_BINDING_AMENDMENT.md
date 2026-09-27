# AIOS P4S7-R32 Recovery Executor / Package-Binding Amendment

Classification: `P4S7_RECOVERY_EXECUTOR_PACKAGE_BINDING_AMENDMENT_READY_FOR_REVIEW`

This implementation binds the reviewed fresh recovery approval to the unchanged
historical approved input. It implements the split-source model governed by
[R30](../stage-0.33c-p4s7-approval-expiry-recovery/00_APPROVAL_EXPIRY_RECOVERY_AMENDMENT.md)
and [R31A](../stage-0.33c-p4s7-recovery-private-source/00_RECOVERY_PRIVATE_SOURCE_FILESYSTEM_GOVERNANCE.md).
Independent review and human merge are required. No automatic merge.

## Active bindings

| Binding | Recovery value |
|---|---|
| Authority | `7bc638e2-e1f4-4e87-a54a-4d0df031b130` |
| Approved-input source | `/run/aios/stage-0.33c-p4s5-source/approved-input.json` |
| Approval source | `/run/aios/stage-0.33c-p4s5-recovery-source/approved-input-approval.json` |
| Input semantic / transport bytes | `1327` / `1328` |
| Input semantic SHA-256 | `e3c66fddf815c57f17baad49926c44588279d60cb4e78df867e0ae2189237a6d` |
| Input transport SHA-256 | `2506e3ca741a2ee0429112af641c2febdae5675f522cd58a855f6b1d6896a837` |
| Approval semantic / transport bytes | `3579` / `3580` |
| Approval semantic SHA-256 | `6ea5fc118e375ac035f321110198eb43811fb5b991a095554c15d0a6cbeb16c9` |
| Approval transport SHA-256 | `1579e7fffd93bd0dc35d31539c9703b21482c486eee14aaed5535ab3a87dc367` |
| Approval ID | `3a478d87-5c4f-4778-9f88-2228f4d7167f` |
| Approved at | `2026-09-26T23:24:12.093093Z` |
| Not after | `2026-10-03T23:24:12.093093Z` |
| Reviewed package payload SHA-256 | `be7a1750eb77ae77e8f020fc3f29c5f047cf88d1720a387f50f58f58c877962e` |
| TF-A | `c006afcad84984baea6af164067fdd4cfc31cdcac5f86baf7b1ceefd6e4c5065` |
| Executor SHA-256 | `da020dff0974acf0bb7fc22bc1b54f17d149ee8f11ace67420eb16cca73cd6be` |

The transport digests above are supplied reviewed evidence. Execution binds
transport through the exact semantic digest/count and the unchanged requirement
for exactly one final LF. No separate redundant transport constant is needed.
The approval also independently binds the input transport digest.

Both private parents independently require root:root, exactly `0700`, and
no-follow directory traversal. Both files independently require regular type,
root:root, exactly `0400`, single link, exact size, digest, and LF transport.
Both parent opens complete before either source is read. All opened descriptors
are closed if either parent or a later preclaim gate fails. The input is never
copied or linked into recovery storage. The supplied recovery parent identity
(device `25`, inode `984328`) is current operator evidence, not a permanent
execution contract; this amendment neither re-observes nor hard-codes it.

The schema-validated package additionally requires the exact approval ID and
both timestamps, and computed payload SHA == outer payload SHA == reviewed
recovery SHA. TF-A must equal both the unchanged DTO projection and the reviewed
constant. Both registry IDs remain null and registration_succeeded remains
false. No database lookup is introduced. Freshness remains strictly now <
not_after, with no renewal, and is rechecked immediately before claim.

## Authority and activation boundary

Marker and result names derive only from the recovery authority:

- `step4-install-authority-7bc638e2-e1f4-4e87-a54a-4d0df031b130.json`
- `step4-install-authority-7bc638e2-e1f4-4e87-a54a-4d0df031b130.json.result.json`

They remain under the existing runtime-sync-evidence directory. Old authority
residue neither consumes nor authorizes recovery. A new recovery marker or
result blocks reuse. UNUSED → CLAIMED → DURABLY_CONSUMED → EXECUTION_STARTED,
ambiguous consumption handling, durability, publication, result evidence, and
partial-install/cleanup behavior remain unchanged.

No merged governance freezes an exact recovery activation path/version.
ACTIVATION_RECORD is therefore None, and the default activation reader stops
with PRECONDITION_FAILED / RECOVERY_ACTIVATION_NOT_GOVERNED before opening
activation or source files. The historical activation is never a default or
fallback. Its historical authority also fails the active authority schema gate.
Canonical activation parsing and runtime Git/interpreter checks remain covered
by isolated regression fixtures; retaining their code does not activate them.
A later governed amendment must incorporate a reviewed recovery activation
path/version and associated merge bindings. Setting a path alone is not that
amendment, and this document does not create or authorize activation.

Preclaim order remains activation/authority, runtime/executor/interpreter,
private parents, source metadata/link/bytes, authority unused, target/staging
absence, package/manifest/TF-A/Model B, freshness, then claim. Runtime target
names and parent are unchanged.

## Validation and evidence limits

All execution-path tests use temporary fixtures and stub production trust
prerequisites. Generic schema/manifest/DTO regressions isolate the new recovery
binding helper; separate recovery tests exercise that helper through the full
package validator with frozen synthetic byte/payload/TF-A bindings and the
exact recovery approval identity/window. Production constants are asserted
separately. No private business bytes are committed, copied, or reread. These
are implementation tests, not a new verification of the private live package.

Coverage includes fresh-pair acceptance; historical, hash, payload, identity,
timestamp, TF-A and Model B rejection; parent ownership/mode/missing/symlink
failures; independent source selection; source link/hash/LF failures; historical
marker preservation; recovery consumption; and historical activation rejection.
Preclaim tests assert claim/staging/publication counts of 0/0/0. Existing
safe.directory, canonical activation, runtime HEAD/clean-tree, interpreter,
manifest, durability, result evidence and cleanup regressions continue to pass.

- Focused: 317 passed, 1 skipped, 42 subtests passed.
- Full suite: 1779 passed, 117 skipped, 835 subtests passed; three existing
  TestEvent collection warnings. Database opt-ins explicitly removed.
- Static: Python compilation without execution, git diff --check, unchanged
  DTO projection comparison, and executor/policy digest equality.
- The initial full unit attempt used an environment lacking pytest-asyncio;
  rerunning in the existing async-capable environment resolved those failures.

## Current boundary and next official action

Recovery activation created: NO. Historical activation modified: NO.
Historical input, approval, authority evidence, and absence evidence modified:
NO. Production runtime modified: NO. Installer executed: NO. Production claim,
staging, targets, candidate, or authorization.json created: NO. Live harness
invoked: NO. PostgreSQL contacted: NO. Step 5 authorized: NO.

The recovery namespace is bound in code, but recovery execution is intentionally
impossible pending separate activation governance. Review this implementation
PR independently, then human merge if accepted. Only afterward may the separate
recovery activation-governance stage proceed. Installation and Step 5 remain
unauthorized. STOP.
