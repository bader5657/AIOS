import unittest

from core.router.command_router import (
    RouteName,
    RouteResult,
    route_command,
)
from core.specialists.registry import (
    SpecialistDefinition,
    SpecialistRegistry,
    build_default_registry,
)


class SpecialistRegistryTests(unittest.TestCase):
    def test_register_and_get_specialist(self):
        registry = SpecialistRegistry()

        specialist = SpecialistDefinition(
            route=RouteName.MISSION,
            name="Mission Control",
            description="System status",
            handler_key="mission.status",
        )

        registry.register(specialist)

        self.assertEqual(registry.get(RouteName.MISSION), specialist)

    def test_duplicate_route_is_rejected(self):
        registry = SpecialistRegistry()

        specialist = SpecialistDefinition(
            route=RouteName.MISSION,
            name="Mission Control",
            description="System status",
            handler_key="mission.status",
        )

        registry.register(specialist)

        with self.assertRaises(ValueError):
            registry.register(specialist)

    def test_disabled_specialist_is_not_returned(self):
        registry = SpecialistRegistry()

        registry.register(
            SpecialistDefinition(
                route=RouteName.CONTENT_FACTORY,
                name="Content Factory",
                description="Content production",
                handler_key="content.factory",
                enabled=False,
            )
        )

        self.assertIsNone(registry.get(RouteName.CONTENT_FACTORY))

    def test_default_registry_contains_expected_specialists(self):
        registry = build_default_registry()

        self.assertIsNotNone(registry.get(RouteName.MISSION))
        self.assertIsNotNone(registry.get(RouteName.SHOEGABox_ADMIN))
        self.assertIsNotNone(registry.get(RouteName.CONTENT_FACTORY))
        self.assertIsNotNone(registry.get(RouteName.HELP))

    def test_router_result_resolves_to_specialist(self):
        registry = build_default_registry()
        route_result = route_command("catat pelanggan baru")

        specialist = registry.resolve(route_result)

        self.assertIsNotNone(specialist)
        self.assertEqual(specialist.handler_key, "shoegabox.admin")

    def test_unknown_route_has_no_specialist(self):
        registry = build_default_registry()

        route_result = RouteResult(
            route=RouteName.UNKNOWN,
            command="perintah asing",
            confidence=0.0,
            reason="no_rule_matched",
        )

        self.assertIsNone(registry.resolve(route_result))

    def test_list_enabled_excludes_disabled_specialists(self):
        registry = SpecialistRegistry()

        registry.register(
            SpecialistDefinition(
                route=RouteName.MISSION,
                name="Mission Control",
                description="System status",
                handler_key="mission.status",
            )
        )

        registry.register(
            SpecialistDefinition(
                route=RouteName.CONTENT_FACTORY,
                name="Content Factory",
                description="Content production",
                handler_key="content.factory",
                enabled=False,
            )
        )

        enabled = registry.list_enabled()

        self.assertEqual(len(enabled), 1)
        self.assertEqual(enabled[0].route, RouteName.MISSION)


if __name__ == "__main__":
    unittest.main()
