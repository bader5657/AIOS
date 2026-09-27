# Telegram authentication evidence retention

This implementation captures future challenge messages. It does not authenticate
the existing PR #305 attempt, merge governance, commission a process, or grant
production/recovery authority. A capture is not an authentication PASS.

## Receiver behavior and closed schema

Immediately before text normalization, the existing receiver projects only these
fields from a direct Telegram `Update.message` into canonical evidence:

```json
{
  "schema_version": "aios-telegram-owner-auth-evidence-v1",
  "update_id": 901,
  "message": {
    "message_id": 51,
    "from": {"id": 961959058, "username": "bagusder21"},
    "date": "2026-09-28T01:00:10.000000Z",
    "chat": {"id": 961959058, "type": "private"},
    "text": "AIOS-PO-AUTH-PR305-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
  "local_received_at_utc": "2026-09-28T01:00:10.123456Z"
}
```

The example is synthetic, not authentication evidence. Username is nullable when
absent. IDs are strict integers (booleans rejected). Timestamps are UTC RFC3339
with six fractional digits; Telegram's second-resolution date is represented with
zero microseconds. Unknown/missing fields and duplicate JSON keys at every level
are rejected. Only exact `AIOS-PO-AUTH-PR[1-9][0-9]*-[A-Za-z0-9_-]{43}` messages
are captured; whitespace and case are not normalized. The nonce format supports
32 random bytes encoded as unpadded URL-safe base64. Issuers must generate fresh,
cryptographically random nonces; this receiver does not issue challenges.

Canonical encoding uses `ensure_ascii=False`, `sort_keys=True`,
`separators=(",", ":")`, `allow_nan=False`, UTF-8 and exactly one trailing LF.
Validation compares the original bytes with their canonical re-encoding.
No tokens, headers, names, captions, arbitrary update extras, or unrelated messages
are retained in this evidence path. The event-loop handler prepares immutable
canonical bytes from the original Update **before normalization**, then offers
those bytes to a single dedicated filesystem worker. Persistence can finish after
normalized ingestion; fields are never reconstructed from a normalized manifest.

Admission is bounded to **one running job and zero waiting jobs**. A nonblocking
slot rejects excess authentication captures immediately (`REJECTED_CAPACITY`,
logged as `NOT_PUBLISHED: capacity exhausted`). No per-message asyncio task or
unbounded executor backlog is created. The slot remains occupied until the worker
finishes, including during stalled I/O; no timeout releases it prematurely.
Ordinary messages bypass the worker. Existing ingestion receives the original
message exactly once, whether admission succeeds, is rejected, or capture fails.
Capture never calls authentication or consumption. Generic failure/state messages
contain no Update contents, credentials, paths or exception details. There is no
automatic retry of rejected or failed captures.

## Storage and directory identity

Default archive: `/opt/aios/data/authentication-evidence/telegram/`.
Evidence filenames remain `<UUID>.<transport-SHA256>.json`; the hash includes LF.
Each publication retains `<filename>.attempt`, `<filename>.complete`, and a
permanent `<filename>.pending` preparation guard. Only `<filename>.commit` is the
final commit decision. The closed evidence schema remains unchanged. The marker,
guard, journal, certificate and directory anchor are separate private control
records. A certificate or prepared journal alone never authorizes authentication.

All path components are opened from `/` using directory descriptors with
`O_DIRECTORY | O_NOFOLLOW`. The walk rejects traversal, symlinks, non-directories,
and unsafe owners/permissions. Ancestors must be root/custodian-owned and not
otherwise writable; a root-owned sticky temporary ancestor is allowed for private
test archives. The archive, its parent and `consumed/` must be custodian-owned and
private (0700). Newly created components use 0700. Files use 0600.

Each descriptor pins device, inode, uid, gid and mode. These identities are checked
against `fstat` and no-follow, parent-descriptor-relative entry metadata throughout
the operation. Temporary creation, file reads, publication links, cleanup, syncing
and consumption are descriptor-relative. A replaced pathname cannot redirect I/O
into the replacement directory. An observed identity change fails closed.
Directory descriptors are registered for cleanup immediately after opening,
before the first `fstat`. File descriptors have an owning context before metadata
or stream-wrapper construction; wrappers do not independently own the descriptor.

The exclusive parent anchor
`/opt/aios/data/authentication-evidence/.telegram.auth-identity.json` retains the
entire directory chain and consumption-directory identity. The process also
remembers an initialized path's identities, refusing to establish a new namespace
if an ancestor or anchor disappears. The retained anchor detects archive and
consumption-directory replacement across process reopen/restart. Preserve the
anchor, its trusted parent, evidence, and consumption directory as one custody
boundary. Deleting/replacing that whole boundary is not supported recovery or
re-enrollment; hashes cannot defend against a custodian intentionally replacing
all trust metadata. Missing anchors in verification are always STOP.

