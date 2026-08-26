"""Transport-independent material-receipt candidate application service."""

from uuid import UUID

from .models import ReceiptCandidateRequest
from .repository import MaterialReceiptRepository


class MaterialReceiptService:
    def __init__(self, repository: MaterialReceiptRepository) -> None:
        self._repository = repository

    async def create_receipt_candidate(self, request: ReceiptCandidateRequest):
        return await self._repository.create_receipt_candidate(request)

    async def revise_receipt_candidate(self, request: ReceiptCandidateRequest,
                                       expected_version: int):
        return await self._repository.revise_receipt_candidate(request, expected_version)

    async def get_receipt_for_review(self, receipt_id: UUID):
        return await self._repository.get_receipt_for_review(receipt_id)

    async def confirm_receipt(self, receipt_id: UUID, expected_version: int,
                              actor_reference: str):
        return await self._repository.confirm_receipt(
            receipt_id, expected_version, actor_reference
        )

    async def reject_receipt(self, receipt_id: UUID, expected_version: int,
                             actor_reference: str):
        return await self._repository.reject_receipt(
            receipt_id, expected_version, actor_reference
        )

    async def cancel_receipt(self, receipt_id: UUID, expected_version: int,
                             actor_reference: str):
        return await self._repository.cancel_receipt(
            receipt_id, expected_version, actor_reference
        )

    async def cancel_receipt_item(self, receipt_id: UUID, receipt_item_id: UUID,
                                  expected_version: int, actor_reference: str):
        return await self._repository.cancel_receipt_item(
            receipt_id, receipt_item_id, expected_version, actor_reference
        )
