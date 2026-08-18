# Immutability and Domain Separation

The Event Engine reads the approved envelope boundary without assigning to it,
mutating its DomainEvent, reconstructing domain facts, or generating identity or
timestamps. Dependency direction is only `core/event → core/domain`; the reverse
direction is absent.

Stage 6.2.2 separation remains fully preserved.
