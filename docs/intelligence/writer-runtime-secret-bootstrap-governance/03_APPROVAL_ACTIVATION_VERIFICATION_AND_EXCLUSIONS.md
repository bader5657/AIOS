# Approval, Activation, Verification, and Exclusions

## Project Owner approval package

Approval freezes:

- the two exact variable names and independent 256-bit-or-greater secrets;
- one manually authenticated, root-mediated, fixed-purpose bootstrap;
- no persistent sudoers capability and no writable-runtime-env relaxation;
- root-owned same-directory temporary files, locking, fsync, atomic rename, and
  byte-preserving unrelated entries;
- no persistent plaintext backup;
- in-memory/private-pipe PostgreSQL password delivery with log-safety gate;
- secret-first ordering, transactional DB provisioning, authentication probes,
  and fail-closed restoration/NOLOGIN compensation;
- removal of the temporary helper and all transient artifacts.

Before reauthorization, evidence must prove target file and parent metadata,
same-filesystem atomic replacement capability, interactive root execution path,
reviewed helper hash/source, no secret-output channel, server log safety, and
the complete recovery path. Evidence records status, key names, presence,
owner/group/mode, and authentication outcome only.

## Activation boundary

This governance package is documentation only. It generates no credential,
installs no helper, changes no sudoers/file/database state, and executes no
provisioning. After its PR merges, a separate authority must approve the exact
reviewed helper artifact and exactly one root-mediated production bootstrap and
writer-role provisioning session.

Receipt/posting runtime services, credential consumption by application code,
business data population, stock mutation, Telegram, OCR, LLM, and inference
remain unauthorized even after identities exist.

The next official action is governance approval/merge followed by a separately
scoped helper implementation review and controlled execution reauthorization.
