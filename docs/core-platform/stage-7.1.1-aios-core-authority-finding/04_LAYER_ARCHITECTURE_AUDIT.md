# Layer Architecture Audit

AIOS Core occupies the Core Layer. The active extension assigns Route from the
Event Engine boundary to AIOS Core, ending at the Brain boundary, and prohibits
AIOS Core from depending on Event Engine to own delivery. Brain and Specialist
Layers are not Route producers or consumers.

The same authority explicitly defines no services, behavior, implementation
ownership, runtime dependency, API, routing algorithm, or implementation
contract. Input, output, allowed dependencies, and runtime behavior otherwise
remain unresolved.
