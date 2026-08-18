# Invalid and No-Handler Containment

Invalid input returns failure with count zero and `INVALID_ENVELOPE`, invokes no
handler, and performs no retry. A later explicit valid invocation succeeds.

A valid envelope with no matching registration returns failure with count zero
and `NO_HANDLER`, never silent success, and performs no retry. After explicit
handler registration, a later independent invocation succeeds.
