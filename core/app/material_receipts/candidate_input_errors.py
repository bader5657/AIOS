"""Bounded failures for the Stage 0.31A candidate-input boundary."""

from __future__ import annotations

from enum import Enum


class CandidateInputFailureCode(str, Enum):
    INVALID_INGESTION_EVIDENCE = "INVALID_INGESTION_EVIDENCE"
    RETAINED_MANIFEST_INVALID = "RETAINED_MANIFEST_INVALID"
    TRUSTED_FACTS_INVALID = "TRUSTED_FACTS_INVALID"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"
    DECIMAL_POLICY_INVALID = "DECIMAL_POLICY_INVALID"
    PACKAGING_FORMULA_INVALID = "PACKAGING_FORMULA_INVALID"
    ID_GENERATION_INVALID = "ID_GENERATION_INVALID"


class CandidateInputError(ValueError):
    """Sanitized validation failure without source or infrastructure detail."""

    def __init__(self, code: CandidateInputFailureCode) -> None:
        self.code = code
        super().__init__(code.value)
