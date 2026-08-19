# Core Failure, Exception, and Preservation

In the conforming same-valid-envelope path, Core `INVALID_INPUT` is unreachable.
Its primary proof remains unchanged Stage 7 unit evidence. The integration test
must not corrupt the end-to-end envelope to manufacture invalid input. A
legitimate injected bounded Core result may verify projection only if it does
not imply production should produce that state.

For a bounded Core non-success:

- `route_handoff_ready=False`;
- no Brain execution occurs;
- Event Engine completed result remains completed;
- Registry row, original, metadata, and Manifest remain intact; and
- no compensation, rollback, retry, or failure-code conversion occurs.

An unexpected `AIOSCore.route()` exception propagates through the normal caller
contract after successful Event Engine completion. No readiness is returned or
falsely claimed, upstream completed state remains intact, and no global
exception mapping, compensation, or retry is introduced.
