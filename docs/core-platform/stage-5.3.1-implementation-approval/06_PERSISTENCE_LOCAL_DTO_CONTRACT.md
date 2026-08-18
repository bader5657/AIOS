# Persistence-Local DTO Contract

The following frozen/slotted dataclass-equivalent transport types are approved
inside `core/registry/postgres_registry.py`:

- `RegistryPersistenceInput`;
- `RegistryPersistenceRow`; and
- `RegistryUpdate`.

They are persistence-local, non-canonical, non-domain, non-business, and not
Stage-wide vocabulary. They must not be named `RegistryEntry` or exported as a
domain contract.

`RegistryPersistenceInput` contains exactly the register input fields.
`RegistryPersistenceRow` contains `record_id` plus all persisted fields.
`RegistryUpdate` contains only mutable optional patch fields and must
distinguish omitted fields from explicit null values using a private/internal
sentinel that creates no public domain concept.
