"""Base value object contract."""

from __future__ import annotations

from abc import ABC, abstractmethod


class ValueObject(ABC):
    """Immutable domain object defined entirely by its values."""

    __slots__ = ()

    @abstractmethod
    def __init__(self) -> None:
        """Initialize a concrete immutable value object."""
