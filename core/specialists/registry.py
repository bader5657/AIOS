from dataclasses import dataclass

from core.router.command_router import RouteName, RouteResult


@dataclass(frozen=True, slots=True)
class SpecialistDefinition:
    """Metadata describing one AIOS specialist."""

    route: RouteName
    name: str
    description: str
    handler_key: str
    enabled: bool = True


class SpecialistRegistry:
    """Stores and resolves specialists by command route."""

    def __init__(self) -> None:
        self._specialists: dict[RouteName, SpecialistDefinition] = {}

    def register(self, specialist: SpecialistDefinition) -> None:
        if specialist.route in self._specialists:
            raise ValueError(
                f"Specialist for route '{specialist.route.value}' "
                "is already registered."
            )

        self._specialists[specialist.route] = specialist

    def get(self, route: RouteName) -> SpecialistDefinition | None:
        specialist = self._specialists.get(route)

        if specialist is None or not specialist.enabled:
            return None

        return specialist

    def resolve(
        self,
        route_result: RouteResult,
    ) -> SpecialistDefinition | None:
        return self.get(route_result.route)

    def list_enabled(self) -> tuple[SpecialistDefinition, ...]:
        return tuple(
            specialist
            for specialist in self._specialists.values()
            if specialist.enabled
        )


def build_default_registry() -> SpecialistRegistry:
    """Build the default specialist registry for AIOS."""

    registry = SpecialistRegistry()

    registry.register(
        SpecialistDefinition(
            route=RouteName.MISSION,
            name="Mission Control",
            description="Menangani status sistem dan laporan operasional.",
            handler_key="mission.status",
        )
    )

    registry.register(
        SpecialistDefinition(
            route=RouteName.SHOEGABox_ADMIN,
            name="Shoegabox Admin",
            description="Menangani administrasi operasional Shoegabox.",
            handler_key="shoegabox.admin",
        )
    )

    registry.register(
        SpecialistDefinition(
            route=RouteName.CONTENT_FACTORY,
            name="Content Factory",
            description="Menangani perencanaan dan produksi konten.",
            handler_key="content.factory",
        )
    )

    registry.register(
        SpecialistDefinition(
            route=RouteName.HELP,
            name="AIOS Help",
            description="Menampilkan bantuan dan daftar perintah.",
            handler_key="system.help",
        )
    )

    return registry
