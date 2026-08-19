# Project Owner Approval, Publication, and Activation

I, as Project Owner, approve one controlled Stage 9.2.2 production/VPS
verification cycle limited to installation and verification of the
already-approved `aios.service`, including one controlled reboot only after all
pre-reboot gates pass.

I do not authorize runtime code changes, database/schema changes, migrations,
Docker Compose changes, secret changes, business-data changes, additional
services, duplicate polling processes, or Brain/LLM deployment. Rollback must
remain service-local.

Upon normal merge of this governance-only package, the approval is published
and active. The executor may then begin the separately reported controlled VPS
execution using only this plan. Merge does not itself install, enable, start,
stop, reboot, connect to Telegram, query PostgreSQL, or otherwise touch the
production host.

The active approval state is:

`STAGE 9.2.2 VPS VERIFICATION APPROVED — READY FOR CONTROLLED EXECUTION`
