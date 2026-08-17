from dataclasses import asdict, dataclass
from typing import Any


class CustomerValidationError(ValueError):
    """Raised when customer data is incomplete or invalid."""


def _clean(value: str | None) -> str:
    return " ".join((value or "").strip().split())


@dataclass(slots=True)
class CustomerDraft:
    """Customer data collected before confirmation and persistence."""

    name: str = ""
    address: str = ""
    city: str = ""
    notes: str = ""

    def set_name(self, value: str | None) -> None:
        name = _clean(value)

        if len(name) < 2:
            raise CustomerValidationError(
                "Nama pelanggan minimal 2 karakter."
            )

        self.name = name

    def set_address(self, value: str | None) -> None:
        address = _clean(value)

        if len(address) < 5:
            raise CustomerValidationError(
                "Alamat pelanggan minimal 5 karakter."
            )

        self.address = address

    def set_city(self, value: str | None) -> None:
        city = _clean(value)

        if len(city) < 2:
            raise CustomerValidationError(
                "Kota pelanggan minimal 2 karakter."
            )

        self.city = city

    def set_notes(self, value: str | None) -> None:
        self.notes = _clean(value)

    def missing_fields(self) -> tuple[str, ...]:
        missing: list[str] = []

        if not self.name:
            missing.append("name")

        if not self.address:
            missing.append("address")

        if not self.city:
            missing.append("city")

        return tuple(missing)

    @property
    def is_complete(self) -> bool:
        return not self.missing_fields()

    def validate(self) -> None:
        missing = self.missing_fields()

        if missing:
            raise CustomerValidationError(
                "Data pelanggan belum lengkap: "
                + ", ".join(missing)
            )

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)

    def confirmation_text(self) -> str:
        self.validate()

        notes = self.notes or "-"

        return (
            "Konfirmasi data pelanggan:\n\n"
            f"Nama    : {self.name}\n"
            f"Alamat  : {self.address}\n"
            f"Kota    : {self.city}\n"
            f"Catatan : {notes}\n\n"
            "Simpan data ini? Ya / Tidak"
        )
