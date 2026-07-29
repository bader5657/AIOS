import unittest

from core.router.command_router import RouteName, normalize_command, route_command


class NormalizeCommandTests(unittest.TestCase):
    def test_normalizes_case_and_spaces(self):
        self.assertEqual(
            normalize_command("  CATAT   PELANGGAN  "),
            "catat pelanggan",
        )

    def test_none_becomes_empty_string(self):
        self.assertEqual(normalize_command(None), "")


class CommandRouterTests(unittest.TestCase):
    def test_routes_status_to_mission(self):
        result = route_command("status")
        self.assertEqual(result.route, RouteName.MISSION)

    def test_routes_daily_report_to_mission(self):
        result = route_command("laporan hari ini")
        self.assertEqual(result.route, RouteName.MISSION)

    def test_routes_customer_command_to_shoegabox(self):
        result = route_command("catat pelanggan baru")
        self.assertEqual(result.route, RouteName.SHOEGABox_ADMIN)

    def test_routes_order_command_to_shoegabox(self):
        result = route_command("tolong catat order")
        self.assertEqual(result.route, RouteName.SHOEGABox_ADMIN)

    def test_routes_content_command_to_factory(self):
        result = route_command("buat konten youtube")
        self.assertEqual(result.route, RouteName.CONTENT_FACTORY)

    def test_routes_help(self):
        result = route_command("bantuan")
        self.assertEqual(result.route, RouteName.HELP)

    def test_routes_unknown_command(self):
        result = route_command("cuaca besok bagaimana")
        self.assertEqual(result.route, RouteName.UNKNOWN)
        self.assertEqual(result.confidence, 0.0)

    def test_empty_command_is_unknown(self):
        result = route_command("")
        self.assertEqual(result.route, RouteName.UNKNOWN)
        self.assertEqual(result.reason, "empty_command")


if __name__ == "__main__":
    unittest.main()
