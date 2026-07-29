from core.registry.models import RegistryRecord


class Registry:
    """Basic registry implementation for Core Platform foundation."""

    def save(self, record: RegistryRecord) -> RegistryRecord:
        return record
