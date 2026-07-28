"""Shared exceptions for the domain layer."""


class DomainError(Exception):
    """Base exception for domain failures."""


class DomainValidationError(DomainError):
    """Raised for invalid domain input or value construction."""


class DomainInvariantError(DomainError):
    """Raised when an operation would violate a domain invariant."""