## Publication outcomes and crash recovery

The protocol is monotonic: prepare and validate every bound artifact, then publish
one final decision. It never removes the guard, mutates a journal to COMMITTED,
or relies on an in-memory denial cache. The final marker is necessary, not advisory.

| Outcome | Meaning |
|---|---|
| `NOT_PUBLISHED` | The final payload name was not published. Provisional artifacts may exist; no final marker exists. |
| `PUBLISHED_DURABILITY_UNCERTAIN` | Provisional payload/certificate may exist, but final marker publication was not attempted. Authentication is impossible, even if diagnostic UNCERTAIN writes fail. |
| `COMMIT_RECOVERY_REQUIRED` | Final marker publication was attempted. Its outcome/durability needs inspection and recovery; this is neither an aborted attempt nor authentication PASS. A missing marker rejects. A surviving valid decision can be recovered as described below. |
| `DURABLY_PUBLISHED` | The final decision and all bindings passed validation, file/directory syncs and current-namespace checks. Capture alone is still not authentication PASS. |

### Authoritative commit schema

`aios-telegram-auth-commit-v1` is a closed canonical UTF-8 JSON object with exactly:

- `schema_version`, `state` (exactly `COMMITTED`), `attempt_id` (payload filename),
  `challenge_sha256`, `telegram_user_id`, and `committed_at_utc`.
- `directory_identity` and `namespace_identities`: pinned device/inode/uid/gid/mode
  of the target directory and governed ancestor/consumption chain.
- `objects`: exactly `evidence`, `certificate`, `journal`, and `guard`. Each entry
  has exactly `filename`, `identity` (device/inode/uid/gid/mode), and `sha256`.
  For consumption publications, the `evidence` slot is the consumption receipt.

The verifier reconstructs the exact expected record from retained objects and
compares canonical bytes; missing/unknown/duplicate fields, altered identities,
noncanonical encodings, or differing hashes reject. Marker publication uses 0600,
UUID staging, O_EXCL/no-overwrite hard linking, pinned directory descriptors,
file fsync and parent fsync. The timestamp records preparation of the commit
decision; it never substitutes for Telegram `message.date` in authentication.

The journal retains exactly canonical PENDING then PREPARED entries using the
existing `aios-telegram-auth-attempt-v1` schema. The permanent guard retains the
exact PENDING entry. These are immutable prerequisites bound by the marker;
neither is independently an authorization record. Old PENDING/COMMITTED journals
and certificate-only records cannot pass this protocol. No backfill is provided.

### Finalization sequence

1. Exclusively create the attempt journal, write/fsync PENDING, then create/fsync
   the guard and parent. The exclusive journal also reserves the attempt name.
2. Stage/fsync and publish the payload and certificate without overwrite. Sync
   the directory, read back exact bytes, and validate pinned namespace identities
   before and after certificate publication.
3. Complete required provisional staging cleanup and directory sync. Append/fsync
   PREPARED. Validate all objects and construct the commit record binding their
   exact bytes, hashes, identities, numeric sender and challenge digest.
4. Stage/fsync the final marker. Repeat current-namespace/object checks and compare
   all bindings immediately before its descriptor-relative final hard link.
5. Publish `<filename>.commit`: this is the **irreversible commit decision**. From
   this point errors mean `COMMIT_RECOVERY_REQUIRED`, never an uncertain attempt
   that can later be promoted. The decision itself is not revoked or rewritten.
6. Validate the marker and all bound objects, fsync each and the parent, and
   revalidate current namespace identities and bytes. Only then return durable
   publication success. No guard retirement occurs. The marker staging alias is
   deliberately retained; no security-critical cleanup follows commitment.

Before step 5, any error or SIGKILL leaves no final marker. A diagnostic UNCERTAIN
append may fail too: rejection still follows from marker absence, with no
quarantine restoration or process memory required. Existing attempts are never
reopened for publication. Provisional and uncertain artifacts remain inspectable.

A crash/error during or after step 5 is an interrupted commit decision. A surviving
link alone cannot prove that the original parent's fsync returned. Every verifier
therefore runs the same recovery barrier: require the existing final marker,
validate its exact canonical bindings and current namespace, fsync all bound files
and the marker and parent, then recheck identities/bytes. Failure rejects before
challenge consumption. Recovery never creates a missing marker, repairs bytes,
changes journal states, retires guards, or retries publication. A lost link rejects;
a surviving valid decision becomes eligible only after this durability barrier.
An interruption after the marker is durable may thus be treated as committed even
if its publisher never returned. This is an explicit durable decision protocol,
not inference from a successful function return or a process-local lock.

