"""Optional phone display string; no dialing, ownership or country inference."""
import re
from core.domain.exceptions import DomainValidationError

def validate_phone(value: str | None) -> None:
    if value is None:
        return
    if type(value) is not str or len(value) > 64 or not re.fullmatch(r"\+?[0-9][0-9 ()-]*", value):
        raise DomainValidationError("phone must be a phone string of at most 64 characters or None")
    if value != value.strip():
        raise DomainValidationError("phone must not have leading or trailing whitespace")
