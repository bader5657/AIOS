# Authority, Baseline, Target, and Operator Trace

## Authority chain

1. Stage 9.1.1 defined the Blueprint-required `aios.service` implementation
   contract in
   `docs/core-platform/stage-9.1.1-aios-service-implementation-contract/`.
   Its authority commit is `8ab4bfe`; its activation merge established the
   baseline `038eee831ba21dd3d7d405bd86c73fbc1ff9dd21`.
2. Stage 9.1.2 approved the concrete unit, runtime-user, environment, restart,
   shutdown, enablement, observability, and single-polling policy in
   `docs/core-platform/stage-9.1.2-systemd-service-policy/`. Its authority
   commit is `8b10d29`; the following implementation-approval baseline is
   `1af6aa506c777b883ca0bbaeadb46c74ea9b3248`.
3. Stage 9.2.1 authorized, implemented, verified, accepted, and closed the
   repository service artifact. The implementation commit is
   `617997e24573b185f236c189967ffcf547295f3f`, implementation merge is
   `8796766703945445c7a887e7de425589765c29b2`, and closure activation baseline
   is `a8f215ff83401a196f69b8397b7c1ec241fb4c07`.
4. Stage 9.2.2 controlled VPS verification authority was activated by merge
   `4168e098612c930215a49028d4ca9fc200d21cfd`. Subsequent governance approvals
   reconciled source deployment, bounded generated residue, runtime
   preparation, and the PostgreSQL loopback endpoint. The exact closure
   baseline after PR #89 is
   `e02f31234e3f852b632536bbf39c135ead9fca8b`.

No lower-level record overrides the Stage 9.1.1 contract or Stage 9.1.2 policy.
The observed operational state conforms to both and to the Stage 9.2.1
artifact.

## Target and authenticated operator model

- SSH/VPS identity: `aiosadmin@aios-prod-01`
- Verified host identity: `aios-prod-01`
- Operational actor: authenticated `aiosadmin` login using controlled
  privilege elevation only where installation or lifecycle operations
  required root authority.
- Runtime service identity and process ownership: systemd is the sole
  production process owner under the approved unit policy.
- Installed unit: `/etc/systemd/system/aios.service`
- Repository artifact: `deploy/systemd/aios.service`
- Approved and verified Git blob:
  `ace763735417d196f3841fb526d76b4e593fbbc3`

The installed unit was reconciled to the approved artifact, followed by
`daemon-reload` and effective-service verification. No alternate unit or
alternate polling owner remained active.

## Source deployment alignment

- Source checkout: `/opt/aios-src`
- Approved deployed commit:
  `4168e098612c930215a49028d4ca9fc200d21cfd`
- Active module: `core.adapters.telegram.main`
- Application semantic changes during operational verification: `NONE`

The source identity used by production therefore matches the exact approved
Stage 9.2.2 deployment commit. Closure documentation does not alter that
checkout.
