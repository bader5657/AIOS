# Stage 0.33B-FP Operator Authority and Password Boundary

Date: 2026-08-28 (Asia/Jakarta)

## Purpose and baseline

This package governs one separate human-operator infrastructure preparation step
for the Stage 0.33B-D execution-evidence root. It is documentation only and does
not provision a directory, contact production PostgreSQL, execute a query or
migration, modify production configuration, restart a service, or activate
production traffic.

Stage 0.33B-A PR #249 remains open and unmerged at reviewed head
`6aa72265f582b32759c80c51aa4b64ed224015dd`. Its deterministic four-table locks,
fixed lock order, first-launch one-shot consumption boundary, evidence format and
durability, transaction/rollback, Migration 0005 artifact, and target identity
contracts are closed and unchanged. Its sole remaining blocker is practical
provisioning beneath `/opt/aios/runtime/intelligence`, observed as a real
non-symlink `root:root` directory with mode `0755`. Non-interactive sudo is not
available; Migration 0005 authority remains UNCONSUMED.

## Human operator boundary

Only the authenticated human Project Owner or authorized VPS operator may
perform the two exact privileged operations frozen in this package, and only
after this package receives independent review PASS and is merged unchanged.
The operator runs the commands manually in the local VPS terminal.

If sudo requests a password, the operator enters it directly into that terminal.
The password remains outside AIOS, Codex, ChatGPT, Git, logs, and execution
evidence. Codex must never request, accept, receive, print, capture, log, store,
pipe, or otherwise handle it; must not use `sudo -S` or `expect`; and must not
modify sudoers, create passwordless sudo, or open a root shell.

## Narrow authority and prohibitions

The Project Owner approves only the two exact `/usr/bin/install` commands in
`01_EXACT_PROVISIONING_COMMANDS_AND_PATH_CONTRACT.md`, solely to establish the
Stage 0.33B-D evidence root. This does not authorize general root access,
Migration 0005 or 0004, production PostgreSQL access, service restart,
`runtime.env` modification, candidate activation, Telegram changes, or Universal
Ingestion changes.

The authority explicitly prohibits `sudo bash`, `sudo sh`, `sudo su`, `sudo -i`,
`sudo python`, `sudo tee`, `sudo sed`, `sudo rm`, `sudo mv`, `sudo cp`, recursive
`chown` or `chmod`, `sudo find`, arbitrary-path `sudo mkdir`, sudoers modification,
and any other privileged filesystem command. There is no general root shell or
arbitrary sudo authority.

Operator provisioning and the later non-privileged write probe do not consume
Migration 0005 authority. That authority remains UNCONSUMED until the first exact
Stage 0.33B-D production Docker/`psql` launch attempt governed by a later-active
PR #249 contract.

## Project Owner approval

The Project Owner approves publication and later human execution of only the two
exact privileged install commands, subject to all path gates and independent
review/merge conditions. The Owner understands that any sudo password must be
entered directly by the operator in the VPS terminal and never disclosed to
AIOS, Codex, or ChatGPT.

Publication safety: production PostgreSQL contacted NO; sudo executed NO;
production filesystem changed NO; Migration 0005 and 0004 NOT EXECUTED;
`runtime.env` and services UNCHANGED; Telegram and Universal Ingestion UNCHANGED;
candidate activation NO.
