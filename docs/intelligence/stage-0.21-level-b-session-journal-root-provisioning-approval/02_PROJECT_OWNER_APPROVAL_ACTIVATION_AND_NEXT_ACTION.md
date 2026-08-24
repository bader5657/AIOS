# Project Owner Approval, Activation, and Next Action

I, as Project Owner, authorize one-time provisioning of exactly:

`/opt/aios/runtime/intelligence/staging/level-b-sessions`

as the persistent root for Stage 0.21 Level B session evidence.

The directory must resolve within the approved staging hierarchy, be owned by
`aiosadmin:aiosadmin`, use mode `0750`, and must not be a symlink or replace an
existing non-directory object.

This authority permits creation of the directory only.

It does not authorize creation of a Level B session, session journal, provider
inference, runtime/service/network mutation, real user data, business data, or
Level C activation.

Publication requires a normal governance-only PR into `main`, without force or
history rewrite. Publication does not create the directory. After merge and
synchronized clean-main audit, authority activates as:

`STAGE 0.21 LEVEL B JOURNAL ROOT PROVISIONING APPROVED — READY FOR CONTROLLED DIRECTORY CREATION`

The next official action is one controlled provisioning task: repeat the path
and target inspection, create the exact directory only if absent, perform the
bounded static post-validation, return evidence, and stop. Successful
provisioning removes only the storage prerequisite. First live Level B session
authority remains separately governed and is not granted here.
