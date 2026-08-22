"""Provider-neutral abstraction contracts owned by AIOS Brain."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from core.brain.inference_contracts import (
    InferenceCapability,
    InferenceRequest,
    InferenceResult,
)


MAX_PROVIDER_IDENTIFIER_LENGTH = 128


class ProviderRuntimeKind(str, Enum):
    """Operational classification without execution authority."""

    LOCAL = "local"
    REMOTE = "remote"


def _validate_identifier(name: str, value: object) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    if not value or value.isspace():
        raise ValueError(f"{name} must not be blank")
    if len(value) > MAX_PROVIDER_IDENTIFIER_LENGTH:
        raise ValueError(
            f"{name} exceeds {MAX_PROVIDER_IDENTIFIER_LENGTH} characters"
        )
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise ValueError(f"{name} contains an ASCII control character")


@dataclass(frozen=True, slots=True)
class ProviderDescriptor:
    """Immutable metadata for one statically configured provider/model."""

    provider_id: str
    model_id: str
    runtime_kind: ProviderRuntimeKind
    capabilities: tuple[InferenceCapability, ...]

    def __post_init__(self) -> None:
        _validate_identifier("provider_id", self.provider_id)
        _validate_identifier("model_id", self.model_id)
        if not isinstance(self.runtime_kind, ProviderRuntimeKind):
            raise TypeError("runtime_kind must be a ProviderRuntimeKind")
        if type(self.capabilities) not in (list, tuple):
            raise TypeError("capabilities must be a list or tuple")
        capabilities = tuple(self.capabilities)
        if any(
            type(capability) is not InferenceCapability
            for capability in capabilities
        ):
            raise TypeError("capabilities must contain InferenceCapability values")
        expected = (InferenceCapability.STRUCTURED_INFERENCE,)
        if capabilities != expected:
            raise ValueError(
                "capabilities must contain exactly STRUCTURED_INFERENCE"
            )
        object.__setattr__(self, "capabilities", capabilities)


class InferenceProvider(ABC):
    """Abstract boundary for one bounded provider inference invocation."""

    @property
    @abstractmethod
    def descriptor(self) -> ProviderDescriptor:
        """Return immutable sanitized identity and capability metadata."""

    @abstractmethod
    async def infer(self, request: InferenceRequest) -> InferenceResult:
        """Execute one bounded request and return one provider-neutral result."""
