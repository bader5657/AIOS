# Runtime Correction Stop Condition

No runtime correction is pre-authorized. If a mandatory test demonstrates that
active authority is violated, implementation must stop and report exactly:

`STAGE 6.4.1 RUNTIME CORRECTION APPROVAL REQUIRED`

The report must identify the failing behavior, violated authority, exact runtime
file required, and smallest correction scope. No runtime patch may be made
under this approval.
