# Stage 0.33C-P4S3-R1 Corrected Runtime Package Installation Governance

## Authority and corrective history

This documentation-only package governs a future installation of the two
already validated Step-4 approved-input artifacts. It does not install either
artifact and does not authorize package reconstruction, harness invocation,
candidate creation, PostgreSQL contact, `authorization.json`, or Step 5.

The preceding P4S3 task stopped before changing Git or runtime state because its
task input transcribed the approval semantic SHA-256 incorrectly as
`266c39d26fae0b04dacf009436334dd34d6791368dcad5066a9b2a37b9bd8a57`.
That value is invalid and prohibited. No package was regenerated, no Project
Owner-approved fact changed, and no installation was attempted. The corrected
and unchanged P4S2 bindings are:

| Binding | Authoritative value |
|---|---|
| manifest identity | `9801b5e4-453d-429a-b51f-e8ffaa17a2c9` |
| approved-input semantic SHA-256 | `e3c66fddf815c57f17baad49926c44588279d60cb4e78df867e0ae2189237a6d` |
| approved-input semantic bytes | `1327` |
| approved-input transport bytes | `1328` |
| approval-record semantic SHA-256 | `266c39426fae0b04dacf009436334dd34d6791368dcad5066a9b2a37b9bd8a57` |
| approval-record semantic bytes | `3549` |
| approval-record transport bytes | `3550` |
| one-shot harness SHA-256 | `b9fc9fb22724184696eabf02525bcc0a626bdff5ce3943ed31ba2e21130f5cad` |

The input SHA is over exactly the 1,327 semantic bytes, excluding the terminal
LF. Its 1,328-byte transport form is those exact semantic bytes followed by
exactly one `0x0A` byte. The approval SHA is over exactly the 3,549 semantic
bytes, also excluding the terminal LF; its 3,550-byte transport form is those
exact semantic bytes followed by exactly one `0x0A` byte. Neither frozen
semantic SHA is claimed to be a SHA-256 of its transport file, and this
remediation does not invent or freeze a transport SHA. Fixed semantic-prefix
length plus its frozen cryptographic SHA, the mandatory final `0x0A`, and exact
total transport length bind each governed transport object to the approved
semantic object plus one LF. A future installer must receive the exact
P4S2-validated
transport byte objects through separately reviewed execution evidence. It must
not reconstruct JSON or business facts from this document, prose, environment
values, or operator input. If the exact byte objects are unavailable or any
binding differs, installation is ineligible and stops without regeneration.

## Exact paths and current prestate

The governed parent is exactly:

`/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c`

It was reverified for this publication as a real non-symlink directory owned
`root:aiosadmin` with mode `0750`. The only governed final paths are:

- `/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/approved-input.json`;
- `/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/approved-input-approval.json`.

Both final paths were absent. Existing `consumed` and
`runtime-sync-evidence` directories are out of scope and remain unchanged.
`authorization.json` and every consumed authorization record are prohibited
targets.

Each future final artifact must be a regular non-symlink file owned
`root:aiosadmin` with mode `0440`. No permission broadening, ownership repair of
an existing target, alternate directory, environment override, or caller-
selected final path is permitted.

## Approval and immutable-package gate

Immediately before a future installation attempt, the governed executor must
read the exact bounded approval transport bytes without following symlinks,
validate the closed Step-4 approval schema and safe-string grammar, verify the
3,550-byte transport contract (a 3,549-byte semantic prefix with the
authoritative semantic SHA-256 followed by exactly one terminal `0x0A` and no
additional bytes), and enforce the merged exclusive `not_after_utc` rule
against an absolute UTC clock. The approval is
valid only while `now < not_after_utc`. Equality or later is expired.

Expiry, invalid time, unreadable time, schema failure, hash failure, byte-count
failure, or disagreement with the bound input and harness identities is a STOP.
The executor must not edit a timestamp, extend a window, generate a replacement
approval, reconstruct an artifact, or request a second identity in the same
attempt. New Project Owner approval requires separate governance.

The Project Owner business facts, item order, descriptions, nulls, units,
packaging, quantities, and provenance remain immutable and are deliberately
absent from Git. This package contains only content-minimized identities,
hashes, sizes, paths, metadata requirements, and execution constraints.

## Separation of governance and execution

This publication creates governance only. The required sequence is:

1. P4S3-R1 governance publication;
2. independent review;
3. merge;
4. separate one-shot runtime-installation authority binding the exact source
   byte objects and the reviewed installer/helper identity;
5. one installation execution;
6. post-install verification and evidence review; and
7. independent Step-4 closure review.

No step may be collapsed. This governance publication does not close Step 4.
Duplicate freshness remains mutable and is not queried here; its later
revalidation remains separately governed. Step 5 remains `NOT AUTHORIZED`.

Production PostgreSQL contacted: `NO`.

Production PostgreSQL writes: `0`.

Harness invoked: `NO`.

Controlled callable invoked: `NO`.

Candidate and item inserts: `0`.

Inventory and stock mutations: `0`.

`authorization.json` created: `NO`.
