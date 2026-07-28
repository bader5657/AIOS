"""Customer name value object."""

from dataclasses import dataclass

from core.domain.exceptions import DomainValidationError
from core.domain.value_object import ValueObject


@dataclass(frozen=True)
class CustomerName(ValueObject):
    """Name of a Customer."""

    value: str

    def __hash__(self) -> int:
        return hash((type(self), self.value))

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise DomainValidationError("value must be a str")
        if not self.value:
            raise DomainValidationError("value must not be empty")
        if not self.value.strip():
            raise DomainValidationError("value must not contain only whitespace")
        if self.value != self.value.strip():
            raise DomainValidationError(
                "value must not have leading or trailing whitespace"
            )
        if len(self.value) < 2:
            raise DomainValidationError("value must contain at least 2 characters")
