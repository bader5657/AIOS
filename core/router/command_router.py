from dataclasses import dataclass
from enum import Enum


class RouteName(str, Enum):
    MISSION = "mission"
    SHOEGABox_ADMIN = "shoegabox_admin"
    CONTENT_FACTORY = "content_factory"
    HELP = "help"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class RouteResult:
    route: RouteName
    command: str
    confidence: float
    reason: str


MISSION_KEYWORDS = (
    "status",
    "laporan",
    "laporan hari ini",
    "mission",
    "kondisi sistem",
)

SHOEGABox_KEYWORDS = (
    "catat pelanggan",
    "catat order",
    "catat produk",
    "catat transaksi",
    "catat bahan",
    "hitung hpp",
    "utang",
    "piutang",
)

CONTENT_KEYWORDS = (
    "buat konten",
    "konten youtube",
    "konten tiktok",
    "konten instagram",
    "buat skrip",
    "buat naskah",
)

HELP_KEYWORDS = (
    "help",
    "bantuan",
    "menu",
    "perintah",
)


def normalize_command(text: str | None) -> str:
    if not text:
        return ""

    return " ".join(text.strip().lower().split())


def _contains_any(command: str, keywords: tuple[str, ...]) -> str | None:
    for keyword in keywords:
        if keyword in command:
            return keyword

    return None


def route_command(text: str | None) -> RouteResult:
    command = normalize_command(text)

    if not command:
        return RouteResult(
            route=RouteName.UNKNOWN,
            command=command,
            confidence=0.0,
            reason="empty_command",
        )

    matched = _contains_any(command, HELP_KEYWORDS)
    if matched:
        return RouteResult(
            route=RouteName.HELP,
            command=command,
            confidence=1.0,
            reason=f"matched:{matched}",
        )

    matched = _contains_any(command, SHOEGABox_KEYWORDS)
    if matched:
        return RouteResult(
            route=RouteName.SHOEGABox_ADMIN,
            command=command,
            confidence=1.0,
            reason=f"matched:{matched}",
        )

    matched = _contains_any(command, CONTENT_KEYWORDS)
    if matched:
        return RouteResult(
            route=RouteName.CONTENT_FACTORY,
            command=command,
            confidence=1.0,
            reason=f"matched:{matched}",
        )

    matched = _contains_any(command, MISSION_KEYWORDS)
    if matched:
        return RouteResult(
            route=RouteName.MISSION,
            command=command,
            confidence=1.0,
            reason=f"matched:{matched}",
        )

    return RouteResult(
        route=RouteName.UNKNOWN,
        command=command,
        confidence=0.0,
        reason="no_rule_matched",
    )
