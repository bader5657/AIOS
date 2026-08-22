# History Scan, Secret Response, and Journal Privacy Decision

## Bounded Git-history scan

Stage 9.2.4 includes all reachable repository history, not only the current
tree. A future static scan may check filenames and content patterns for:

- private-key headers;
- Telegram token-like and common API credential formats;
- credential-bearing PostgreSQL URLs;
- real production environment files;
- database dump/backup artifacts;
- production business-file/media/archive patterns; and
- log, rollback, runtime, or temporary artifacts.

Output is limited to commit identity, repository path, and classification:
`confirmed secret`, `likely secret`, `placeholder/example`, or
`false positive`. Matching content must never be printed. History rewrite is
not authorized.

If a real credential is proven in Git/history or journal output, stop with:

`STAGE 9.2.4 SECRET EXPOSURE RESPONSE REQUIRED`

and record:

`CREDENTIAL ROTATION REQUIRED`

Removal or ignore rules alone are not an adequate response to a committed
credential. Rotation and any history remediation require separate authority.
The present accepted finding remains `NONE DETECTED`; proactive rotation is
not authorized.

## Journal privacy classification

Recent journal review is limited to category presence/absence and must
separate:

- `CONTEXTUAL USER/BUSINESS METADATA`: Telegram user identifier, chat
  identifier, username, message metadata/text, and file metadata; from
- `AUTHENTICATION SECRET`: bot token, password, private key, credential-bearing
  DSN, or API secret.

Known contextual Telegram metadata is a bounded privacy/security finding. No
authentication-secret journal exposure is proven.

Decision:

`B — DOCUMENTED PRIVACY HARDENING DEFERRED`

Current authority prohibits secrets and protected runtime files from entering
Git/source; it does not define a complete journal minimization/redaction
contract. Contextual metadata therefore remains an explicit future
privacy/logging-hardening backlog item. The finding is not waived, but Stage
9.2.4 does not redesign logging or change journald/service behavior.
