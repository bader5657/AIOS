"""Review-only material-receipt application facade."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import PurePosixPath
import re
from uuid import UUID

from core.material_receipts.errors import MaterialReceiptError
from core.material_receipts.models import ReceiptCandidateRequest, ReceiptForReview

from .ports import CandidateReviewPort, RetainedEvidenceVerifier
from .results import ReviewApplicationError, ReviewFailureCode


_MANIFEST_ROOT = PurePosixPath("/opt/aios/data/documents/manifests")
_ACTOR_REFERENCE = re.compile(
    r"\A(?:operator|reviewer):[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z"
)


def _is_uuid_json_name(name: str) -> bool:
    if not name.endswith(".json"):
        return False
    try:
        identifier = UUID(name[:-5])
    except (ValueError, AttributeError):
        return False
    return str(identifier) == name[:-5]


@dataclass(frozen=True, slots=True)
class SourceContext:
    """Canonical identity for retained Universal Ingestion evidence."""

    manifest_reference: str
    registry_record_id: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.manifest_reference, str):
            raise ValueError("manifest_reference must be canonical manifest identity")
        if self.manifest_reference != self.manifest_reference.strip():
            raise ValueError("manifest_reference must be canonical")
        reference = PurePosixPath(self.manifest_reference)
        if (
            not reference.is_absolute()
            or str(reference) != self.manifest_reference
            or reference.parent != _MANIFEST_ROOT
            or not _is_uuid_json_name(reference.name)
        ):
            raise ValueError("manifest_reference must be canonical manifest identity")
        if self.registry_record_id is not None and (
            type(self.registry_record_id) is not int or self.registry_record_id <= 0
        ):
            raise ValueError("registry_record_id must be a positive integer or None")


@dataclass(frozen=True, slots=True)
class ActorContext:
    """Canonical review/audit identity with no operational authority."""

    actor_reference: str

    def __post_init__(self) -> None:
        if (
            not isinstance(self.actor_reference, str)
            or _ACTOR_REFERENCE.fullmatch(self.actor_reference) is None
        ):
            raise ValueError(
                "actor_reference must match operator:<id> or reviewer:<id>"
            )


class ReviewFacade:
    """Expose exactly candidate create, revise, and retrieval orchestration."""

    __slots__ = ("__candidate_port", "__evidence_verifier")

    def __init__(
        self,
        candidate_port: CandidateReviewPort,
        evidence_verifier: RetainedEvidenceVerifier,
    ) -> None:
        self.__candidate_port = candidate_port
        self.__evidence_verifier = evidence_verifier

    async def create_candidate(
        self, request: ReceiptCandidateRequest, source_context: SourceContext
    ) -> ReceiptForReview:
        self._require_request(request)
        if type(source_context) is not SourceContext:
            raise ReviewApplicationError(ReviewFailureCode.INVALID_REVIEW_REQUEST)
        if request.source_asset_reference != source_context.manifest_reference:
            raise ReviewApplicationError(ReviewFailureCode.SOURCE_IDENTITY_CONFLICT)
        self._require_retained(source_context)
        bound_request = replace(
            request, source_asset_reference=source_context.manifest_reference
        )
        try:
            result = await self.__candidate_port.create_candidate(bound_request)
        except ReviewApplicationError:
            raise
        except MaterialReceiptError as exc:
            raise self._candidate_error(exc) from exc
        except Exception as exc:
            raise ReviewApplicationError(ReviewFailureCode.INTERNAL_FAILURE) from exc
        return self._require_result_source(
            result, source_context.manifest_reference
        )

    async def revise_candidate(
        self,
        request: ReceiptCandidateRequest,
        expected_version: int,
        actor_context: ActorContext,
    ) -> ReceiptForReview:
        self._require_request(request)
        self._require_actor(actor_context)
        if type(expected_version) is not int or expected_version < 1:
            raise ReviewApplicationError(ReviewFailureCode.INVALID_REVIEW_REQUEST)
        try:
            current = await self.__candidate_port.get_candidate_for_review(
                request.receipt_id
            )
        except ReviewApplicationError:
            raise
        except MaterialReceiptError as exc:
            raise self._candidate_error(exc) from exc
        except Exception as exc:
            raise ReviewApplicationError(ReviewFailureCode.INTERNAL_FAILURE) from exc
        try:
            current_context = SourceContext(current.source_asset_reference)
        except (AttributeError, TypeError, ValueError) as exc:
            raise ReviewApplicationError(
                ReviewFailureCode.SOURCE_IDENTITY_INVALID
            ) from exc
        self._require_retained(current_context)
        if request.source_asset_reference != current.source_asset_reference:
            raise ReviewApplicationError(ReviewFailureCode.SOURCE_IDENTITY_CONFLICT)
        try:
            result = await self.__candidate_port.revise_candidate(
                request, expected_version
            )
        except ReviewApplicationError:
            raise
        except MaterialReceiptError as exc:
            raise self._candidate_error(exc) from exc
        except Exception as exc:
            raise ReviewApplicationError(ReviewFailureCode.INTERNAL_FAILURE) from exc
        return self._require_result_source(result, current.source_asset_reference)

    async def get_candidate_for_review(
        self, receipt_id: UUID, actor_context: ActorContext
    ) -> ReceiptForReview:
        self._require_actor(actor_context)
        if type(receipt_id) is not UUID:
            raise ReviewApplicationError(ReviewFailureCode.INVALID_REVIEW_REQUEST)
        try:
            result = await self.__candidate_port.get_candidate_for_review(receipt_id)
        except ReviewApplicationError:
            raise
        except MaterialReceiptError as exc:
            raise self._candidate_error(exc) from exc
        except Exception as exc:
            raise ReviewApplicationError(ReviewFailureCode.INTERNAL_FAILURE) from exc
        return self._require_result_source(result)

    def _require_result_source(
        self, result: ReceiptForReview, expected: str | None = None
    ) -> ReceiptForReview:
        try:
            source_context = SourceContext(result.source_asset_reference)
        except (AttributeError, TypeError, ValueError) as exc:
            raise ReviewApplicationError(
                ReviewFailureCode.SOURCE_IDENTITY_INVALID
            ) from exc
        if expected is not None and result.source_asset_reference != expected:
            raise ReviewApplicationError(ReviewFailureCode.SOURCE_IDENTITY_CONFLICT)
        self._require_retained(source_context)
        return result

    def _require_retained(self, source_context: SourceContext) -> None:
        try:
            retained = self.__evidence_verifier.is_retained(source_context)
        except Exception as exc:
            raise ReviewApplicationError(ReviewFailureCode.INTERNAL_FAILURE) from exc
        if retained is not True:
            raise ReviewApplicationError(ReviewFailureCode.SOURCE_IDENTITY_INVALID)

    @staticmethod
    def _require_request(request: object) -> None:
        if type(request) is not ReceiptCandidateRequest:
            raise ReviewApplicationError(ReviewFailureCode.INVALID_REVIEW_REQUEST)

    @staticmethod
    def _require_actor(actor_context: object) -> None:
        if type(actor_context) is not ActorContext:
            raise ReviewApplicationError(ReviewFailureCode.INVALID_REVIEW_REQUEST)

    @staticmethod
    def _candidate_error(exc: MaterialReceiptError) -> ReviewApplicationError:
        return ReviewApplicationError(
            ReviewFailureCode.CANDIDATE_OPERATION_FAILED,
            candidate_code=exc.code,
        )