Journal locks serialize live publishers/verifiers, but termination releases them
without changing the above rules. Namespace swaps fail current identity checks,
including on restart through the retained identity anchor. Restoring the exact
original custody namespace can recover an existing final decision; it cannot
create a decision for a provisional attempt. Namespace checks establish commit-time
objects; custody must preserve the entire archive afterward.

The crash suite uses SIGKILL and separate fresh Python interpreters for publication,
verification and replay. It tests missing-marker rejection across intermediate
steps, failed uncertainty diagnostics, pre-link termination, post-link recovery,
and post-durability termination. It also checks permanent guards, closed marker
schema, bound-object replacement and final-marker namespace swaps. These are
process-crash tests on the local filesystem, not a simulation of hardware falsely
acknowledging fsync or physical power-loss ordering.

## Verification and replay

The receiver never calls `verify_and_consume`. An explicitly authorized operator
can call that function with the trusted archive path and a `ChallengeBinding`
constructed from the previously issued challenge, not from received content.
The binding supplies exact challenge text, PR number, HEAD, approval UUID, expected
numeric sender ID, declared username and issue/expiry timestamps. The operator
must verify these inputs against the retained issuance record and current subject
before invoking it. This helper does not query GitHub or certify merge readiness.

Verification checks the closed canonical schema and filename digest, exact text,
numeric sender identity, exact username if present, and a private chat whose ID
equals the sender. Both Telegram time and local receipt must be in the challenge
window; the issue boundary permits Telegram's second precision, while local
receipt must be at or after the precise issue time. Verification can occur later
than expiry if the evidence was received within the window. A missing username
does not invent a verified display name; the receipt separates actual username
from the declared display username.

Only after all checks succeed does descriptor-relative, no-replace publication
create `consumed/<SHA256-of-challenge-text>.json`, its prepared journal, permanent
guard, completion certificate and authoritative final commit marker. The receipt binds source digest, numeric identity,
PR/HEAD, approval ID, validity window and disclosed `solo-project-owner-bootstrap`
roles. Exclusive journal creation permits at most one consumer. The anchored
consumption directory cannot be replaced to reset this check. Overloaded captures
and incomplete/uncertain evidence never enter challenge consumption.

If consumption publication is interrupted, do not report PASS: before the final
decision report failure/uncertainty; after attempting that decision report
COMMIT_RECOVERY_REQUIRED. Its retained attempt namespace conservatively reserves
the nonce against retry. Preserve the artifacts for custody inspection; do not
infer authentication from a provisional receipt or a failed function return. No failed identity/text/time/schema check writes
a consumption attempt. Restoring a renamed directory cannot remove the exclusive attempt reservation or
permit a second successful consumer. A consumption decision interrupted after final
marker publication is retained for custody inspection; a subsequent call does not
return a second successful consumption.

Filesystem custody is part of the trust boundary. Hashes do not authenticate a
hand-written file; accept only the existing receiver's controlled archive, never
an uploaded or copied JSON record. Old incomplete manifests fail the schema;
the previous challenge and its sources remain unchanged and unconsumed. Use a
new challenge after a separately approved deployment.

## Deployment and rollback

This PR does not deploy or restart production. Using capture requires deploying
the two receiver Python files and a separately authorized service restart. Confirm
the service account can create the dedicated archive under `/opt/aios/data`.
No database migration, configuration secret, new polling consumer, webhook, or
logging reconfiguration is required.

Rollback restores the **pre-feature** receiver under separate deployment approval
and restarts the host `aios.service` only if authorized. Keep the archive, identity
anchor, attempt journals, pending guards, completion certificates, final commit markers
and consumption records unchanged; a code-only
rollback leaves them intact. Do not use the superseded draft verifier from PR #306
HEADs `796c551`, `9a04954` or `2f9fb09`: they do not enforce this final commit contract
and must not verify retained evidence. While capture/verification is rolled back, no challenge may be
authenticated from a normalized manifest alone.

This change requires no database migration or new config/environment variable.
It creates private evidence/control files only when a future deployed receiver
admits a challenge. It does not migrate or promote old evidence; records without final commit markers are ineligible. Moving/restoring
archive directories with new inode/device identities is not a transparent rollback:
the identity checks deliberately STOP and require a separately reviewed custody
recovery decision. No namespace replacement/re-enrollment procedure is implemented
or authorized here; final-marker durability recovery preserves existing identities.
